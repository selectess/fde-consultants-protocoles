# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Frozen Arbiters** (`modex/arbiters.py`): full-autonomy governance for the Collective —
  sealed tamper-evident Contract (clause-tagged actions, mechanical rejection, measured drift),
  frozen mutation-tested Oracles that override the Certifier at ship time, citation-mandatory
  verdicts (uncited = null), trajectory audit (thrashing/plateau), and a distillation gate
  (only oracle-validated trajectories become lessons; lessons must pass on fresh cases).
  Opt-in via `run_autonomous(contract=…, oracles=…)`; 18 new tests (suite: 144)
- Frozen Arbiters exposed end-to-end: `engage(governed=True)` and `python3 -m modex.engage --governed`
  ship a default governance (sealed Contract over the four DeepSCR stages + frozen oracles proven by
  mutation testing: evals gate, on-disk evidence) and surface the contract report — hash, integrity,
  clause drift, cited verdicts (suite: 147)
- **Measured baseline oracle** (`sota_baseline_gate`): at ship time the frozen oracle re-runs the
  hypothesis search independently and requires a claimed candidate to reproduce, to match its
  measured held-out score, and to beat the best measured alternative — the baseline is measured,
  never declared; a candidate-less deliverable is not-applicable, not vetoed
- Token budget in the Contract (`budgets={"tokens": N}`): deterministic ~4 chars/token proxy,
  honest `budget_exhausted` stop, spend reported in the contract report
- Distillation wired into the loop: a certified, oracle-validated trajectory is distilled into a
  lesson and persisted (`distilled_lessons.jsonl`); vetoed runs leave no lesson (no echo chamber)
- `specialist_report`: the 4 FDE specialists' full analyses ride in the autonomous result as an
  audit trail, not just their names (suite: 154)
- Protocols white paper: new § 6 "Full autonomy — the Frozen Arbiters"
- `$6` buyer journey completed: activation page + accurate license spec
- Protocols page rewritten as a single academic white paper (DeepSCR figure integrated)
- Two HEP entity pages on rising 2026 keywords (FDE demand, verifiable AI), cross-linked from 8 related articles
- WebSite + Organization authority graph, HowTo/Product/WebPage schemas
- Sitemap enriched with `lastmod`/`changefreq`/`priority`; Google Search Console site verification

### Changed
- `.gitignore` hardened: internal working files, service-account keys, and generated multi-runtime exports are never publishable

## [1.0.0] - 2026-06-27

First public release.

### Skill methodology (Apache-2.0)
- 14 Operating Principles and 10 Anti-Patterns
- 6-Q decomposition (process / decision / data / cost / current state / success metric)
- 4-stage FDE loop (Scoping → Prototyping → Production → Feedback)
- FDE Assurance Score protocol (DeepSCR: 25×Claim + 25×Contradiction + 30×Evidence + 20×Anti-patterns)
- 11 reference documents, 4 deliverable templates, 8 Python scripts
- 3 certified case studies (FDE Assurance Scores 90, 91, 93)

### Modex multi-agent runtime (MIT)
- 4-role orchestrator (Lead / Researcher / Builder / Certifier)
- ed25519 license system with revocation list and offline grace period
- Open-source fallback (no license required, single agent)
- `generate.sh` (5 runtime artifacts), `init.sh`, `verify.sh`

### Modex Plugin (BSL 1.1, $6 lifetime)
- ed25519-signed per-customer license
- Plugin loader with offline verification and revocation

### MCP tools
- 7 tools exposed via stdio transport (`fde_decompose`, `fde_roi`,
  `fde_scientific_search`, `fde_evals`, `fde_ontology`, `fde_trust_score`) — Python stdlib only

### FDE Assurance Score Registry (Apache-2.0)
- Genesis entry + 3 case studies, SHA-256 hash chain (append-only, git-backed)
- Independent Certifier re-derives every score (no self-attestation)

### Multi-platform distribution
- Claude Code, Cursor, Windsurf, Codex CLI, OpenClaw, Kiro, Hermes, ChatGPT, Gemini

### Quality & CI
- 116/116 tests passing (41 skill + 75 modex) on Python 3.10–3.13, Linux + macOS
- CI secret-scanning gate (rejects committed tokens, keys, and `.env` files)
- FDE Assurance Score: 100/100 (independent Certifier)

---

## Versioning policy

- **MAJOR** — incompatible changes to the Skill methodology
- **MINOR** — new functionality, backwards-compatible
- **PATCH** — backwards-compatible fixes

[1.0.0]: https://github.com/selectess/fde-consultants-protocoles/releases/tag/v1.0.0
