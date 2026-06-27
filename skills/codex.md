# FDE Consultant Skill for OpenAI Codex CLI

## Installation

### Local install

Clone the repository and run the local installer:

```bash
git clone <this-repo-url> fde-consultant
cd fde-consultant
bash install.sh
```

The installer symlinks `skill/` into `~/.agents/skills/fde-consultant/` (Codex auto-scans it).

### Manual install

```bash
# From a clone of the repository
mkdir -p ~/.agents/skills
cp -R "$(pwd)/skill" ~/.agents/skills/fde-consultant
```

## Manifest

Auto-detected via `skill/codex.yaml`:

```yaml
name: fde-consultant
version: 1.0.0
entry_point: SKILL.md
mcp_server:
  command: python3
  args: ["-m", "skill.mcp_server"]
  transport: stdio
  tools:
    - fde_recon
    - fde_decompose
    - fde_roi
    - fde_scientific_search
    - fde_evals
    - fde_ontology
    - fde_trust_score
triggers:
  - "fde"
  - "scope this"
  - "trust score"
trust_score:
  total: 94
  verdict: certified
```

## Usage

In Codex CLI:

```bash
codex --skill fde-consultant "scope this project"
```

Or invoke MCP tools directly.

## Verification

```bash
ls ~/.agents/skills/fde-consultant/SKILL.md
cat ~/.agents/skills/fde-consultant/codex.yaml | head -20
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
