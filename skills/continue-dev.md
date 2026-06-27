# FDE Consultant Skill for Continue.dev

## Installation

### Manual

Continue.dev supports skills via `.continue/config.json`:

```bash
# After cloning the Skill repo
cd /your/project
mkdir -p .continue
cat > .continue/config.json << 'EOF'
{
  "models": [...],
  "skills": [
    {
      "name": "fde-consultant",
      "path": "/path/to/fde-skill/skill/SKILL.md"
    }
  ]
}
EOF
```

## Usage

In Continue.dev (`Cmd+L` or `Ctrl+L`), type:

```
Use the FDE Consultant skill. Start with Stage 0 Reconnaissance — run `skill/scripts/fde_recon.py` (or the `fde_recon` tool) to scrutinize the codebase — before scoping. Then scope this project.
```

## Verification

```bash
cat .continue/config.json | grep fde-consultant
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
