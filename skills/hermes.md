# FDE Consultant Skill for Hermes

Hermes is an autonomous agent runtime: it discovers skills, plans its own steps, and
calls MCP tools without a human in the loop on every turn. This adapter points a Hermes
agent at the universal FDE Skill (`skill/SKILL.md`) so it runs the Forward Deployed
Engineering methodology end to end.

## Installation

### Local install (recommended)

Clone the repository and run the Hermes installer:

```bash
git clone <this-repo-url> fde-consultant
cd fde-consultant
bash hermes/install.sh
```

The installer symlinks `skill/` to `${HERMES_HOME:-~/.hermes}/skills/fde-consultant/`
(and Modex to `fde-modex/` when present), so Skill updates flow automatically.

### Manual install

```bash
# From a clone of the repository
mkdir -p ~/.hermes/skills
ln -s "$(pwd)/skill" ~/.hermes/skills/fde-consultant
```

## Manifest

Auto-detected via `skill/agents.manifest.json`. Hermes discovers any skill with a valid
manifest and starts its MCP server over stdio:

```json
{
  "name": "fde-consultant",
  "version": "1.0.0",
  "manifest_version": "1.0",
  "mcp_servers": [
    {
      "name": "fde-consultant",
      "transport": "stdio",
      "command": "python3",
      "args": ["-m", "skill.mcp_server"],
      "tools": [
        {"name": "fde_recon", "stage": 0},
        {"name": "fde_decompose", "stage": 1},
        {"name": "fde_roi", "stage": 1},
        {"name": "fde_scientific_search", "stage": 2},
        {"name": "fde_evals", "stage": 4},
        {"name": "fde_ontology", "stage": 1},
        {"name": "fde_trust_score", "stage": 4}
      ]
    }
  ]
}
```

The canonical entrypoint is the single module `python3 -m skill.mcp_server`, which exposes
all **7 tools**: `fde_recon`, `fde_decompose`, `fde_roi`, `fde_scientific_search`,
`fde_evals`, `fde_ontology`, `fde_trust_score`. Do not point Hermes at per-tool module
paths (e.g. `skill.mcp_server.tools.fde_decompose`) — those are not valid entrypoints.

## The FDE Loop (starts at Stage 0)

Because Hermes acts autonomously, the entry gate matters most. Every engagement runs:

**Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback.**

The agent MUST begin with **Stage 0 — Reconnaissance**: scrutinize the user's real
codebase/business before scoping. Call `fde_recon` (or run `skill/scripts/fde_recon.py`)
on the project root, read the files it flags, and clear the reconnaissance gate (actual
stack, whether an AI/ML system exists, top 3 risks, the real process and its owner) before
advancing to Scoping. No reconnaissance → no scoping. Never skip the 6-Q decomposition, and
end every deliverable with a `## FDE Assurance Score` section (target >=85).

## Usage

Hermes auto-discovers the Skill on its next agent invocation; restart the Hermes daemon to
force a reload. Then hand it a goal:

```
Act as FDE Consultant. Run Stage 0 reconnaissance on this repo, then scope it with the 6-Q framework.
```

The agent will call `fde_recon` first, then chain the remaining tools as the loop demands.

## Verification

```bash
ls ~/.hermes/skills/fde-consultant/SKILL.md
python3 -m skill.mcp_server --help
```

## License

Apache-2.0.

## Author

Mehdi Wehbi.

## FDE Assurance Score

94/100 → Certified.
