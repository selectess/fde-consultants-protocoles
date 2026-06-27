"""Tools package: one module per MCP tool.

Each module wraps an existing skill/scripts/*.py CLI into an MCP @mcp.tool()
function so AI agents can invoke the FDE methodology programmatically.

Tools exposed:
    decompose.py        -> fde_decompose
    roi.py              -> fde_roi
    scientific_search.py -> fde_scientific_search
    evals.py            -> fde_evals
    ontology.py         -> fde_ontology
    trust_score.py      -> fde_trust_score (NEW: pure Trust Score calculation)
"""
__all__ = [
    "decompose",
    "roi",
    "scientific_search",
    "evals",
    "ontology",
    "trust_score",
]