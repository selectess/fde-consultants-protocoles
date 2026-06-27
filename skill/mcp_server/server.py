"""FDE Consultant Skill MCP Server — registers all 7 tools.

Uses FastMCP (the high-level API from the official MCP Python SDK).
Transport: stdio (the canonical transport for local MCP servers).
"""
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Make skill/scripts/ importable when invoked as `python -m skill.mcp_server`
SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REFS_DIR = SKILL_ROOT / "references"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Lazy / type-checked imports to keep static analyzers (Pyright, Pylance)
# from complaining about non-installed-in-IDE packages.
if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP  # noqa: F401
else:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        FastMCP = None  # type: ignore[assignment]

# Initialize the server with the canonical Skill identity
mcp = FastMCP(
    name="fde-consultant",
    instructions=(
        "Forward Deployed Engineering (FDE) methodology tools for AI agents. "
        "Use these tools to apply the FDE 4-stage loop (Scoping -> Prototyping -> "
        "Production -> Feedback) with rigorous FDE Assurance Score verification. "
        "Every deliverable must end with a FDE Assurance Score >= 85 before shipping. "
        "See skill/SKILL.md for the full operating principles."
    ),
)

# Import tool modules and register them on the shared `mcp` instance
from .tools import (
    recon,
    decompose,
    roi,
    scientific_search,
    evals,
    ontology,
    trust_score,
)

recon.register(mcp)
decompose.register(mcp)
roi.register(mcp)
scientific_search.register(mcp)
evals.register(mcp)
ontology.register(mcp)
trust_score.register(mcp)


def main() -> int:
    """Run the MCP server on stdio. Returns process exit code."""
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())