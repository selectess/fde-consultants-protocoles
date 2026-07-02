#!/usr/bin/env python3
"""Modex Collective — real multi-agent orchestration (the $260 tier).

Unlike ModexRuntime (one role per call), the Collective coordinates ALL FOUR
roles end-to-end with separation of powers and REAL concurrent dispatch:

    Lead        -> 6-Q decomposition + falsifiable claim + hypothesis tree
    Researchers -> N in parallel (thread pool), each falsifies ONE hypothesis
                   against the held-out promotion gate
    Builder     -> assembles/score the deliverable on the 6-trait rubric
    Certifier   -> INDEPENDENT FDE Assurance Score; may VETO the Lead's optimism

SELF-PROMPTING PROTOCOL (the autopoietic layer)
-----------------------------------------------
`run_autonomous()` adds a loop in which the Lead and the sub-agents *talk to and
prompt each other* through a shared Blackboard, driven by accumulated experience.
After every event/result/approach, the FIVE JUDGMENTS are applied:

    evidence  -> grounded in held-out / test / file:line proof?   (DeepSCR core)
    telos     -> does it advance the engagement goal (6-Q)?
    risk      -> reversible & within guardrails?  (the human-checkpoint trigger)
    coherence -> consistent with accumulated experience (memory)?
    value     -> shippable ROI worth the effort?

The judgment verdicts deterministically generate the NEXT prompt (self-prompting)
and route it to the agent best able to act on it — e.g. the Certifier's veto
prompts the owner of the weakest component to fix it, and the loop self-corrects.
This removes the human from the step-by-step loop while keeping them informed via
the Notifier (and gating ONLY genuinely irreversible / high-impact actions when
`human_in_loop=True`).

Shared state is written to fde-memory/ (context.json, episodes/, trust-score.json,
blackboard.jsonl, notifications.md) so any agent can resume the engagement.

Usage:
    from modex.collective import ModexCollective
    result = ModexCollective().run(problem_dict, golden_cases=None)            # single pass
    auto   = ModexCollective().run_autonomous(problem_dict)                    # self-prompting loop

    python3 -m modex.collective --problem problem.json [--autonomous]
"""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "skill" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scientific_search import FDECoordinator, FDEExecutor, default_golden_cases  # noqa: E402
from modex.orchestrator import ModexRuntime  # noqa: E402
from modex.specialists import (  # noqa: E402
    run_specialists, specialists_markdown, DEEPSCR_ROLES, FDE_SPECIALIST_ROLES)
from modex.arbiters import (  # noqa: E402
    FrozenContract, OracleRegistry, TrajectoryAuditor, make_verdict, ContractError)


# ============================================================================
# The Five Judgments — applied to every event / result / approach
# ============================================================================
FIVE_LENSES = ("evidence", "telos", "risk", "coherence", "value")

# verdict thresholds on a 0..1 score
_PASS = 0.8
_WEAK = 0.5

# pipeline + routing tables (module-level so the router is pure & testable)
NEXT_STAGE = {"lead": "researcher", "researcher": "builder", "builder": "certifier"}
DEFAULT_PROMPT = {
    "researcher": "Researcher: falsify the hypothesis tree against the held-out gate; promote only survivors.",
    "builder": "Builder: assemble the deliverable from the promoted architecture and score it on the 6-trait rubric.",
    "certifier": "Certifier: compute an INDEPENDENT FDE Assurance Score; veto shipping if the evidence is weak.",
}
# lower number = higher routing priority (risk is handled separately as a human checkpoint)
ROUTE_PRIORITY = {"evidence": 0, "telos": 1, "coherence": 2, "value": 3}
# which agent owns each FDE Assurance Score component (used by the Certifier's veto routing)
WEAKEST_OWNER = {"claim": "lead", "contradiction": "researcher", "evidence": "researcher", "antipatterns": "builder"}


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def _verdict(score: float) -> str:
    if score >= _PASS:
        return "pass"
    if score >= _WEAK:
        return "weak"
    return "fail"


@dataclass
class Judgment:
    """One of the five judgments applied to an event/result/approach."""
    lens: str                     # one of FIVE_LENSES
    score: float                  # 0.0 .. 1.0
    verdict: str                  # "pass" | "weak" | "fail"
    rationale: str
    next_prompt: Optional[str] = None   # the self-prompt emitted when not "pass"
    route_to: Optional[str] = None      # the agent role that should receive it

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---- per-lens scorers: (score, rationale) from the structured stage payload ----
def _j_evidence(stage: str, p: dict) -> tuple[float, str]:
    if stage == "scoping":
        d = p.get("decomposition", {})
        s = 1.0 if p.get("ready") else _clamp(d.get("overall_score", 0) / 100)
        return s, f"6-Q concreteness {d.get('overall_score', '?')}/100"
    if stage == "prototyping":
        if p.get("best"):
            return _clamp(p["best"].get("held_out_score", 0) / 100), \
                f"held-out {p['best'].get('held_out_score')}/100 on {p['best'].get('hypothesis_id')}"
        return (0.3 if p.get("hypotheses_count") else 0.0), "no hypothesis survived the held-out gate"
    if stage == "production":
        ok = p.get("evals", {}).get("verdict") == "PASS"
        return (1.0 if ok else 0.4), f"builder verdict={p.get('evals', {}).get('verdict')}"
    if stage == "certification":
        t = p.get("trust", {})
        return _clamp(t.get("trust_score", 0) / 100), f"trust={t.get('trust_score')} weakest={t.get('lowest_component')}"
    return 0.5, "n/a"


def _j_telos(stage: str, p: dict) -> tuple[float, str]:
    if stage == "scoping":
        return _clamp(p.get("decomposition", {}).get("overall_score", 0) / 100), "engagement framed toward the goal"
    if stage == "prototyping":
        return (1.0 if p.get("best") else 0.4), "forward progress = a promoted architecture"
    if stage == "production":
        return (1.0 if p.get("evals", {}).get("verdict") == "PASS" else 0.6), "deliverable assembled"
    if stage == "certification":
        v = p.get("trust", {}).get("verdict")
        return {"certified": 1.0, "needs_revision": 0.6, "rejected": 0.3}.get(v, 0.3), f"verdict={v}"
    return 0.5, "n/a"


def _j_risk(stage: str, p: dict) -> tuple[float, str]:
    # The irreversible / high-impact action in an FDE engagement is the SHIP /
    # production-handoff decision. Analysis stages are reversible.
    if stage == "certification":
        if p.get("shipped"):
            t = p.get("trust", {}).get("trust_score", 0)
            return (0.9 if t >= 85 else 0.2), "IRREVERSIBLE: ship / production-handoff decision"
        return 1.0, "no ship (held by the Certifier) — reversible"
    if stage == "production":
        return (0.9 if p.get("evals", {}).get("verdict") == "PASS" else 0.5), "building toward production"
    return 1.0, "analysis only — reversible"


def _j_coherence(_stage: str, _p: dict, m: dict) -> tuple[float, str]:
    if m.get("repeated_failure"):
        return 0.4, "looping: same weakest component twice — reconcile with accumulated lessons"
    return 1.0, "consistent with accumulated experience"


def _j_value(stage: str, p: dict) -> tuple[float, str]:
    if stage == "scoping":
        return _clamp(p.get("decomposition", {}).get("overall_score", 0) / 100), "value potential from scope"
    if stage == "prototyping":
        return (0.8 if p.get("best") else 0.3), "value depends on a viable architecture"
    if stage == "production":
        return (0.8 if p.get("evals", {}).get("verdict") == "PASS" else 0.4), "deliverable value"
    if stage == "certification":
        t = p.get("trust", {}).get("trust_score", 0)
        v = p.get("trust", {}).get("verdict")
        if v == "certified" and t >= 85:
            return 1.0, "shippable, high assurance"
        if t >= 60:
            return 0.7, "partial value, needs revision"
        return 0.4, "not shippable yet"
    return 0.5, "n/a"


def judge(event: dict, memory_signals: Optional[dict] = None) -> list[Judgment]:
    """Apply the five judgments to one event/result/approach.

    Returns one Judgment per lens; lenses that are not 'pass' carry a self-prompt
    and the agent role it should be routed to.
    """
    stage = event.get("stage", "")
    p = event.get("payload", {})
    m = memory_signals or {}
    specs = [
        ("evidence", _j_evidence(stage, p), "researcher",
         "Researcher: strengthen the evidence trail — widen the hypothesis tree / add held-out cases; promote only survivors."),
        ("telos", _j_telos(stage, p), "lead",
         "Lead: re-decompose — the 6-Q is too vague to progress toward the goal; sharpen Q1/Q2/Q6."),
        ("risk", _j_risk(stage, p), None,
         "HUMAN CHECKPOINT: a high-impact / irreversible action is on the table — informing the operator before proceeding."),
        ("coherence", _j_coherence(stage, p, m), "lead",
         "Lead: reconcile with accumulated lessons — this result contradicts prior experience or is looping."),
        ("value", _j_value(stage, p), "builder",
         "Builder: revise the deliverable — not shippable on the 6-trait rubric / assurance bar."),
    ]
    out: list[Judgment] = []
    for lens, (score, rationale), route, prompt in specs:
        v = _verdict(score)
        out.append(Judgment(
            lens=lens, score=round(score, 3), verdict=v, rationale=rationale,
            next_prompt=(prompt if v != "pass" else None),
            route_to=(route if v != "pass" else None),
        ))
    return out


def route_next(role: str, judgments: list[Judgment], ctx: dict, budgets: dict) -> Optional[tuple]:
    """Self-prompting router: decide who the next agent is and what to prompt it.

    Returns (next_role, prompt) or None when the engagement has converged
    (certified) or can make no further progress within the retry budgets.
    Pure & deterministic — `budgets` is mutated to guarantee termination.
    """
    # Agent-routable failures (risk routes to a human checkpoint, not an agent).
    fails = [j for j in judgments if j.verdict != "pass" and j.route_to in budgets]
    fails.sort(key=lambda j: ROUTE_PRIORITY.get(j.lens, 9))
    for j in fails:
        if budgets.get(j.route_to, 0) > 0:
            budgets[j.route_to] -= 1
            return (j.route_to, j.next_prompt)

    # No actionable failure with budget left → advance the pipeline or converge.
    if role == "certifier":
        if ctx.get("shipped"):
            return None  # converged: certified & shipped
        lowest = (ctx.get("trust") or {}).get("lowest_component")
        owner = WEAKEST_OWNER.get(lowest) if lowest else None
        if owner and budgets.get(owner, 0) > 0:
            budgets[owner] -= 1
            return (owner, f"Certifier veto (upward): raise '{lowest}' — {ctx.get('veto')}")
        return None  # stop: could not certify within budget
    nxt = NEXT_STAGE.get(role)
    return (nxt, DEFAULT_PROMPT[nxt]) if nxt else None


# ============================================================================
# Blackboard — the shared space where agents talk to & prompt each other
# ============================================================================
class Blackboard:
    """Append-only shared message log. Every agent posts its event + judgments +
    the self-prompt routed to the next agent, so the dialogue is auditable and
    later agents can read accumulated experience."""

    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.posts: list[dict[str, Any]] = []

    def post(self, sender: str, event: dict, judgments: list[Judgment], self_prompt: Optional[str]) -> dict:
        trust = event.get("payload", {}).get("trust", {}) if event.get("stage") == "certification" else {}
        entry = {
            "i": len(self.posts),
            "sender": sender,
            "kind": event.get("stage"),
            "summary": event.get("summary", ""),
            "judgments": {j.lens: j.verdict for j in judgments},
            "self_prompt": self_prompt,
            "lowest_component": trust.get("lowest_component"),
            "not_certified": bool(event.get("stage") == "certification" and not event.get("payload", {}).get("shipped")),
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self.posts.append(entry)
        self._persist(entry)
        return entry

    def memory_signals(self) -> dict[str, Any]:
        """Accumulated-experience signals derived from the conversation so far."""
        certs = [p for p in self.posts if p["kind"] == "certification"]
        lows = [p.get("lowest_component") for p in certs]
        repeated = len(lows) >= 2 and lows[-1] is not None and lows[-1] == lows[-2]
        return {
            "prior_events": len(self.posts),
            "prior_certifications": len(certs),
            "prior_veto": any(p.get("not_certified") for p in certs),
            "repeated_failure": repeated,
        }

    def _persist(self, entry: dict) -> None:
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            with (self.memory_dir / "blackboard.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            print(f"[collective] blackboard write skipped: {e}", file=sys.stderr)


# ============================================================================
# Notifier — human OUT of the loop, but kept informed
# ============================================================================
class Notifier:
    """Streams what the swarm is doing to the operator. The loop runs without
    human input by default; a checkpoint is recorded for high-impact / irreversible
    actions and only *gates* the loop when `human_in_loop=True`."""

    def __init__(self, memory_dir: Path, human_in_loop: bool = False):
        self.memory_dir = Path(memory_dir)
        self.human_in_loop = human_in_loop
        self.feed: list[dict[str, Any]] = []

    def notify(self, level: str, message: str) -> dict:
        n = {"level": level, "message": message, "at": datetime.now(timezone.utc).isoformat()}
        self.feed.append(n)
        print(f"[collective:{level}] {message}", file=sys.stderr)
        self._persist(n)
        return n

    def checkpoint(self, reason: str) -> bool:
        """Record a human checkpoint. Returns True iff the loop must halt for an ack."""
        self.notify("checkpoint", f"HUMAN CHECKPOINT (informed): {reason}")
        return self.human_in_loop

    def _persist(self, n: dict) -> None:
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            with (self.memory_dir / "notifications.md").open("a", encoding="utf-8") as f:
                f.write(f"- `{n['at']}` **{n['level']}** — {n['message']}\n")
        except OSError as e:
            print(f"[collective] notification write skipped: {e}", file=sys.stderr)


@dataclass
class CollectiveResult:
    """Consolidated result of a full Collective engagement (single pass)."""
    schema: str
    claim: str
    decomposition: dict[str, Any]
    research: list[dict[str, Any]]
    promoted_hypothesis: Optional[dict[str, Any]]
    evals: dict[str, Any]
    trust_score: dict[str, Any]
    shipped: bool
    veto: Optional[str]
    roles: dict[str, str]
    executed_at: str
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AutonomousResult:
    """Result of a self-prompting (autonomous) engagement."""
    schema: str
    status: str                  # certified | stopped_unresolved | max_iterations_reached | awaiting_human_ack
    shipped: bool
    iterations: int
    claim: str
    trust_score: dict[str, Any]
    veto: Optional[str]
    transcript: list[dict[str, Any]]     # the inter-agent dialogue (who prompted whom, and why)
    blackboard: list[dict[str, Any]]
    notifications: list[dict[str, Any]]
    five_lenses: tuple = FIVE_LENSES
    roles: Optional[dict] = None          # the 8-agent roster (4 DeepSCR + 4 FDE specialists)
    executed_at: str = ""
    duration_seconds: float = 0.0
    contract_report: Optional[dict] = None  # Frozen-Arbiters audit (when a Contract governs the run)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModexCollective:
    """Coordinates the 4 FDE roles with separation of powers + parallel research,
    plus an optional self-prompting autonomous loop."""

    def __init__(self, memory_dir: Optional[Path] = None, max_workers: int = 4):
        self.memory_dir = Path(memory_dir) if memory_dir else Path("./fde-memory")
        self.max_workers = max_workers

    # ---- Researcher worker (runs in a thread) -----------------------------
    @staticmethod
    def _research_one(hypothesis, problem: dict, golden_cases: list) -> dict[str, Any]:
        """One researcher falsifies one hypothesis on the held-out gate."""
        result = FDEExecutor(hypothesis).evaluate(problem, golden_cases)
        result["researcher"] = hypothesis.hypothesis_id
        return result

    # ---- Stage actions (shared by single-pass run() and run_autonomous()) --
    def _act_lead(self, ctx: dict) -> dict:
        problem = ctx["problem"]
        lead = ModexRuntime(role="lead", memory_dir=self.memory_dir).run({"problem_json": json.dumps(problem)})
        decomposition = lead.output.get("decomposition", {})
        claim = lead.output.get("claim", "") or f"Decomposition of {problem.get('q1_process', 'unknown')[:50]}"
        ctx["decomposition"] = decomposition
        ctx["claim"] = claim
        summary = f"concreteness={decomposition.get('overall_score', 'n/a')}"
        ctx["episodes"].append(self._episode("scoping", "lead", "6-Q decomposition + claim", summary, claim))
        return {"stage": "scoping", "role": "lead", "summary": summary,
                "payload": {"decomposition": decomposition, "claim": claim, "ready": lead.output.get("ready", False)}}

    def _act_researcher(self, ctx: dict) -> dict:
        problem = ctx["problem"]
        golden = ctx.get("golden")
        if golden is None:
            golden = default_golden_cases(problem)
        if isinstance(golden, dict):
            golden = golden.get("cases", [])
        coordinator = FDECoordinator(problem, golden, self.memory_dir / "lessons.json")
        hypotheses = coordinator.generate_hypothesis_tree()
        research: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(self._research_one, h, problem, golden) for h in hypotheses]
            for fut in as_completed(futures):
                research.append(fut.result())
        research.sort(key=lambda r: r["hypothesis_id"])
        promoted = [r for r in research if r["promoted"]]
        best = max(promoted, key=lambda r: (r["held_out_score"], r["development_score"]), default=None)
        failure_modes = [r for r in research if not r["promoted"]]
        ctx["research"] = research
        ctx["best"] = best
        ctx["failure_modes"] = failure_modes
        ctx["hypotheses_count"] = len(hypotheses)
        summary = (f"promoted {best['hypothesis_id']} (held_out={best['held_out_score']})" if best else "none promoted")
        ctx["episodes"].append(self._episode(
            "prototyping", "researcher",
            f"{len(hypotheses)} hypotheses tested in parallel ({self.max_workers} workers)", summary, ctx.get("claim", "")))
        return {"stage": "prototyping", "role": "researcher", "summary": summary,
                "payload": {"hypotheses_count": len(hypotheses), "promoted_count": len(promoted),
                            "best": best, "failure_modes_count": len(failure_modes)}}

    def _act_builder(self, ctx: dict) -> dict:
        # The DeepSCR Builder consults the 4 FDE domain specialists (in parallel)
        # and assembles their analysis into the deliverable it then scores.
        specialists = ctx.get("specialists") or run_specialists(ctx["problem"], self.max_workers)
        ctx["specialists"] = specialists
        deliverable = ctx.get("deliverable_markdown") or self._draft_deliverable(
            ctx["problem"], ctx.get("claim", ""), ctx.get("best"), ctx.get("failure_modes", []), specialists)
        builder = ModexRuntime(role="builder", memory_dir=self.memory_dir).run({"deliverable_markdown": deliverable})
        evals = builder.output.get("evals", {})
        ctx["evals"] = evals
        summary = f"verdict={evals.get('verdict', 'n/a')} (+{len(specialists)} FDE specialists)"
        ctx["episodes"].append(self._episode("production", "builder",
                               "deliverable assembled from 4 FDE specialists + scored", summary, ctx.get("claim", "")))
        return {"stage": "production", "role": "builder", "summary": summary,
                "payload": {"evals": evals, "specialists": [s.role for s in specialists]}}

    def _act_certifier(self, ctx: dict) -> dict:
        claim = ctx.get("claim", "")
        failure_modes = ctx.get("failure_modes", [])
        evals = ctx.get("evals", {})
        # Ground-truth evidence: the engagement must cite REAL artifacts (file:line);
        # the Certifier verifies them against disk. Synthetic structure no longer buys
        # the evidence component (fixes the "certify form, not truth" flaw).
        evidence_trail = ctx["problem"].get("evidence_trail", [])
        evidence = {
            "claim_present": bool(claim),
            "has_3_failure_modes": len(failure_modes) >= 3,
            "evidence_trail": evidence_trail,
            "antipatterns_clean": (evals.get("verdict") == "PASS"),
            "claim_text": claim,
        }
        certifier = ModexRuntime(role="certifier", memory_dir=self.memory_dir).run(evidence)
        trust = certifier.output.get("trust_score", {})
        verdict = trust.get("verdict", "rejected")
        shipped = verdict == "certified"
        veto = None if shipped else (
            f"Certifier blocked shipping (verdict={verdict}, "
            f"weakest={trust.get('lowest_component')}, score={trust.get('trust_score')})")
        ctx["trust"] = trust
        ctx["verdict"] = verdict
        ctx["shipped"] = shipped
        ctx["veto"] = veto
        summary = f"trust={trust.get('trust_score')} verdict={verdict} shipped={shipped}"
        ctx["episodes"].append(self._episode("certification", "certifier",
                               f"independent FDE Assurance Score = {trust.get('trust_score')}", summary, claim))
        return {"stage": "certification", "role": "certifier", "summary": summary,
                "payload": {"trust": trust, "shipped": shipped}}

    def _dispatch(self) -> dict:
        return {"lead": self._act_lead, "researcher": self._act_researcher,
                "builder": self._act_builder, "certifier": self._act_certifier}

    # ---- Single-pass engagement (original behaviour, preserved) -----------
    def run(
        self,
        problem: dict[str, Any],
        golden_cases: Optional[list] = None,
        deliverable_markdown: Optional[str] = None,
    ) -> CollectiveResult:
        start = datetime.now(timezone.utc)
        ctx: dict[str, Any] = {"problem": problem, "golden": golden_cases,
                               "deliverable_markdown": deliverable_markdown, "episodes": []}
        self._act_lead(ctx)
        self._act_researcher(ctx)
        self._act_builder(ctx)
        self._act_certifier(ctx)
        end = datetime.now(timezone.utc)
        result = self._result_from_ctx(ctx, start, end)
        self._write_memory(result, ctx["episodes"])
        return result

    # ---- Autonomous engagement (the self-prompting protocol) --------------
    def run_autonomous(
        self,
        problem: dict[str, Any],
        golden_cases: Optional[list] = None,
        deliverable_markdown: Optional[str] = None,
        max_iterations: int = 10,
        retries_per_agent: int = 2,
        human_in_loop: bool = False,
        contract: Optional[FrozenContract] = None,
        oracles: Optional[OracleRegistry] = None,
    ) -> AutonomousResult:
        """Run the engagement as a self-prompting loop. The Lead and sub-agents
        prompt each other based on the five judgments until the Certifier
        certifies, the retry budgets are exhausted, or `max_iterations` is hit.
        The human is informed throughout and only gates irreversible actions when
        `human_in_loop=True`.

        FROZEN ARBITERS (optional): when a sealed `contract` governs the run,
        every action must serve a Contract clause (or is mechanically rejected),
        the frozen `oracles` override the Certifier's optimism at ship time, and
        the result carries a `contract_report` (clause drift distribution,
        cited verdicts, oracle ledger, thrashing/plateau audit)."""
        if contract is not None and not contract.sealed:
            raise ContractError("the Contract must be sealed (frozen) before launch")
        if contract is not None and "iterations" in contract.budgets:
            max_iterations = min(max_iterations, contract.budgets["iterations"])
        rejected_actions: list[dict] = []
        clause_tags: list[str] = []
        cited_verdicts: list[dict] = []
        trust_history: list[float] = []
        role_seq: list[str] = []
        start = datetime.now(timezone.utc)
        ctx: dict[str, Any] = {"problem": problem, "golden": golden_cases,
                               "deliverable_markdown": deliverable_markdown, "episodes": []}
        bb = Blackboard(self.memory_dir)
        notifier = Notifier(self.memory_dir, human_in_loop=human_in_loop)
        budgets = {r: retries_per_agent for r in ("lead", "researcher", "builder", "certifier")}
        dispatch = self._dispatch()
        transcript: list[dict[str, Any]] = []
        current: Optional[tuple] = ("lead", "Goal → Lead: decompose the engagement (6-Q) and state a falsifiable claim.")
        status = "max_iterations_reached"
        iteration = 0

        for iteration in range(1, max_iterations + 1):
            role, prompt = current
            role_seq.append(role)
            notifier.notify("step", f"iter {iteration}: {role} ⟵ {prompt}")
            event = dispatch[role](ctx)

            # ---- Frozen Arbiters: the agent pleads, it never grades itself ----
            if contract is not None:
                clause = contract.clause_for(event["stage"])
                if clause is None:
                    # An action serving no Contract clause is mechanically rejected.
                    rejected_actions.append({"iteration": iteration, "role": role, "stage": event["stage"]})
                    notifier.notify("contract", f"REJECTED: stage '{event['stage']}' serves no Contract clause")
                    if budgets.get("lead", 0) > 0:
                        budgets["lead"] -= 1
                        current = ("lead", "Lead: the last action served no Contract clause — re-frame within the Contract.")
                        continue
                    status = "contract_violation"
                    break
                clause_tags.append(clause)
                event["clause"] = clause
                if event["stage"] == "certification":
                    # The frozen oracles override the Certifier's optimism at ship time,
                    # and the verdict must cite a run id — an uncited verdict is null.
                    runs = oracles.run_all(ctx) if oracles is not None else []
                    failed = [r for r in runs if not r.passed]
                    if failed:
                        ctx["shipped"] = False
                        ctx["veto"] = (f"frozen oracle '{failed[0].oracle}' failed "
                                       f"({failed[0].run_id}): {failed[0].detail}")
                        event["payload"]["shipped"] = False
                    cited_verdicts.append(make_verdict(
                        claim=ctx.get("claim", ""),
                        decision="pass" if (ctx.get("shipped") and not failed) else "fail",
                        cites_run=(runs[0].run_id if runs else None),
                        cites_clause=clause,
                    ).to_dict())
                    trust_history.append(float((ctx.get("trust") or {}).get("trust_score", 0)))
                if TrajectoryAuditor.detect_thrashing(role_seq):
                    notifier.notify("audit", "THRASHING: A→B→A routing oscillation detected")

            judgments = judge(event, bb.memory_signals())
            nxt = route_next(role, judgments, ctx, budgets)
            self_prompt = nxt[1] if nxt else None
            bb.post(role, event, judgments, self_prompt)

            notifier.notify("judgment", f"{role}: " + ", ".join(f"{j.lens}={j.verdict}" for j in judgments))
            transcript.append({
                "iteration": iteration, "from": role, "summary": event["summary"],
                "judgments": {j.lens: j.verdict for j in judgments},
                "to": (nxt[0] if nxt else None), "self_prompt": self_prompt,
            })

            # Human checkpoint on irreversible / high-impact action (informed; gates only if human_in_loop).
            irreversible = bool(event["stage"] == "certification" and event["payload"].get("shipped"))
            risk = next((j for j in judgments if j.lens == "risk"), None)
            if irreversible or (risk and risk.verdict != "pass"):
                if notifier.checkpoint(risk.rationale if risk else "irreversible action"):
                    status = "awaiting_human_ack"
                    break

            if nxt is None:
                status = "certified" if ctx.get("shipped") else "stopped_unresolved"
                break
            current = nxt

        end = datetime.now(timezone.utc)
        contract_report = None
        if contract is not None:
            distribution = ({c: round(clause_tags.count(c) / len(clause_tags), 3)
                             for c in sorted(set(clause_tags))} if clause_tags else {})
            contract_report = {
                "contract_hash": contract.hash,
                "integrity": contract.verify_integrity(),      # tamper-evident, machine-checked
                "clause_distribution": distribution,           # drift is measured, not felt
                "rejected_actions": rejected_actions,
                "verdicts": cited_verdicts,                    # every one cites a run id + clause
                "oracle_ledger": ([r.to_dict() for r in oracles.ledger]
                                  if oracles is not None else []),
                "thrashing": TrajectoryAuditor.detect_thrashing(role_seq),
                "plateau": TrajectoryAuditor.detect_plateau(trust_history),
            }
        # Persist the single-pass-style memory snapshot + the autonomous transcript.
        self._write_memory(self._result_from_ctx(ctx, start, end), ctx["episodes"])
        self._write_transcript(transcript)
        notifier.notify("done", f"status={status}; shipped={ctx.get('shipped', False)}; iterations={iteration}")
        return AutonomousResult(
            schema="fde-modex-collective-autonomous-v1",
            status=status,
            shipped=bool(ctx.get("shipped", False)),
            iterations=iteration,
            claim=ctx.get("claim", ""),
            trust_score=ctx.get("trust", {}),
            veto=ctx.get("veto"),
            transcript=transcript,
            blackboard=bb.posts,
            notifications=notifier.feed,
            roles={"deepscr": list(DEEPSCR_ROLES), "fde_specialists": list(FDE_SPECIALIST_ROLES)},
            executed_at=start.isoformat(),
            duration_seconds=(end - start).total_seconds(),
            contract_report=contract_report,
        )

    def _result_from_ctx(self, ctx: dict, start: datetime, end: datetime) -> CollectiveResult:
        return CollectiveResult(
            schema="fde-modex-collective-result-v1",
            claim=ctx.get("claim", ""),
            decomposition=ctx.get("decomposition", {}),
            research=ctx.get("research", []),
            promoted_hypothesis=ctx.get("best"),
            evals=ctx.get("evals", {}),
            trust_score=ctx.get("trust", {}),
            shipped=bool(ctx.get("shipped", False)),
            veto=ctx.get("veto"),
            roles={"lead": "DeepSCR", "researcher": f"DeepSCR x{ctx.get('hypotheses_count', 0)} parallel",
                   "builder": "DeepSCR", "certifier": "DeepSCR (independent veto)",
                   "scoping": "FDE specialist", "architecture": "FDE specialist",
                   "agent": "FDE specialist", "production": "FDE specialist"},
            executed_at=start.isoformat(),
            duration_seconds=(end - start).total_seconds(),
        )

    # ---- Deliverable drafting --------------------------------------------
    @staticmethod
    def _draft_deliverable(problem, claim, best, failure_modes, specialists=None) -> str:
        """Evidence-backed deliverable for the Builder to score.

        Surfaces the real 6-Q fields and includes the artifacts the 6-trait rubric
        rewards (quantified ownership, code/runbook, stakeholder/change-management,
        exec summary + architecture) so a well-scoped engagement can actually pass.
        """
        g = problem.get
        promoted = (f"{best['hypothesis_id']} — {best['description']} "
                    f"(held-out {best['held_out_score']}/100, dev {best['development_score']}/100)"
                    if best else "No hypothesis survived the held-out gate.")
        lessons = "\n".join(f"- {r['hypothesis_id']}: {r.get('lesson', 'pruned')}" for r in failure_modes) or "- none"
        body = f"""# FDE Deliverable — Prototype Spec

## Executive Summary
{claim}. This SaaS / B2B engagement targets the process **{g('q1_process', 'n/a')}**
(volume {g('q1_volume', 'n/a')}, owner {g('q1_owner', 'the process owner')}). Compliance
context: {g('q3_compliance', 'none stated')}. Target: >200% ROI within 90 days, go-live by week 7.

## 6-Q Decomposition (evidence-grounded)
- **Q1 process**: {g('q1_process', 'n/a')} — volume {g('q1_volume', 'n/a')}
- **Q2 decision**: {g('q2_decision_type', 'classification')} — latency {g('q2_latency', '<1s')}, accuracy {g('q2_accuracy_target', 'n/a')}
- **Q3 data**: {g('q3_volume', 'n/a')} — quality {g('q3_quality', 'n/a')}, compliance {g('q3_compliance', 'n/a')}
- **Q4 cost of error**: {g('q4_direct_cost', 'n/a')} — regulatory {g('q4_regulatory', 'n/a')}
- **Q5 current baseline**: {g('q5_current_type', 'manual')} at {g('q5_current_performance', 'n/a')}
- **Q6 success metric / ROI**: {g('q6_primary_metric', 'n/a')} — threshold {g('q6_threshold', '>200% ROI')}

## Recommended Architecture (promoted hypothesis)
{promoted}

```python
# Reference implementation skeleton (runbook + deployment config ready)
def serve(request):
    # deployment: containerized; config via env vars; RBAC enforced for compliance
    return model.predict(request)  # latency target: {g('q2_latency', '<1s')}
```

## Rejected Hypotheses (held-out evidence preserved)
{lessons}

## Stakeholders & Change Management
Stakeholder {g('q1_owner', 'the owner')} sponsors adoption; team training plus a
2-week ramp (week 1 shadow, week 2 cutover) drives adoption. Production go-live by week 7.

## FDE Assurance Score & Assurance
Submitted to the independent Certifier; every claim above is backed by held-out
validation scores from the Researcher stage. ROI threshold {g('q6_threshold', '>200% ROI')}
measured by {g('q6_measurement', 'monthly cohort analysis')}.
"""
        if specialists:
            body += ("\n\n## FDE Specialist Analysis (consulted by the Builder)\n\n"
                     + specialists_markdown(specialists))
        return body

    # ---- Shared memory ----------------------------------------------------
    def _episode(self, stage, role, what, outcome, claim) -> dict[str, Any]:
        return {"stage": stage, "role": role, "what": what, "outcome": outcome, "claim": claim,
                "at": datetime.now(timezone.utc).isoformat()}

    def _write_transcript(self, transcript: list[dict[str, Any]]) -> None:
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "autonomous-transcript.json").write_text(
                json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError as e:
            print(f"[collective] transcript write skipped: {e}", file=sys.stderr)

    def _write_memory(self, result: CollectiveResult, episodes: list[dict[str, Any]]) -> None:
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "episodes").mkdir(exist_ok=True)
            (self.memory_dir / "context.json").write_text(json.dumps({
                "schema": "fde-memory-context-v1",
                "stage": "certification",
                "claim": result.claim,
                "six_q": result.decomposition,
                "promoted_hypothesis": result.promoted_hypothesis,
                "shipped": result.shipped,
                "veto": result.veto,
                "updated_at": result.executed_at,
            }, indent=2), encoding="utf-8")
            # Compute a real, reproducible certificate SHA-256 and a last_verdict
            # block so `bash modex/verify.sh <project>` can verify the engagement.
            ts_doc = dict(result.trust_score) if result.trust_score else {}
            score = ts_doc.get("trust_score")
            if score is not None:
                cert_canonical = json.dumps({
                    "claim": result.claim,
                    "trust_score": score,
                    "verdict": ts_doc.get("verdict"),
                    "promoted_hypothesis": result.promoted_hypothesis,
                    "certified_at": result.executed_at,
                }, sort_keys=True).encode("utf-8")
                ts_doc["last_verdict"] = {
                    "score": score,
                    "sha256": hashlib.sha256(cert_canonical).hexdigest(),
                    "verdict": ts_doc.get("verdict"),
                    "certified_at": result.executed_at,
                }
            (self.memory_dir / "trust-score.json").write_text(
                json.dumps(ts_doc, indent=2), encoding="utf-8")
            for i, ep in enumerate(episodes):
                fname = f"{ep['at'].replace(':', '').replace('.', '')}-{i}-{ep['role']}.md"
                (self.memory_dir / "episodes" / fname).write_text(
                    f"# Episode: {ep['what']}\n"
                    f"**Stage**: {ep['stage']}\n**Agent role**: {ep['role']}\n"
                    f"## Claim\n{ep['claim']}\n## Outcome\n{ep['outcome']}\n",
                    encoding="utf-8")
        except OSError as e:
            print(f"[collective] memory write skipped: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Modex Collective — full FDE loop, 4 roles + self-prompting")
    parser.add_argument("--problem", required=True, help="Path to 6-Q problem JSON")
    parser.add_argument("--golden", default=None, help="Optional held-out cases JSON")
    parser.add_argument("--deliverable", default=None, help="Optional deliverable markdown to score")
    parser.add_argument("--memory-dir", default="./fde-memory")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--autonomous", action="store_true", help="Run the self-prompting loop")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--retries-per-agent", type=int, default=2)
    parser.add_argument("--human-in-loop", action="store_true",
                        help="Halt for an ack at irreversible-action checkpoints (default: informed but not gated)")
    args = parser.parse_args()

    problem = json.loads(Path(args.problem).read_text())
    golden = json.loads(Path(args.golden).read_text()) if args.golden else None
    deliverable = Path(args.deliverable).read_text() if args.deliverable else None

    collective = ModexCollective(memory_dir=args.memory_dir, max_workers=args.workers)
    if args.autonomous:
        auto = collective.run_autonomous(
            problem, golden_cases=golden, deliverable_markdown=deliverable,
            max_iterations=args.max_iterations, retries_per_agent=args.retries_per_agent,
            human_in_loop=args.human_in_loop)
        print(json.dumps(auto.to_dict(), indent=2, default=str))
        return 0 if auto.shipped else 2
    result = collective.run(problem, golden_cases=golden, deliverable_markdown=deliverable)
    print(json.dumps(result.to_dict(), indent=2, default=str))
    return 0 if result.shipped else 2


if __name__ == "__main__":
    sys.exit(main())
