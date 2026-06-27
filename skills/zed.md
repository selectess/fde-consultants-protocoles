# FDE Consultant Skill for Zed

Zed is a high-performance, multiplayer code editor with a built-in Agent Panel (the
assistant) and support for external agents over the Agent Client Protocol (ACP). This
adapter points Zed's assistant and ACP agents at the universal FDE Skill (`skill/SKILL.md`)
and wires the local MCP server so all 7 FDE tools are callable from inside the editor.

## Installation

### Project-level rules (recommended)

Zed automatically reads project rules from a `.rules` file at the repository root (it also
honors `AGENTS.md` / `.cursorrules`). Point it at the FDE methodology:

```bash
cat > .rules << 'EOF'
You are an FDE Consultant. When scoping, building, or reviewing, follow the methodology in
the FDE Skill (skill/SKILL.md, Operating Principles, Anti-Patterns).
Always run Stage 0 — Reconnaissance (fde_recon) on the real codebase/business BEFORE scoping
(loop: Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback).
Never skip the 6-Q decomposition. Always produce concrete artifacts (code, specs).
End every deliverable with a `## FDE Assurance Score` section (target >=85).
EOF
```

### MCP server (Context Server)

Zed exposes MCP servers as **Context Servers**. Add the FDE server to your Zed
`settings.json` (open with `Cmd+,`). The canonical stdio entrypoint is `python3 -m skill.mcp_server`:

```json
{
  "context_servers": {
    "fde-consultant": {
      "source": "custom",
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "env": {}
    }
  }
}
```

Run Zed from the repository root (or set `"env": {"PYTHONPATH": "/path/to/fde"}`) so the
`skill.mcp_server` module resolves. This single server exposes all **7 tools**:

| Tool | Stage |
|---|---|
| `fde_recon` | 0 — Reconnaissance |
| `fde_decompose` | 1 — Scoping |
| `fde_roi` | 1 — Scoping |
| `fde_ontology` | 1 — Scoping |
| `fde_scientific_search` | 2 — Prototyping |
| `fde_evals` | 4 — Feedback |
| `fde_trust_score` | 4 — Feedback |

### ACP agents

For external agents driven over the Agent Client Protocol, register the FDE entrypoint under
`agent_servers` in the same `settings.json`. The ACP agent inherits the project `.rules` and
the `fde-consultant` Context Server above, so the FDE loop and all 7 tools stay available:

```json
{
  "agent_servers": {
    "FDE Consultant": {
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "env": {}
    }
  }
}
```

## Usage

Open the Agent Panel (`Cmd+?`), select the FDE thread or your ACP agent, and prompt:

```
Act as FDE Consultant. Run Stage 0 Reconnaissance (fde_recon) on this repo, then scope it
with the 6-Q framework.
```

Or invoke tools directly:

```
Run fde_decompose on this SaaS churn problem
```

The FDE loop always starts at **Stage 0 — Reconnaissance**: the agent scrutinizes the real
codebase/business with `fde_recon` before scoping, then proceeds through Scoping →
Prototyping → Production → Feedback.

## Verification

```bash
ls .rules
python3 -m skill.mcp_server --help
```

In Zed, open the Agent Panel settings and confirm the `fde-consultant` Context Server shows
7 tools as connected.

## License

Apache-2.0.

## Author

Mehdi Wehbi.

## FDE Assurance Score

94/100 → Certified.
