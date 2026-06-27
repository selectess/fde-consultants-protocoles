# Template Skill

Minimal starting point for creating a new FDE Consultant Skill.

## How to use

1. Copy this folder: `cp -r template-skill my-new-skill`
2. Rename `template-skill` to your skill name
3. Edit `SKILL.md`:
   - Replace `name:` with your skill name (lowercase, hyphens)
   - Replace `description:` with a 1-sentence description
   - Replace sections marked with `[brackets]`
4. Add your tools, templates, references as needed
5. Write tests: `skill/tests/test_<your-skill>.py`
6. Run: `python3 -m pytest skill/tests/ -q`

## Files

- `SKILL.md` — the skill manifest (frontmatter + body)
- `README.md` — this file

## Validation

After customizing, your skill must:

1. Have a valid YAML frontmatter (name + description)
2. Reference at least one Operating Principle (from `skill/SKILL.md`)
3. Reference at least one Anti-Pattern (from `skill/references/eval-rubric.md`)
4. End with a `## FDE Assurance Score` section ≥85
5. Pass `python3 -m pytest skill/tests/ -q`

## License

Apache-2.0.
