"""MCP tool: fde_ontology

Wraps skill/scripts/ontology_extractor.py as an MCP tool.
Extracts Palantir-style ontology (objects, links, actions) from free text / markdown.
"""
import json
import pathlib
import sys
from typing import Any

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mcp.server.fastmcp import FastMCP

from ontology_extractor import heuristic_extract as extract_ontology, to_mermaid


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="fde_ontology",
        description=(
            "Extract Palantir-style ontology (objects, links, actions) from free "
            "text or markdown interview notes. Returns JSON + a Mermaid erDiagram. "
            "Useful at Stage 1 (Scoping) to formalize a domain before coding."
        ),
    )
    def fde_ontology(notes_markdown: str) -> dict[str, Any]:
        """Extract ontology from notes.

        Args:
            notes_markdown: Free text or markdown to analyze.

        Returns:
            dict with objects, links, actions, mermaid_diagram.
        """
        ontology = extract_ontology(notes_markdown)
        return {
            "objects": [o.__dict__ if hasattr(o, "__dict__") else o for o in ontology.objects],
            "links": [l.__dict__ if hasattr(l, "__dict__") else l for l in ontology.links],
            "actions": [a.__dict__ if hasattr(a, "__dict__") else a for a in ontology.actions],
            "mermaid_diagram": to_mermaid(ontology),
        }