#!/usr/bin/env python3
"""The Frozen Arbiters — external judges the agent cannot modify.

In full autonomy the human is NOT replaced by the agent's confidence in
itself (the AutoGPT failure mode) but by three arbiters, frozen before
launch, that the agent can plead to but never edit:

    Contract  -> written once at t0, sealed (SHA-256), append-only amendments.
                 Goal, numbered clauses, metric thresholds, budgets, NON-goals.
                 Every action must carry the clause it serves; an action
                 without a clause is mechanically rejected, so drift becomes
                 a measurable distribution instead of a feeling.
    Oracles   -> executable checks registered then FROZEN; the agent cannot
                 edit its own graders. An oracle is only trusted after
                 mutation testing (it must catch deliberately injected bugs).
    Verdicts  -> a verdict must cite an oracle run id or a contract clause;
                 a verdict citing nothing is NULL. "Tests pass" does not
                 exist — only "run #0007: 34/34" exists.

Plus the two guards that keep long autonomy honest:

    TrajectoryAuditor -> mechanical detection of thrashing (A→B→A routing)
                         and plateau (N cycles without metric gain).
    DistillationGate  -> only oracle-validated trajectories may become
                         lessons, and a lesson enters the policy only after
                         passing on FRESH cases it has never seen.

Consumed by `modex.collective.ModexCollective.run_autonomous(contract=…,
oracles=…)`; fully standalone and deterministic (no LLM, no network).
"""
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Optional


class ContractError(Exception):
    """Raised on invalid Contract usage (unsealed, unknown clause…)."""


class FrozenError(ContractError):
    """Raised when the agent tries to modify a frozen arbiter."""


def _canonical_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# ============================================================================
# Arbiter 1 — the Contract (sealed at t0, tamper-evident)
# ============================================================================
class FrozenContract:
    """The alignment anchor. Sealed once; mutation is blocked AND tamper-evident.

    `stage_clauses` maps each pipeline stage (scoping/prototyping/production/
    certification) to the clause id it serves — the mechanical link that lets
    the loop reject any action not covered by the Contract.
    """

    def __init__(
        self,
        goal: str,
        clauses: dict[str, str],
        metrics: dict[str, dict],
        budgets: dict[str, int],
        non_goals: list[str],
        stage_clauses: dict[str, str],
    ):
        for stage, cid in stage_clauses.items():
            if cid not in clauses:
                raise ContractError(f"stage '{stage}' maps to unknown clause '{cid}'")
        self.goal = goal
        self.clauses = dict(clauses)
        self.metrics = {k: dict(v) for k, v in metrics.items()}
        self.budgets = dict(budgets)
        self.non_goals = list(non_goals)
        self.stage_clauses = dict(stage_clauses)
        self.amendments: list[dict] = []          # append-only, never edits clauses
        self._sealed = False
        self._hash: Optional[str] = None

    # -- sealing & integrity -------------------------------------------------
    def _payload(self) -> dict:
        return {"goal": self.goal, "clauses": self.clauses, "metrics": self.metrics,
                "budgets": self.budgets, "non_goals": self.non_goals,
                "stage_clauses": self.stage_clauses}

    def seal(self) -> str:
        if self._sealed:
            raise FrozenError("Contract is already sealed")
        self._hash = _canonical_hash(self._payload())
        self._sealed = True
        return self._hash

    @property
    def sealed(self) -> bool:
        return self._sealed

    @property
    def hash(self) -> Optional[str]:
        return self._hash

    def verify_integrity(self) -> bool:
        """Machine-verifiable: recompute the canonical hash against the seal."""
        return self._sealed and _canonical_hash(self._payload()) == self._hash

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_sealed", False) and not name.startswith("_") and name != "amendments":
            raise FrozenError(f"Contract is sealed — cannot modify '{name}'")
        super().__setattr__(name, value)

    def append_amendment(self, text: str) -> dict:
        """Append-only: an ambiguity discovered in flight is logged, never edited in."""
        prev = self.amendments[-1]["link"] if self.amendments else self._hash
        entry = {"text": text, "at": datetime.now(timezone.utc).isoformat(),
                 "link": _canonical_hash({"prev": prev, "text": text})}
        self.amendments.append(entry)
        return entry

    # -- what the loop consumes ----------------------------------------------
    def clause_for(self, stage: str) -> Optional[str]:
        return self.stage_clauses.get(stage)

    def victory(self, measured: dict[str, float]) -> bool:
        """The threshold is a CEILING, not a floor: all metrics at threshold = done."""
        return all(measured.get(name, float("-inf")) >= spec.get("threshold", float("inf"))
                   for name, spec in self.metrics.items())


# ============================================================================
# Arbiter 2 — the Oracles (frozen graders + mutation-tested trust)
# ============================================================================
@dataclass
class OracleRun:
    """One execution of one oracle — the only citable unit of proof."""
    run_id: str
    oracle: str
    passed: bool
    score: float
    detail: str
    at: str

    def to_dict(self) -> dict:
        return asdict(self)


class OracleRegistry:
    """Executable checks the agent can invoke but never edit once frozen."""

    def __init__(self):
        self._oracles: dict[str, Callable[[Any], tuple[bool, float, str]]] = {}
        self._frozen = False
        self._ledger: list[OracleRun] = []       # append-only
        self.proven: dict[str, bool] = {}        # mutation-testing outcome

    def register(self, name: str, fn: Callable[[Any], tuple[bool, float, str]]) -> None:
        if self._frozen:
            raise FrozenError("OracleRegistry is frozen — the agent cannot edit its graders")
        self._oracles[name] = fn

    def freeze(self) -> None:
        self._frozen = True

    @property
    def frozen(self) -> bool:
        return self._frozen

    def prove(self, name: str, known_bad: list[Any]) -> bool:
        """Mutation testing: the oracle earns trust only by CATCHING injected bugs."""
        fn = self._oracles[name]
        caught_all = all(not fn(mutant)[0] for mutant in known_bad)
        self.proven[name] = caught_all
        return caught_all

    def run(self, name: str, subject: Any) -> OracleRun:
        if name not in self._oracles:
            raise ContractError(f"unknown oracle '{name}'")
        passed, score, detail = self._oracles[name](subject)
        seq = len(self._ledger) + 1
        rec = OracleRun(
            run_id=f"run#{seq:04d}-{_canonical_hash({'n': name, 's': seq, 'd': detail})[:8]}",
            oracle=name, passed=bool(passed), score=float(score), detail=str(detail),
            at=datetime.now(timezone.utc).isoformat(),
        )
        self._ledger.append(rec)
        return rec

    def run_all(self, subject: Any) -> list[OracleRun]:
        return [self.run(name, subject) for name in self._oracles]

    @property
    def ledger(self) -> tuple[OracleRun, ...]:
        return tuple(self._ledger)                # read-only view — append via run() only

    def passing_ids(self) -> set[str]:
        return {r.run_id for r in self._ledger if r.passed}


# ============================================================================
# Arbiter 3 — the Verdict grammar (no citation = null verdict)
# ============================================================================
@dataclass
class Verdict:
    """claim / proof / decision — a verdict citing nothing is NULL."""
    claim: str
    decision: str                     # "pass" | "fail" | "null"
    cites_run: Optional[str] = None
    cites_clause: Optional[str] = None

    @property
    def valid(self) -> bool:
        return self.decision != "null" and bool(self.cites_run or self.cites_clause)

    def to_dict(self) -> dict:
        return {**asdict(self), "valid": self.valid}


def make_verdict(claim: str, decision: str,
                 cites_run: Optional[str] = None,
                 cites_clause: Optional[str] = None) -> Verdict:
    """The Registrar-Arbiter's only pen: uncited decisions are nulled, not trusted."""
    if not (cites_run or cites_clause):
        return Verdict(claim=claim, decision="null")
    return Verdict(claim=claim, decision=decision, cites_run=cites_run, cites_clause=cites_clause)


# ============================================================================
# Trajectory audit — mechanical, not vibes
# ============================================================================
class TrajectoryAuditor:
    """Macro-verification over the registry: convergence, thrashing, plateau."""

    @staticmethod
    def detect_thrashing(roles: list[str], window: int = 4) -> bool:
        """A→B→A→B routing oscillation in the last `window` steps."""
        tail = roles[-window:]
        return len(tail) >= 4 and tail[0] == tail[2] and tail[1] == tail[3] and tail[0] != tail[1]

    @staticmethod
    def detect_plateau(metric_history: list[float], window: int = 3) -> bool:
        """`window` consecutive cycles without metric gain → force a strategy-CLASS change."""
        if len(metric_history) < window + 1:
            return False
        base = metric_history[-(window + 1)]
        return all(m <= base for m in metric_history[-window:])

    @staticmethod
    def tokens_per_point(tokens_spent: float, metric_gain: float) -> Optional[float]:
        """Governance ratio: cost per metric point gained; exploding ratio = stop signal."""
        if metric_gain <= 0:
            return None
        return round(tokens_spent / metric_gain, 2)


# ============================================================================
# Distillation gate — self-training without collapse
# ============================================================================
class DistillationGate:
    """Only oracle-validated trajectories become lessons; lessons pass their own CI."""

    def __init__(self, oracles: OracleRegistry):
        self._oracles = oracles
        self.lessons: list[dict] = []             # candidate lessons (not yet policy)
        self.policy: list[dict] = []              # admitted lessons only

    def distill(self, trajectory: list[dict]) -> Optional[dict]:
        """A trajectory is distillable only if EVERY step cites a passing oracle run."""
        passing = self._oracles.passing_ids()
        if not trajectory or not all(step.get("cites_run") in passing for step in trajectory):
            return None                            # echo-chamber input refused
        lesson = {"rule": f"validated trajectory of {len(trajectory)} steps",
                  "steps": [s["cites_run"] for s in trajectory],
                  "at": datetime.now(timezone.utc).isoformat()}
        self.lessons.append(lesson)
        return lesson

    def admit(self, lesson: dict, fresh_cases: list[Any], oracle_name: str) -> bool:
        """A lesson enters the policy only after passing on cases it has never seen."""
        if lesson not in self.lessons:
            return False
        runs = [self._oracles.run(oracle_name, case) for case in fresh_cases]
        if runs and all(r.passed for r in runs):
            self.policy.append({**lesson, "admitted_on": [r.run_id for r in runs]})
            return True
        return False
