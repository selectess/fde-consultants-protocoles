# FDE Modex Plugin — License System

> **License model**: ed25519-signed JSON license per customer + Stripe webhook + offline grace period.

This document is the public, auditable specification of the Modex Plugin license system.
Every component is reproducible from this spec alone.

## 1. License File Format

A license file (`license.json`) is a JSON document:

```json
{
  "license_id": "uuid-v4-string",
  "schema": "fde-modex-license-v1",
  "issued_at": "2026-06-23T19:11:00Z",
  "expires_at": "2099-12-31T23:59:59Z",
  "customer_email": "user@example.com",
  "public_key_id": "fde-modex-2026",
  "features": ["lead", "researcher", "builder", "certifier"],
  "max_agents": 4,
  "offline_grace_days": 7,
  "signature": "<ed25519 signature of all fields above>"
}
```

## 2. Cryptographic Identity

- **Algorithm**: ed25519 (RFC 8032)
- **Public key**: stored in `modex/license.py` as `EMBEDDED_PUBLIC_KEY_HEX`
- **Private key**: kept offline on a HSM or dedicated signing machine (not in repo)
- **Signing payload**: canonical JSON of all fields except `signature`

## 3. Issuance Flow

```
1. Customer purchases on Stripe ($6 lifetime)
2. Stripe webhook -> modex/stripe_webhook.py
3. Webhook creates a license_id, fetches customer_email
4. modex/license.py signs the license JSON with ed25519
5. License emailed + downloadable from account page
6. Customer saves license.json to ~/.fde-modex/license.json
```

## 4. Verification Flow

```
1. Plugin loads (modex/plugin_loader.py:load_plugin)
2. Reads license.json from ~/.fde-modex/license.json
3. Validates:
   a. JSON schema (required fields present)
   b. expires_at > now
   c. ed25519 signature against EMBEDDED_PUBLIC_KEY_HEX
   d. license_id not in revocation_list.json
4. If offline > offline_grace_days, requires re-verification
5. On success, exposes 4 features to the runtime
```

## 5. Revocation List

`~/.fde-modex/revocation_list.json` (fetched on online verification):

```json
{
  "schema": "fde-modex-revocation-v1",
  "fetched_at": "2026-06-23T19:11:00Z",
  "revoked_license_ids": ["uuid-1", "uuid-2"],
  "signature": "<ed25519>"
}
```

## 6. Offline Grace Period

- A license that was verified online within the last N days works offline.
- Default N = 7 days.
- After N days offline, plugin requires a re-verification (HTTPS call to modex.dev/verify).
- The customer can extend N to 30 days for $2/month (optional).

## 7. Failure Modes

| Failure | Behavior |
|---|---|
| No license file found | Open-source fallback: Modex runs with 1 agent (Lead only) |
| License expired | Open-source fallback |
| Signature invalid | Reject load, log error, suggest re-download |
| Revoked | Reject load, show contact email |
| Offline > grace days | Show countdown, require online check within N hours |
| Clock skew > 24h | Fail safe (refuse activation) |

## 8. Privacy

- We store: email, license_id, Stripe customer_id, public_key_id
- We do NOT store: agent outputs, file contents, conversation logs
- GDPR-compliant: customer can request full deletion via email

## 9. Audit

Every license issuance and verification is logged server-side (optional).

## 10. Self-Test

```bash
# Generate a test license (requires MODEX_PRIVATE_KEY_HEX env var)
python3 -m modex.license generate --email test@example.com --output /tmp/test.json

# Verify a license
python3 -m modex.license verify --license /tmp/test.json --public-key $(python3 -c "from modex.license import EMBEDDED_PUBLIC_KEY_HEX; print(EMBEDDED_PUBLIC_KEY_HEX)")

# Self-test the entire flow
python3 -m pytest modex/tests/test_license.py -v
```

## 11. Roadmap (next 90 days)

- [ ] Hardware binding (optional, opt-in)
- [ ] Per-license revocation API (REST endpoint)
- [ ] Stripe customer portal integration
- [ ] Multi-device license transfer (1 transfer per 30 days)
- [ ] Tiered licenses: Personal / Team / Enterprise

---

Last updated: 2026-06-23
License system version: v1
Contact: security@selectess.dev
