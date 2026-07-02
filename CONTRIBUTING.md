# Contributing to FDE Consultant

This project follows its own [Operating Principles](skill/SKILL.md) and [Anti-Patterns](skill/SKILL.md).
We reject PRs that violate them.

## The Four-Checklist for Every PR

Before opening a PR, your contribution must answer all four questions:

### 1. Falsifiable claim
What does this PR change? In one sentence, what is now measurably different?

> ❌ "Improves performance"
> ✅ "Reduces cold-start time from 2.1s to 1.4s (measured via `pytest --benchmark`)"

### 2. Three failure modes
What could go wrong? What did you mitigate? List three risks, even if minor.

> ❌ "Tested locally, looks good"
> ✅ "Failure modes: (1) race condition in concurrent MCP calls, mitigated by adding a lock; (2) binary read on text-only path, mitigated by `isinstance` check; (3) version drift in dependency, mitigated by pinning `==1.2.3`."

### 3. Evidence trail
File:line pointers + test commands. Every claim must be traceable to a file, a SHA, or a passing test.

> ❌ "Works on my machine"
> ✅ "Verified by `pytest skill/tests/ -q` (36 passed), file `skill/scripts/decompose_problem.py:42-58` implements the new branch, SHA `aaca7ce...595c59500` matches the certified SKILL.md."

### 4. Anti-pattern check
No scope creep, no buzzword inflation, no self-certification.

> ❌ "This is industrial-grade / state-of-the-art / next-gen"
> ✅ "This is a bugfix that adds a missing input check."

## Local setup

```bash
git clone https://github.com/selectess/fde-consultants-protocoles.git
cd fde-consultants-protocoles

# Install dev dependencies (Python 3.10+)
python3 -m pip install pytest pytest-asyncio

# Run all tests (must pass 154/154 (skill + modex; the hosted MCP Cloud suite is private))
python3 -m pytest skill/tests/ modex/tests/

# Re-certify the Skill (must return 100/100 certified)
python3 -m modex.certify_skill --skill-path ./skill --output ./cert.json
```

## Code style

- **Python**: PEP 8, type hints, no external deps beyond `pytest` (for tests) and `httpx`/`fastapi` (for MCP server).
- **Markdown**: sentence case for titles, no trailing whitespace, fenced code blocks with language tags.
- **Shell**: `set -e`, `set -u`, shellcheck-clean.
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`).

## Branch & PR process

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-change`
3. Add tests for any new behavior (`test_your_change.py` in the relevant `tests/` dir)
4. Run the full test suite (must be 154+ passing)
5. Open a PR with the **four-checklist** as the PR body

## What we will reject

- PRs without tests
- PRs that introduce external dependencies without justification
- PRs that change the FDE Assurance Score without re-running the Certifier
- PRs that add buzzwords without evidence
- PRs that "fix" something unrelated to the PR title

## What we love

- A test that fails before the fix and passes after
- A SHA-256 hash that proves a deliverable wasn't tampered with
- A case study with a real customer problem (anonymized)
- A reduction in test runtime (we benchmark 154 tests in ~10s)

## Code of conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/).
Be technical, not personal. Disagree on facts, agree on principles.

## License

By contributing, you agree your contribution is licensed under:
- Apache-2.0 if you touch `skill/`, `registry/`, or docs
- MIT if you touch `modex/` core
- BSL 1.1 if you touch `modex/plugin_loader.py` or `modex/license.py`

See [`LICENSE`](LICENSE) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for details.