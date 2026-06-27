"""MCP tool: fde_recon

Wraps skill/scripts/fde_recon.py as an MCP tool.
Stage 0 reconnaissance: scrutinize a real codebase before scoping, and turn the
findings into 6-Q signals. The FDE rule is "scrutinize before you scope".

Input: a filesystem path to the repository to scan.
Output: JSON dossier (size, languages, dependencies, tests, tech-debt,
ontology candidates, git hotspots, risk flags, six_q_signals, summary).
"""
import pathlib
import sys
from typing import Any

# Make fde_recon.py importable
SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mcp.server.fastmcp import FastMCP

from fde_recon import scan_codebase


def register(mcp: FastMCP) -> None:
    """Register the fde_recon tool on the given FastMCP server."""

    @mcp.tool(
        name="fde_recon",
        description=(
            "Stage 0 (Reconnaissance): scan a real codebase BEFORE scoping. "
            "Returns languages, LOC, dependencies (incl. AI/ML libs), test "
            "coverage, tech-debt markers, complexity/git hotspots, ontology "
            "candidates, risk flags, and 6-Q pre-fill signals. Run this first so "
            "the FDE 6-Q decomposition is grounded in the actual code, not "
            "imagination."
        ),
    )
    def fde_recon(path: str = ".") -> dict[str, Any]:
        """Scrutinize a codebase and return the FDE reconnaissance dossier.

        Args:
            path: Filesystem path to the repository to scan.

        Returns:
            dict dossier with keys: summary, size, languages, dependencies,
            tests, tech_debt, hotspots, ontology_candidates, project_hygiene,
            git, risk_flags, six_q_signals.
        """
        return scan_codebase(pathlib.Path(path))
