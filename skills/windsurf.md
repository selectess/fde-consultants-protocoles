# FDE Consultant Skill for Windsurf

## Installation

### Project-level (recommended)

The repo already ships the rule at `.windsurf/rules/fde-consultant.mdc`. Clone it and the editor picks it up — or copy it into your own project:

```bash
# the rule ships in the repo — just clone it
git clone https://github.com/selectess/fde-consultants-protocoles fde-consultant
```

Both `.cursor/rules/fde-consultant.mdc` and the byte-identical `.windsurf/rules/fde-consultant.mdc` ship in this repo — clone and use, no installer step.

(The Cursor `.mdc` rule format is compatible with Windsurf.)

### Manual install

Create `.windsurf/rules/fde-consultant.mdc` with the same content as the Cursor rule (see `cursor.md`).

## Usage

In Windsurf, type:

```
Act as FDE Consultant. Start with Stage 0 Reconnaissance — run `skill/scripts/fde_recon.py` (or the `fde_recon` MCP tool) to scrutinize the codebase — then run the 5-stage loop: Reconnaissance → Scoping → Prototyping → Production → Feedback.
```

## Verification

```bash
ls .windsurf/rules/fde-consultant.mdc
```

## Compatibility

Windsurf is a Cursor-compatible editor. The same `.mdc` rule format works in both.

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
