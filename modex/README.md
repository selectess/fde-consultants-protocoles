# FDE Skill Modex — $6 lifetime

> The declarative configuration that turns any agent runtime into an autonomous **FDE + DeepSCR swarm**. One source (`modex.yaml`), every runtime. The Skill is free; the Modex is the configuration that deploys it as a swarm.

---

## What it is

The **Modex** is a single manifest (`modex.yaml`) plus four role prompts plus a memory schema. Together they turn Claude Code, Cursor, Windsurf, Codex, autonomous agents (autoClaw, openClaw, Hermes), and even web LLMs (ChatGPT, Claude.ai, Gemini) into the **same agent**: an FDE operator that reconnoiters the real codebase/business, scopes, prototypes, productionizes, and **certifies** every deliverable with a FDE Assurance Score.

The open-source Skill (Apache-2.0) is the methodology. The Modex is the **deployment configuration** that makes that methodology run as a coordinated, memory-backed swarm on any runtime.

---

## Why it's $6 lifetime

- The Skill is free (distribution, community, standard).
- The Modex is a one-time $6 purchase: you get the swarm configuration, the 4 role prompts, the local memory schema, and the runtime fan-out generator. No subscription, no server, no API key.
- The MCP server (separate, Beta) is the future recurring tier: hosted team memory, FDE Assurance Score registry, dashboards. It is **not** required to use the Modex.

$6 is the impulse-buy price — less than a coffee — that funds the project while keeping the barrier at zero.

---

## What's in the box

```
modex/
├── modex.yaml              # the single declarative source
├── generate.sh             # fan-out: produces runtime artifacts from the manifest
├── README.md               # this file
├── roles/
│   ├── lead.md             # Coordinator — assigns, collects, obeys the Certifier
│   ├── researcher.md       # Parallel worker — falsifies one hypothesis via held-out gate
│   ├── builder.md          # Produces artifacts + evidence trail (file:line)
│   └── certifier.md        # INDEPENDENT — computes FDE Assurance Score, may veto the Lead
└── memory/
    └── SCHEMA.md           # local-first memory: context.json + episodes/ + lessons.json
```

---

## The swarm topology (Lead + Workers + independent Certifier)

```
         ┌─────────────────────────────────────────┐
         │  LEAD (Coordinator)                      │
         │  Stage 0: Reconnaissance (fde_recon)      │
         │  Stage 1: Hypothesis (6-Q claim)          │
         └────────┬──────────────────────┬──────────┘
                  │ dispatch (parallel)  │ dispatch
                  ▼                      ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │ RESEARCHER (×N)     │   │ BUILDER              │
    │ Stage 2:            │   │ Stage 3:             │
    │ Contradiction       │   │ Verification         │
    │ (held-out gate)     │   │ (evidence trail)     │
    └──────────┬──────────┘   └──────────┬──────────┘
               │ results                 │ artifact
               ▼                         ▼
         ┌─────────────────────────────────────────┐
         │  CERTIFIER (INDEPENDENT)                 │
         │  Stage 4: Certification                  │
         │  FDE Assurance Score ≥85 to ship, else REJECT    │
         └─────────────────────────────────────────┘
```

The Certifier is **structurally separate** from the Lead. This is the DeepSCR separation of powers: the agent that produces the work cannot be the one that declares it done. (The project's own Stage-4 proof showed self-certification scores 80/100 — independence is what lifts it.)

---

## Quick start

```bash
# 1. Generate runtime artifacts (no install, no network)
bash modex/generate.sh

# 2. (Optional) Place them at runtime targets in this project
bash modex/generate.sh --install
```

This produces, in `.fde-modex-out/`:
- `cursor/fde-modex.mdc` + `windsurf/fde-modex.mdc` — IDE rules
- `AGENTS.md` — Codex project guidance
- `system-prompt-autonomous.md` — for autoClaw / openClaw / Hermes
- `zero-install-paste.md` — paste block for ChatGPT / Claude.ai / Gemini

---

## The memory (local-first, zero server)

The swarm writes its state into the project under `fde-memory/`:

| File | Holds |
|---|---|
| `context.json` | Current 6-Q decomposition, stakeholders, stage, claim |
| `episodes/*.md` | One file per major decision/action — the audit trail |
| `lessons.json` | Accumulated rejected-hypothesis lessons (compounds over time) |
| `trust-score.json` | Latest certification verdict + SHA-256 |

Any agent resuming the work reads `fde-memory/` and has the full state. No server, no API, no lock-in. See [`memory/SCHEMA.md`](memory/SCHEMA.md).

---

## How it relates to the rest of FDE

| Layer | Price | Role |
|---|---|---|
| **Skill** (`skill/`) | Free (Apache-2.0) | The methodology + scripts + templates. The hook. |
| **Modex** (`modex/`) | $6 lifetime | The deployment config that runs the Skill as a swarm on any runtime. |
| **MCP Cloud** (hosted) | Recurring (waitlist) | Hosted team memory + FDE Assurance Score registry. Future tier, not required. |
| **DeepSCR** | Free (in the Skill) | The protocol — FDE Assurance Score + held-out gate + falsification. The differentiator. |

---

## FDE Assurance Score of this Modex

The Modex certifies itself by its own protocol. Claim: *"The Modex deploys the FDE + DeepSCR swarm on any runtime via a single manifest."* Falsifiable by running `generate.sh` on a fresh project and checking the artifacts. Evidence: `modex.yaml`, the 4 role prompts, `SCHEMA.md`, `generate.sh`. The score is computed in `work/` alongside the other DeepSCR proofs.
