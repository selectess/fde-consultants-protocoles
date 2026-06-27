"""Entry point: python -m skill.mcp_server.

Runs the MCP server on stdio transport. Add to your MCP client config:

    {
      "mcpServers": {
        "fde-consultant": {
          "command": "python3",
          "args": ["-m", "skill.mcp_server"]
        }
      }
    }
"""
import sys
from .server import main

USAGE = """FDE Consultant — local MCP server (stdio transport).

Usage:
  python3 -m skill.mcp_server          serve the 7 FDE tools on stdio
  python3 -m skill.mcp_server --help   print this help and exit

Tools: fde_recon · fde_decompose · fde_roi · fde_scientific_search ·
       fde_evals · fde_ontology · fde_trust_score

MCP client config:
  {"mcpServers": {"fde-consultant": {"command": "python3",
                  "args": ["-m", "skill.mcp_server"]}}}
"""

if __name__ == "__main__":
    if any(a in ("-h", "--help", "--list-tools") for a in sys.argv[1:]):
        print(USAGE)
        sys.exit(0)
    sys.exit(main())