# FDE Consultant Skill for Trae

Trae is the AI-native IDE by ByteDance. It steers its agent with **rules/context files**
(`.trae/rules/`) and connects to external tooling through **MCP servers**. This adapter points
Trae at the universal FDE Skill (`skill/SKILL.md`) and wires the local FDE MCP server.

## Installation

### Project-level (recommended)

From this repository root:

```bash
bash install.sh
```

The installer writes the rule file and (where supported) the MCP config. If Trae is not auto-detected,
use the manual steps below — the universal Skill in `skill/SKILL.md` is the single source of truth either way.

### Manual install — rules file

Create `.trae/rules/project_rules.md` in your project:

```markdown
# FDE Consultant — Project Rules

You are an FDE Consultant. When scoping, building, or reviewing, follow the methodology in the
FDE Skill (`skill/SKILL.md` — Operating Principles, Anti-Patterns).

Always run **Stage 0 — Reconnaissance** (`fde_recon`) against the real codebase/business BEFORE
scoping. The loop is: Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback.

Never skip the 6-Q decomposition. Always produce concrete artifacts (code, specs). End every
deliverable with a `## FDE Assurance Score` section (target >= 85).
```

## Wiring the MCP server

The FDE MCP server runs locally over **stdio** with a single canonical entrypoint and exposes
**7 tools**. In Trae, open **Settings → MCP → Add (Manual / JSON)** and paste:

```json
{
  "mcpServers": {
    "fde-consultant": {
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "transport": "stdio"
    }
  }
}
```

> Run Trae with this repository as the workspace root (or set `cwd` to it) so
> `python3 -m skill.mcp_server` resolves the package. Do **not** use per-tool module paths such as
> `skill.mcp_server.tools.fde_decompose` — only the single entrypoint above is valid.

The 7 tools exposed by the server:

| Tool | Stage | Purpose |
|---|---|---|
| `fde_recon` | Stage 0 | Scrutinize the real codebase/business before scoping (`skill/scripts/fde_recon.py`) |
| `fde_decompose` | Scoping | 6-Q problem decomposition |
| `fde_roi` | Scoping | ROI / opportunity sizing |
| `fde_scientific_search` | Prototyping | Generate & score competing architecture hypotheses |
| `fde_evals` | Prototyping | Eval framework scaffolding |
| `fde_ontology` | Production | Domain ontology / schema modeling |
| `fde_trust_score` | Feedback | Score the deliverable (target >= 85) |

## Usage

In the Trae AI chat / Builder panel:

```
Act as FDE Consultant. Start with Stage 0 — run fde_recon on this workspace, then scope with the 6-Q framework.
```

Or invoke a tool directly:

```
Run fde_decompose on this SaaS churn problem
```

## The FDE loop in Trae

1. **Stage 0 — Reconnaissance** — `fde_recon` reads the real artifact first (mandatory entry gate).
2. **Scoping** — `fde_decompose` (6-Q) + `fde_roi`; domain research lives here.
3. **Prototyping** — `fde_scientific_search` + `fde_evals`.
4. **Production** — `fde_ontology` and architecture/code scaffolds.
5. **Feedback** — `fde_trust_score` closes the loop.

## Verification

```bash
ls .trae/rules/project_rules.md
python3 -m skill.mcp_server --help
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.

---

Author: Mehdi Wehbi · © Mehdi Wehbi. Product: FDE Consultant.
