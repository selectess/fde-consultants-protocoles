# FDE Modex Plugin — License System

> **Model**: one ed25519-signed `license.json` per customer, verified **fully offline** against a public key embedded in the plugin. No phone-home, no revocation server, no expiry.

This is the public, auditable specification of the Modex license system. It describes exactly what the shipped code does — `modex/license.py`, `modex/plugin_loader.py`, `modex/polar_webhook.py`, `modex/fulfillment.py` — and nothing it does not.

## 1. License file format

A license (`license.json`) is the JSON produced by `modex/license.py:generate_license`:

```json
{
  "schema": "fde-modex-license-v1",
  "license_id": "uuid-v4",
  "email": "user@example.com",
  "tier": "plugin",                          // "plugin" ($6) | "collective" ($260)
  "issued_at": "2026-06-29T19:11:00Z",
  "valid_until": "2099-12-31T23:59:59Z",     // lifetime
  "stripe_payment_id": "polar_ord_...",      // purchase reference
  "public_key_fingerprint": "sha256:...",
  "signature": "ed25519:<hex>"               // signature of the canonical JSON of all other fields
}
```

## 2. Cryptographic identity

- **Algorithm**: ed25519 (RFC 8032).
- **Public key**: embedded in `modex/plugin_loader.py` as `EMBEDDED_PUBLIC_KEY_HEX` — shipped with the plugin; it can only *verify*.
- **Private key**: held by the issuer only (production: 1Password / HSM; never in the repo). It can only *sign*. Anyone can verify; only the issuer can mint.
- **Signed payload**: the canonical JSON (sorted keys) of every field except `signature`. Changing any field invalidates the signature.

## 3. Issuance — on a paid order

```
1. Customer buys on Polar ($6 plugin / $260 collective).
2. Polar fires a signed webhook -> modex/polar_webhook.py (signature verified, fail-closed).
3. modex/license.py:generate_license mints + ed25519-signs license.json for the tier.
4. modex/fulfillment.py persists it to an append-only ledger (audit), emails it, and is
   idempotent on the order id — a retried webhook returns the same license, never a new one.
```

A Stripe reference handler, `modex/stripe_webhook.py`, follows the same path.

## 4. Verification & activation — offline

```
1. Plugin loads: modex/plugin_loader.py:load_plugin
2. Reads ~/.fde-modex/license.json (an override path is supported)
3. Verifies the ed25519 signature against EMBEDDED_PUBLIC_KEY_HEX and checks tier ∈ {plugin, collective}
4. Valid   -> unlocks the tier's features
   Missing -> open-source fallback (licensed:false, no commercial features; the full Skill still runs)
   Invalid -> raises LicenseError (tampered, or signed by the wrong key)
```

There is **no network call, no expiry check, and no revocation list** — verification is fully offline by design.

## 5. Tiers & features

| Tier | Price | Features unlocked |
|---|---|---|
| *(none)* | free | open-source mode — the whole Skill, no commercial features |
| `plugin` | $6 lifetime | `trust_score_audit` · `registry_access` · `priority_support` |
| `collective` | $260 lifetime | the above + `multi_agent_orchestration` · `shared_memory` |

## 6. Security model & honest limits

ed25519 proves **authenticity** (only the issuer could have minted it) and **integrity** (no field was altered) — a buyer cannot self-upgrade `plugin` → `collective`, because editing the tier breaks the signature. It does **not** prove non-duplication: a license file can be copied or shared. Anti-sharing (email / machine binding, online activation) is a separate layer that is deliberately **not** shipped — it is not needed to sell, and would only be added if abuse appears. There is no revocation server and no grace period; once issued, a license is valid for life.

## 7. Self-test

```bash
# mint a test license with the issuer key, verify it, and run the suite
python3 -m modex.license generate --email test@example.com --tier plugin \
        --private-key modex/.keys/modex_private.key --output /tmp/test.json
python3 -m modex.license verify --license-file /tmp/test.json \
        --public-key modex/.keys/modex_public.key
python3 -m pytest modex/tests/test_license.py -q
```

## 8. End-user activation

Buyer-facing activation — place `license.json` at `~/.fde-modex/license.json`, verify, what it unlocks — is documented at **`/activate.html`** on the site.

---

Last updated: 2026-06-29 · License system version: v1 · *This spec matches the shipped code.*
