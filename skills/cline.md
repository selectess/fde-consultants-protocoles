# FDE Consultant Skill for Cline

Cline is an autonomous coding agent for VS Code. It reads project rules from a
`.clinerules` file (or a `.clinerules/` directory) and connects to MCP servers
declared in its MCP settings. This adapter points Cline at the universal FDE
Skill (`skill/SKILL.md`) and wires the local MCP server.

## Installation

### Project-level (recommended)

From this repository root, run the local installer — it writes the rule file for you:

```bash
bash install.sh
```

The installer detects the project layout and writes `.clinerules/fde-consultant.md`.

### Manual install

Create `.clinerules/fde-consultant.md` in your project (or append to a top-level
`.clinerules` file):

```markdown
You are an FDE Consultant. When scoping, building, or reviewing, follow the
methodology in the FDE Skill (skill/SKILL.md, Operating Principles, Anti-Patterns).

Always begin with Stage 0 — Reconnaissance (fde_recon): scrutinize the user's real
codebase/business BEFORE scoping. The loop is:
Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback.

Never skip the 6-Q decomposition. Always produce concrete artifacts (code, specs).
End every deliverable with a `## FDE Assurance Score` section (target >=85).
```

## MCP server

Cline connects to MCP servers through its MCP settings
(`cline_mcp_settings.json`, editable from the Cline MCP Servers panel). Add the
local FDE server over stdio — the canonical entrypoint is `python3 -m skill.mcp_server`:

```json
{
  "mcpServers": {
    "fde-consultant": {
      "transport": "stdio",
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

This exposes the 7 FDE tools, one per loop stage:

| Tool | Stage |
|---|---|
| `fde_recon` | 0 — Reconnaissance |
| `fde_decompose` | 1 — Scoping |
| `fde_roi` | 1 — Scoping |
| `fde_ontology` | 1 — Scoping |
| `fde_scientific_search` | 2 — Prototyping |
| `fde_evals` | 4 — Feedback |
| `fde_trust_score` | 4 — Feedback |

## Usage

In the Cline chat panel:

```
Act as FDE Consultant. Run Stage 0 reconnaissance (fde_recon) on this repo,
then scope it using the 6-Q framework.
```

Or invoke a tool directly:

```
Run fde_decompose on this SaaS churn problem.
```

## Verification

```bash
ls .clinerules/fde-consultant.md
python3 -m skill.mcp_server --help
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.

---

Author: Mehdi Wehbi
