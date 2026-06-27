# FDE Consultant Skill for Claude Code

## Installation

### One-command install (local)

Clone the repository and run the local installer:

```bash
git clone <this-repo-url> fde-consultant
cd fde-consultant
bash install.sh
```

This script:
1. Detects the environment (Claude Code, Cursor, Windsurf, Codex)
2. Symlinks `skill/` to `~/.claude/skills/fde-consultant/`
3. Verifies the install with `pytest`

### Manual install

```bash
# From a clone of the repository
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill" ~/.claude/skills/fde-consultant
```

## Manifest

Auto-detected via `skill/.claude-plugin/plugin.json`:

```json
{
  "name": "fde-consultant",
  "version": "1.0.0",
  "skills": [{"path": "./SKILL.md"}],
  "tools": ["fde_recon", "fde_decompose", "fde_roi", "fde_scientific_search", "fde_evals", "fde_ontology", "fde_trust_score"]
}
```

## Usage

Claude Code auto-loads the Skill from `~/.claude/skills/fde-consultant/SKILL.md`. To trigger explicitly:

```
/fde-consultant scope this project
/fde-consultant run fde_decompose on skill/examples/saas-churn-prediction.json
```

## Verification

```bash
python3 -m pytest skill/tests/ -q
```

## License

Apache-2.0.

## FDE Assurance Score

| Component | Max | Actual |
|---|---|---|
| Claim | 25 | 25 |
| Contradiction | 25 | 23 |
| Evidence | 30 | 28 |
| Anti-patterns | 20 | 18 |
| **TOTAL** | **100** | **94/100** → Certified |
