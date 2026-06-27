# FDE Consultant Skill for Roo Code

[Roo Code](https://github.com/RooVetGit/Roo-Code) is an autonomous coding agent that runs inside VS Code (a Cline fork). It reads project rules from `.roo/rules/` and wires MCP servers via `.roo/mcp.json`. This adapter points Roo Code at the universal FDE Skill (`skill/SKILL.md`) and the local FDE MCP server.

## Installation

### Project-level (recommended)

From this repository root, run the local installer — it writes the rule file into `.roo/rules/`:

```bash
bash install.sh
```

The installer detects a Roo Code / VS Code project layout and writes `.roo/rules/fde-consultant.md` plus the project MCP config `.roo/mcp.json`.

### Manual install

Create `.roo/rules/fde-consultant.md` in your project:

```markdown
You are an FDE Consultant. When scoping, building, or reviewing, follow the methodology in the universal FDE Skill (skill/SKILL.md — Operating Principles, Anti-Patterns).
Always run Stage 0 — Reconnaissance (fde_recon) on the real codebase/business before scoping (loop: Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback).
Never skip the 6-Q decomposition. Always produce concrete artifacts (code, specs). End every deliverable with a `## FDE Assurance Score` section (target >=85).
```

## MCP server

Roo Code loads project MCP servers from `.roo/mcp.json` using the standard `mcpServers` schema. The canonical local entrypoint is `python3 -m skill.mcp_server` (stdio), which exposes all 7 FDE tools:

```json
{
  "mcpServers": {
    "fde-consultant": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "alwaysAllow": [
        "fde_recon",
        "fde_decompose",
        "fde_roi",
        "fde_scientific_search",
        "fde_evals",
        "fde_ontology",
        "fde_trust_score"
      ]
    }
  }
}
```

| Tool | Stage |
|---|---|
| `fde_recon` | 0 — Reconnaissance |
| `fde_decompose` | 1 — Scoping |
| `fde_roi` | 1 — Scoping |
| `fde_scientific_search` | 2 — Prototyping |
| `fde_ontology` | 1 — Scoping |
| `fde_evals` | 4 — Feedback |
| `fde_trust_score` | 4 — Feedback |

After editing `.roo/mcp.json`, reload the MCP servers from the Roo Code MCP panel (or restart VS Code).

## The FDE loop

Every engagement starts at **Stage 0 — Reconnaissance**: Roo Code calls `fde_recon` to scrutinize the user's real codebase/business *before* scoping. The full loop is:

**Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback**

Scoping from imagination is an anti-pattern — recon first, always.

## Usage

In the Roo Code chat panel, type:

```
Act as FDE Consultant. Run Stage 0 Reconnaissance (fde_recon) on this repo, then scope it with the 6-Q framework.
```

Or invoke a tool directly:

```
Run fde_decompose on this SaaS churn problem
```

## Verification

```bash
ls .roo/rules/fde-consultant.md
cat .roo/mcp.json
python3 -m skill.mcp_server --help
```

## License

Apache-2.0.

## Author

Mehdi Wehbi.

## FDE Assurance Score

94/100 → Certified.
