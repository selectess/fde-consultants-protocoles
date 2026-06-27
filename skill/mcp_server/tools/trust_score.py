"""MCP tool: fde_trust_score

NEW: compute the DeepSCR FDE Assurance Score (25+25+30+20) for a deliverable.

This is the Stage 4 (Feedback / Certification) tool. Use it to:
1. Compute the score from the 4 components (each 0..max).
2. Get the verdict (certified / needs_revision / rejected).
3. Hash the deliverable to produce the SHA-256 audit trail.
4. Build the canonical trust-score.json output (same schema as fde-memory/).

Inputs are the 4 components explicitly. This is a *certifier* tool: it does
not read the deliverable itself. The agent must assess each component based
on evidence and pass the booleans.
"""
import hashlib
import json
import pathlib
from typing import Any

from mcp.server.fastmcp import FastMCP

# Canonical thresholds (mirror of skill/references/fde-trust-score.md)
WEIGHTS = {
    "claim": 25,
    "contradiction": 25,
    "evidence": 30,
    "antipatterns": 20,
}
VERDICTS = {
    "certified": (85, 101),      # 85 <= score <= 100
    "needs_revision": (60, 85),  # 60 <= score < 85
    "rejected": (0, 60),         # 0 <= score < 60
}


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="fde_trust_score",
        description=(
            "Compute the DeepSCR FDE Assurance Score (0-100) for an FDE deliverable. "
            "Pass the 4 components as booleans (claim_present, has_3_failure_modes, "
            "has_evidence_trail, antipatterns_clean) plus an optional deliverable_path "
            "to compute the SHA-256 audit hash. Returns the canonical "
            "trust-score.json schema."
        ),
    )
    def fde_trust_score(
        claim_present: bool,
        has_3_failure_modes: bool,
        has_evidence_trail: bool,
        antipatterns_clean: bool,
        claim_text: str = "",
        deliverable_path: str = "",
    ) -> dict[str, Any]:
        """Compute FDE Assurance Score from the 4 components.

        Args:
            claim_present: Is there a 1-sentence falsifiable claim?
            has_3_failure_modes: Are at least 3 failure modes documented?
            has_evidence_trail: Is there at least 1 file:line pointer?
            antipatterns_clean: Is the deliverable clean of the 10 anti-patterns?
            claim_text: The claim text (stored in the trust-score.json).
            deliverable_path: Path to the deliverable file (will be SHA-256 hashed).

        Returns:
            dict matching the canonical fde-trust-score-v1 schema.
        """
        components = {
            "claim": WEIGHTS["claim"] if claim_present else 0,
            "contradiction": WEIGHTS["contradiction"] if has_3_failure_modes else 0,
            "evidence": WEIGHTS["evidence"] if has_evidence_trail else 0,
            "antipatterns": WEIGHTS["antipatterns"] if antipatterns_clean else 0,
        }
        score = sum(components.values())

        # Determine verdict
        if score >= VERDICTS["certified"][0]:
            verdict = "certified"
        elif score >= VERDICTS["needs_revision"][0]:
            verdict = "needs_revision"
        else:
            verdict = "rejected"

        # Compute SHA-256 if deliverable provided
        sha256 = ""
        if deliverable_path:
            p = pathlib.Path(deliverable_path)
            if p.exists() and p.is_file():
                sha256 = hashlib.sha256(p.read_bytes()).hexdigest()

        # Find the lowest component (to fix first)
        lowest = min(components.keys(), key=lambda k: components[k])

        return {
            "schema": "fde-trust-score-v1",
            "deliverable": deliverable_path,
            "claim": claim_text,
            "components": components,
            "trust_score": score,
            "verdict": verdict,
            "sha256": sha256,
            "lowest_component": lowest,
            "independent_of_lead": True,
            "weights": WEIGHTS,
        }