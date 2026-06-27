# Contributing to FDE Consultant Skill

Thank you for helping turn FDE Consultant into a serious open-source operating method for AI agents.

## How to Contribute

1. Create a branch for your change.
2. Make the smallest useful improvement.
3. Run `python3 -m pytest skill/tests -q` from the repository root.
4. Document what changed and why.
5. Open a pull request when the public repository is available.

## What We Want

- New industry examples with real 6-Q fields.
- Better templates for scoping, prototype specs, handoffs, and productization.
- Improved eval rubrics and anti-pattern detection.
- Agent runtime adapters for Claude Code, Codex, Cursor, Windsurf, Hermes, and open-source agents.
- Documentation and Academy improvements.

## Contribution Standard

Every contribution should make the skill more concrete, more testable, or more useful in real delivery work. Avoid vague AI advice, fake benchmarks, and unverified claims.

## Skeptical Deployment Gate (Mandatory)

Before opening a pull request that introduces a **new method, framework, or script**, you MUST complete the Skeptical Deployment loop documented in [references/fde-skeptical-deployment.md](references/fde-skeptical-deployment.md):

1. **Claim**: one-sentence promise of what the method will produce.
2. **Source of Authority**: primary source, not secondary commentary.
3. **Failure Modes**: at least 3 documented ways the method could fail for our users.
4. **Cheapest Test**: the minimal evidence (file, command, page, click) that would prove or disprove the claim.
5. **Decision**: ship, defer, or skip. A PR without this 5-line block will be rejected.

## FDE Assurance Score Gate (Mandatory for templates and entry-points)

Any contribution that modifies a template (`templates/*.md`) or an entry-point (`SKILL.md`, `ZERO-INSTALL.md`, `system-prompt-fde.md`, `AGENT-INSTALL.md`, `README.md`) must end with a `## FDE Assurance Score` section in the PR description, computed as defined in [references/fde-trust-score.md](references/fde-trust-score.md). Ship only if ≥85.
