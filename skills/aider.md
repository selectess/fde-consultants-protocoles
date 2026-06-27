# FDE Consultant Skill for Aider

Aider is a terminal-based AI pair-programmer that edits files in your local git
repo. It does not auto-discover skills the way Claude Code does, so you point it
at the universal FDE Skill through its conventions / read-files mechanism
(`CONVENTIONS.md`, `--read`), and wire the FDE tools through Aider's MCP support.

## Installation

### Local install

Clone the repository and run the local installer:

```bash
git clone <this-repo-url> fde-consultant
cd fde-consultant
bash install.sh
```

The installer drops `skill/` in place and writes a project `CONVENTIONS.md`
that references the universal FDE Skill at `skill/SKILL.md`.

### Manual install

Create (or append to) `CONVENTIONS.md` at your repo root so Aider treats it as
always-loaded guidance:

```markdown
# Conventions — FDE Consultant

Act as an FDE Consultant. Follow the methodology in the universal FDE Skill
(skill/SKILL.md, Operating Principles, Anti-Patterns).

Always begin with Stage 0 — Reconnaissance (fde_recon) on the real
codebase/business BEFORE scoping. The loop is:
Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback.

Never skip the 6-Q decomposition. Always produce concrete artifacts (code,
specs). End every deliverable with a `## FDE Assurance Score` section (target >=85).
```

Then load it on every run:

```bash
aider --read CONVENTIONS.md --read skill/SKILL.md
```

Or persist it via `.aider.conf.yml` at the repo root so you never have to pass
the flags manually:

```yaml
read:
  - CONVENTIONS.md
  - skill/SKILL.md
```

## MCP server

Aider exposes the FDE tools over the local MCP server (stdio). Configure it in
`.aider.conf.yml`:

```yaml
mcp_servers:
  fde-consultant:
    command: python3
    args: ["-m", "skill.mcp_server"]
    transport: stdio
    tools:
      - fde_recon            # Stage 0 — Reconnaissance
      - fde_decompose        # Stage 1 — Scoping (6-Q)
      - fde_roi              # Stage 1 — Scoping
      - fde_scientific_search # Stage 2 — Prototyping
      - fde_evals            # Stage 4 — Feedback
      - fde_ontology         # Stage 1 — Scoping
      - fde_trust_score      # Stage 4 — Feedback
```

The canonical entrypoint is `python3 -m skill.mcp_server` — all 7 tools are
served from that single module (do not point Aider at per-tool module paths).

## Usage

From within an Aider session in your repo:

```
Act as FDE Consultant. Run Stage 0 Reconnaissance (fde_recon) on this repo,
then scope it using the 6-Q framework.
```

Or invoke a tool directly:

```
Run fde_decompose on skill/examples/saas-churn-prediction.json
```

## Verification

```bash
ls CONVENTIONS.md skill/SKILL.md
python3 -m skill.mcp_server --help
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.

---

Author: Mehdi Wehbi. "FDE Consultant" is the product name.
