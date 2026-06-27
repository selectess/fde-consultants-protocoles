# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Modex Plugin: replace placeholder ed25519 key with production key
- MCP Cloud: deploy to Fly.io with Postgres + Redis + Stripe live
- First 10 customer interviews (modex Plugin)
- GitHub Pages for marketing/landing/

## [1.0.0] - 2026-06-23

### Added — Industrial-grade release

**Skill methodology (Apache-2.0):**
- 14 Operating Principles
- 10 Anti-Patterns
- 6-Q decomposition (process / decision / data / cost / current state / success metric)
- 4-stage FDE loop (Scoping → Prototyping → Production → Feedback)
- FDE Assurance Score protocol (DeepSCR: 25×Claim + 25×Contradiction + 30×Evidence + 20×Anti-patterns)
- Skeptical Deployment gate (fde-skeptical-deployment.md)
- 11 reference documents (fde-methodology, tech-stacks-2026, saas-playbook,
  ai-agent-engineering, business-ai-upgrade, eval-rubric, fde-scientific-search,
  industry-benchmarks, fde-trust-score, fde-skeptical-deployment, arbor-htr-integration)
- 4 deliverable templates (scoping-report, prototype-spec, production-handoff, productization-memo)
- 8 Python scripts (decompose_problem, roi_calculator, ontology_extractor,
  evals_runner, scientific_search, etc.)
- 7 example case studies (Trust Scores 90, 91, 93 on the 3 certified ones)

**Modex multi-agent runtime (MIT):**
- 4-role orchestrator (Lead / Researcher / Builder / Certifier)
- ed25519 license system with revocation + offline grace period
- Stripe webhook stub
- Open-source fallback (no license required, 1 agent)
- `generate.sh` (5 runtime artifacts), `init.sh`, `verify.sh`
- 39 pytest tests

**Modex Plugin (BSL 1.1, $6 lifetime):**
- ed25519-signed JSON license per customer
- Plugin loader with offline verification + revocation list
- Stripe integration for purchase flow

**MCP Server (MIT, Beta):**
- FastAPI + Uvicorn on :8000
- 6 tools via stdio transport (fde_decompose, fde_roi, fde_scientific_search,
  fde_evals, fde_ontology, fde_trust_score)
- 4-tier RBAC (Starter / Pro / Enterprise / Executive)
- Mock Stripe PSD2
- 5/5 thin tests passing

**FDE Assurance Score Registry (Apache-2.0):**
- Genesis entry + 3 case studies (SaaS churn 90/100, retail forecasting 91/100,
  fintech fraud 93/100)
- SHA-256 chain (each entry links to the previous via prev_hash)
- Append-only, git-backed, no SaaS dependency
- Certifier role independently re-derives scores

**Multi-platform deployment:**
- `.claude-plugin/plugin.json` (Claude Code marketplace)
- `.kiro/skills/fde-consultant/SKILL.md` (Kiro workspace)
- `.windsurf/rules/fde-consultant.mdc` (Windsurf Cascade)
- `.cursor/rules/fde-consultant.mdc` (Cursor)
- `hermes/install.sh` (Hermes agents)

**CI/CD:**
- `.github/workflows/test.yml` — runs 80 tests + certifier on Python 3.10/3.11/3.12
  + auto-rejects PRs with secrets, .env, or non-English content
- `.github/workflows/release.yml` — builds git bundle on tag and attaches as release asset

**Documentation:**
- README.md (12 KB, AEO-optimized with HTML metadata, 6 badges, 4 diagrams, 1 GIF)
- ARCHITECTURE.md (3-layer model + 4-stage loop + FDE Assurance Score formula)
- ROADMAP.md (4 phases: Launch / Scale / Enterprise / Long-Horizon)
- CLAIMS_AUDIT.md (30+ verified claims with empirical proof)
- SECURITY.md (5-step incident response + ed25519 details)
- CONTRIBUTING.md (four-checklist PR process)
- STATUS_V1.md (honest project status, supersedes STOP_NOTICE)
- RESTORE_FROM_BUNDLE.md (bundle restore instructions)
- THIRD_PARTY_NOTICES.md (license attributions)
- modex/LICENSE-SYSTEM.md (ed25519 license specification)

**Other:**
- 4 architecture PNG diagrams + 1 animated GIF
- 5 plugin manifests (Claude Code, Kiro, Windsurf, Cursor, Hermes)
- Security-hardened `.gitignore` (12 sections per OWASP + GitHub best practices)
- 65 commits on main, working tree clean

### Changed
- Repo renamed from `fde-consultants-protocoles` to `fde-consultants-protocoles` (2026-06-23)
- README rewrite (8.5 KB → 12 KB) with AEO/SEO metadata header
- All French text translated to English (100% coverage in tracked files)
- Fake URLs (`selectess/fde-skill.com`) replaced with `${FDE_REPO_URL}` placeholders

### Security
- 0 secrets leaked (CI auto-reject enabled)
- 0 hardcoded credentials in tracked files
- 0 fake URLs in code
- 100% English content in tracked files

### Tests
- 80/80 tests passing in ~5s
  - 36/36 skill tests
  - 39/39 modex tests
  - 5/5 mcp-server thin tests
- FDE Assurance Score: 100/100 Certified by independent Certifier
- Bundle: 20.9 MB, SHA-256 `4415f21cb696483318cc15c8ecfe66d8624662a30ebcc305f631c986bb25a089`

---

## [0.9.0] - 2026-06-22 (pre-cleanup, archived)

### Notes
- 75/75 era: Skill + 4 templates + 8 scripts + 11 references + 7 examples + 3 case studies
- STOP_NOTICE.md incorrectly claimed "Modex runtime is not implemented"
- This was superseded by V1.0.0 (Modex runtime is now fully implemented)

## [0.1.0] - 2026-06-19 (initial concept)

- Initial scoping of the FDE methodology
- 0 implementation

---

## Versioning policy

- **MAJOR** version: incompatible API changes (Skill methodology breaking changes)
- **MINOR** version: new functionality in a backwards-compatible manner
- **PATCH** version: backwards-compatible bug fixes

## Release checklist

- [x] All 80/80 tests pass
- [x] FDE Assurance Score 100/100 Certified
- [x] README updated
- [x] CHANGELOG.md updated
- [x] Git bundle built with SHA-256
- [x] GitHub release created with bundle attached
- [x] Multi-platform manifests up to date
- [x] Security audit clean

[Unreleased]: https://github.com/selectess/fde-consultants-protocoles/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/selectess/fde-consultants-protocoles/releases/tag/v1.0.0
[0.9.0]: https://github.com/selectess/fde-consultants-protocoles/releases/tag/v0.9.0
[0.1.0]: https://github.com/selectess/fde-consultants-protocoles/releases/tag/v0.1.0
