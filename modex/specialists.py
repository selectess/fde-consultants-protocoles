#!/usr/bin/env python3
"""The 4 FDE domain specialists — the domain layer the DeepSCR roles GOVERN.

Architecture (the 8-agent Collective):
    DeepSCR roles  (Lead · Researcher · Builder · Certifier) = separation of powers,
                    domain-agnostic governance (propose / contradict / verify / certify).
    FDE specialists (Scoping · Architecture · Agent · Production) = domain depth.

The DeepSCR **Builder** consults the specialists to assemble the deliverable; the
**Certifier** verifies their claims. So it is "DeepSCR governing FDE specialists",
not "FDE applying DeepSCR". Each specialist maps to a skill reference and produces
grounded, deterministic domain guidance from the 6-Q problem (no hallucination).
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from typing import Any

DEEPSCR_ROLES = ("lead", "researcher", "builder", "certifier")
FDE_SPECIALIST_ROLES = ("scoping", "architecture", "agent", "production")
ALL_AGENTS = DEEPSCR_ROLES + FDE_SPECIALIST_ROLES  # the 8


def _vague(v: str) -> bool:
    v = str(v or "").strip().lower()
    return (len(v) < 6) or any(w in v for w in ("use ai", "ai/ml", "tbd", "n/a", "unknown", "?"))


@dataclass
class SpecialistOutput:
    role: str
    domain: str
    section_title: str
    findings: list
    recommendation: str
    reference: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        bullets = "\n".join(f"- {f}" for f in self.findings)
        return (f"## {self.section_title} — *FDE {self.domain} specialist*\n"
                f"{bullets}\n\n**Recommendation**: {self.recommendation} "
                f"_(ref: {self.reference})_")


class FDESpecialist:
    role = ""; domain = ""; reference = ""; section_title = ""

    def analyze(self, problem: dict) -> SpecialistOutput:  # pragma: no cover - abstract
        raise NotImplementedError


class ScopingSpecialist(FDESpecialist):
    role = "scoping"; domain = "Scoping & Domain"; reference = "references/fde-methodology.md"
    section_title = "Scope sharpening"

    def analyze(self, problem: dict) -> SpecialistOutput:
        g = problem.get
        findings = []
        for q, label in (("q1_process", "Q1 process"), ("q2_accuracy_target", "Q2 target"),
                         ("q6_primary_metric", "Q6 success metric"), ("q4_direct_cost", "Q4 cost-of-error")):
            if _vague(g(q, "")):
                findings.append(f"{label} is vague/missing — sharpen before building.")
        if not findings:
            findings.append("6-Q is concrete enough to prototype against.")
        rec = (f"Lock the success metric ({g('q6_primary_metric', 'define a measurable KPI')}) "
               f"and the cost-of-error ({g('q4_direct_cost', 'quantify €/error')}) before any code.")
        return SpecialistOutput(self.role, self.domain, self.section_title, findings, rec, self.reference)


class ArchitectureSpecialist(FDESpecialist):
    role = "architecture"; domain = "SaaS Architecture"; reference = "references/saas-playbook.md"
    section_title = "Recommended architecture"

    def analyze(self, problem: dict) -> SpecialistOutput:
        g = problem.get
        decision = str(g("q2_decision_type", "recommendation")).lower()
        latency = str(g("q2_latency", "")).lower()
        compliance = str(g("q3_compliance", "")).lower()
        findings = []
        if "classif" in decision or "score" in decision:
            findings.append("Decision = classification/scoring → gradient-boosted model + calibrated thresholds.")
        else:
            findings.append(f"Decision = {decision} → retrieval + LLM with structured output + guardrails.")
        if any(x in latency for x in ("<1", "real", "ms", "sync")):
            findings.append("Low-latency → containerized inference service, warm pool, cache hot paths.")
        else:
            findings.append("Batch-tolerant → scheduled batch scoring, cheaper compute.")
        if any(x in compliance for x in ("gdpr", "eu", "hipaa", "soc")):
            findings.append(f"Compliance ({g('q3_compliance')}) → in-region data, RBAC, audit log, PII minimization.")
        rec = "Promote the architecture only if it clears the Researcher's held-out gate; keep it reversible (feature-flagged)."
        return SpecialistOutput(self.role, self.domain, self.section_title, findings, rec, self.reference)


class AgentSpecialist(FDESpecialist):
    role = "agent"; domain = "AI-Agent Engineering"; reference = "references/ai-agent-engineering.md"
    section_title = "Eval & guardrails"

    def analyze(self, problem: dict) -> SpecialistOutput:
        g = problem.get
        target = g("q2_accuracy_target", "the stated target")
        findings = [
            f"Define a held-out eval gate: promote only if it beats {target}.",
            "Emit reason codes with every decision (not just a score) for reviewability.",
        ]
        cost = str(g("q4_direct_cost", "")).lower()
        if any(c.isdigit() for c in cost) or "high" in cost:
            findings.append(f"High cost-of-error ({g('q4_direct_cost')}) → human-in-the-loop on the riskiest decisions.")
        findings.append("Add red-team / prompt-injection cases to the eval suite before production.")
        rec = "Make evals the promotion contract: no eval gate, no ship."
        return SpecialistOutput(self.role, self.domain, self.section_title, findings, rec, self.reference)


class ProductionSpecialist(FDESpecialist):
    role = "production"; domain = "Production & Evals"; reference = "references/eval-rubric.md"
    section_title = "Production handoff"

    def analyze(self, problem: dict) -> SpecialistOutput:
        g = problem.get
        findings = [
            "Runbook: deploy, rollback, on-call owner, incident path.",
            "Observability: drift monitoring on inputs + outputs, alert on metric regression.",
            f"Cost ceiling tied to ROI threshold ({g('q6_threshold', 'define budget')}); kill-switch if exceeded.",
        ]
        compliance = str(g("q3_compliance", "")).lower()
        if any(x in compliance for x in ("gdpr", "eu", "hipaa", "soc")):
            findings.append(f"Compliance controls for {g('q3_compliance')}: retention policy, DSAR path, access audit.")
        rec = f"Measure success by {g('q6_measurement', 'a monthly cohort/KPI review')}; hand off only with the runbook signed."
        return SpecialistOutput(self.role, self.domain, self.section_title, findings, rec, self.reference)


SPECIALISTS = (ScopingSpecialist, ArchitectureSpecialist, AgentSpecialist, ProductionSpecialist)


def run_specialists(problem: dict, max_workers: int = 4) -> list[SpecialistOutput]:
    """Run the 4 FDE specialists concurrently (the Builder consults them in parallel)."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(lambda S: S().analyze(problem), SPECIALISTS))


def specialists_markdown(outputs: list[SpecialistOutput]) -> str:
    return "\n\n".join(o.to_markdown() for o in outputs)
