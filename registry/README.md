# FDE Assurance Score Registry

> **Publicly auditable, append-only certification log.** Each entry is a JSON file committed to this git repository. The `shasum`/`prev_hash` chain lets anyone *detect* a change relative to a root they have already witnessed — it does **not**, on its own, prevent the registry operator from rewriting every entry. Real tamper-proofing requires an external anchor. **Read the [Trust model](#trust-model-what-this-proves--and-what-it-does-not) before relying on this.**

## What this is

A chain of FDE Assurance Score certifications, where:

- Each entry references the SHA-256 of the certified artifact.
- Each entry (except genesis) references the SHA-256 of the previous entry — a tamper-evident chain.
- The chain algorithm: `next_hash = sha256(json_of_entry_without_prev_hash)`. The first entry (`genesis.json`) has `prev_hash = null`.

## How to verify

```bash
# 1. Re-hash each entry file and compare to its sha256 in index.json.
#    (Per-entry files do NOT embed their own sha256 — index.json is the manifest,
#     so `shasum -c` does not apply here; hash the files directly instead.)
for f in registry/*.json; do shasum -a 256 "$f"; done
#    → compare each digest to the matching "sha256" in registry/index.json

# 2. Verify linkage: each entry's prev_hash must equal the previous entry's sha256.

# 3. Verify append-only history — only meaningful against a commit you previously
#    witnessed (a force-push can rewrite this locally with no internal trace).
git log --diff-filter=A --name-only --pretty=format: -- registry/ | grep -v '^$'

# 4. Run the executable gate (does 1 + 2 for you).
bash modex/verify.sh

# 5. REQUIRED for real tamper-proofing: check the latest root hash against the
#    external anchor — see "How to make it truly tamper-proof" below.
```

## How to add a new certification

1. Compute `sha256` of the artifact: `shasum -a 256 <file>`.
2. Compute the FDE Assurance Score using the formula: `25*claim + 25*contradiction + 30*evidence + 20*antipatterns`.
3. Copy the latest entry as a template, replace fields, set `prev_hash` to the SHA-256 of the previous entry.
4. Update `registry/index.json` (machine-readable index).
5. `git add registry/ && git commit -m "cert(<claim>): trust_score=N, sha256=<prefix>..."`.
6. Push to GitHub — the public `marketing/landing/trust.html` will display the new entry automatically.

## FDE Assurance Score formula

```
FDE Assurance Score = round(
    25 * (Claim present and falsifiable)
  + 25 * (At least 3 failure modes documented)
  + 30 * (Evidence trail contains ≥1 file/command/test)
  + 20 * (Anti-patterns check passed)
)
```

- ≥85 → Certified → Ship
- 60-84 → Needs revision
- <60 → Rejected → Return to Stage 1

## Schema

```json
{
  "schema": "fde-registry-entry-v1",
  "cert_id": "<YYYY-MM-DD>-<claim-slug>-<score>",
  "case_study_path": "<repo-relative path>",
  "trust_score": <int 0-100>,
  "sha256": "<64 hex chars>",
  "prev_hash": "<64 hex chars> or null for genesis>",
  "certified_at": "<ISO 8601 UTC>",
  "certifier_id": "fde-consultants-protocoles",
  "claim": "<one-sentence falsifiable claim>",
  "evidence_trail": ["file:line", ...],
  "falsification_modes_documented": <int>
}
```

## Trust model (what this proves — and what it does NOT)

Be precise about the guarantee. "Tamper-proof" is easy to overclaim, and DeepSCR forbids overclaiming.

**What the hash-chain DOES give you:**
- *Integrity against accidental corruption* — alter any committed entry and its `shasum` stops matching `index.json` and the `prev_hash` linkage breaks.
- *Detection by a third party who already witnessed a root* — anyone who recorded a previous head `sha256` (or a signed git commit) can prove the log changed after that point.

**What it does NOT give you (the honest limit):**
- It does **not** protect against the **registry operator**. Whoever controls this repo can edit an old entry, recompute *every* downstream hash, rewrite `index.json`, and `git push --force` — producing a perfectly self-consistent chain with no internal evidence of tampering. A self-contained hash chain is only as trustworthy as the party holding it. (Cf. Russ Cox, *Transparent Logs for Skeptical Clients*; RFC 6962 Certificate Transparency, which solves exactly this with external witnesses.)

So: **"verifiable with `shasum`, no external service" = tamper-*evidence relative to a witnessed root*, not tamper-*proofing against the operator*.**

## How to make it truly tamper-proof (external anchor)

To earn the word "tamper-proof", anchor the head hash to an independent witness — any one of:
- **Sigstore Rekor** — append the head `sha256` to the public transparency log, or sign releases with `cosign`.
- **RFC 3161 timestamp** or an **OpenTimestamps** proof committed alongside `index.json`.
- **Signed git tags** (`git tag -s registry-vN`) so history is cryptographically attributable and a force-push is detectable by anyone holding the tag.
- Periodically publish the head hash somewhere outside your control (a dated public post, a second org's repo).

Until one of these is wired in, this README and any `trust.html` must say **"publicly auditable certification log"**, not **"tamper-proof"**.

## Why not "blockchain"?

We keep the *useful* properties (hash-chain linkage, append-only intent, offline `shasum` checks) and lean on Git for distribution + history — without mining/gas/consensus/wallets. The trade-off (above) is that Git + `shasum` alone don't defend against the operator; a single external anchor closes that gap far more cheaply than a blockchain would.
