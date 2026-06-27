"""FDE Consultant Skill MCP Server.

Exposes the 8 FDE Python scripts as MCP tools (stdio transport).
This is the canonical entry point for AI agents (Claude Code, Cursor,
Windsurf, Codex, OpenClaw) that want to invoke FDE methodology programmatically
instead of just reading SKILL.md.

Usage:
    # Add to Claude Code / Cursor MCP config:
    {
      "mcpServers": {
        "fde-consultant": {
          "command": "python3",
          "args": ["-m", "skill.mcp_server"],
          "cwd": "/path/to/fde-skill"
        }
      }
    }

Tools exposed:
    fde_decompose       — validate 6-Q decomposition of a problem
    fde_roi             — compute ROI + payback + NPV
    fde_scientific_search — generate hypotheses, apply held-out gate, write lessons
    fde_evals           — score 6-trait rubric on a deliverable
    fde_ontology        — extract Palantir-style ontology from notes
    fde_trust_score     — compute Trust Score (25+25+30+20) for a deliverable

Architecture:
    server.py    — FastMCP server definition, registers all tools
    tools/       — one file per tool, each imports from skill/scripts/
    __main__.py  — entry point (python -m skill.mcp_server)
"""
__version__ = "1.0.0"