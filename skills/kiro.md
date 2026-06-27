# FDE Consultant Skill for Kiro

[Kiro](https://kiro.dev) is AWS's spec-driven agentic IDE. It steers the agent
through steering rules (`.kiro/steering/`), specs, and MCP tool servers — which
maps cleanly onto the FDE 5-stage loop. The universal FDE Skill lives at
`skill/SKILL.md`; this adapter points Kiro at it and wires the local MCP server.

## Installation

### Project-level (recommended)

Kiro is project-scoped, so install the Skill into the repo's own `.kiro/`
directory from a clone of this repository:

```bash
mkdir -p .kiro/skills/fde-consultant
cp -R skill/* .kiro/skills/fde-consultant/
```

> Note: the cross-runtime `bash install.sh` targets the **global** agent runtimes
> (Claude Code, Codex, Hermes, openclaw). Kiro reads from the **project-local**
> `.kiro/`, so use the copy above (or the steering setup below).

### Manual install

Point Kiro at the universal Skill and add a steering rule:

```bash
# From a clone of the repository
mkdir -p .kiro/skills/fde-consultant
cp -R skill/* .kiro/skills/fde-consultant/

mkdir -p .kiro/steering
cat > .kiro/steering/fde-consultant.md << 'EOF'
---
inclusion: always
---

You are an FDE Consultant. When scoping, building, or reviewing, follow the
methodology in the FDE Skill (`.kiro/skills/fde-consultant/SKILL.md`: Operating
Principles, Anti-Patterns).
Always run Stage 0 — Reconnaissance (fde_recon) on the real codebase/business
before scoping. The loop is: Stage 0 Reconnaissance → Scoping → Prototyping →
Production → Feedback.
Never skip the 6-Q decomposition. Always produce concrete artifacts (code,
specs). End every deliverable with a `## FDE Assurance Score` section (target >=85).
EOF
```

## MCP server

Wire the 7 FDE tools via Kiro's workspace MCP config at
`.kiro/settings/mcp.json` (stdio transport, canonical entrypoint
`python3 -m skill.mcp_server`):

```json
{
  "mcpServers": {
    "fde-consultant": {
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "transport": "stdio",
      "disabled": false,
      "autoApprove": [
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
| `fde_ontology` | 1 — Scoping |
| `fde_scientific_search` | 2 — Prototyping |
| `fde_evals` | 4 — Feedback |
| `fde_trust_score` | 4 — Feedback |

## Usage

In the Kiro chat panel:

```
Act as FDE Consultant. Start with Stage 0 — Reconnaissance: run fde_recon to
scrutinize this real codebase/business, then scope it with the 6-Q framework.
```

Or invoke a tool directly:

```
Run fde_decompose on this SaaS churn problem
```

## Verification

```bash
ls .kiro/skills/fde-consultant/SKILL.md
cat .kiro/settings/mcp.json
python3 -m skill.mcp_server --help
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.

---

Author: Mehdi Wehbi · Product: FDE Consultant
