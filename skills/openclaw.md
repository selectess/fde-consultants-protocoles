# FDE Consultant Skill for OpenClaw / Hermes

## Installation

### Local install

Clone this repository and run the local installer:

```bash
git clone <this-repo-url> fde-consultant
cd fde-consultant
bash install.sh
```

The installer symlinks the Skill into `~/.openclaw/workspace/skills/fde-consultant` (openclaw) and `~/.hermes/skills/fde-consultant` (Hermes).

### Manual install

```bash
# From a clone of the repository
mkdir -p ~/.openclaw/workspace/skills
cp -R "$(pwd)/skill" ~/.openclaw/workspace/skills/fde-consultant
```

## Manifest

Auto-detected via `skill/agents.manifest.json`:

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

## Usage

OpenClaw / Hermes auto-detects agents with a valid `agents.manifest.json` in their skills directory.

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
