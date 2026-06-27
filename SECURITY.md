# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | Active             |
| < 1.0   | End of life        |

## Reporting a Vulnerability

**Please do not file a public GitHub issue for security vulnerabilities.**

Email `security@selectess.dev` or open a private security advisory at
<https://github.com/selectess/fde-consultants-protocoles/security/advisories/new>

We aim to acknowledge within **48 hours** and patch within **14 days** for
critical issues, **30 days** for high-severity.

## FDE Assurance Score Integrity

The FDE Assurance Score for every certified deliverable in `registry/` is computed
from the SHA-256 hash of the underlying file. If you find a FDE Assurance Score entry
whose `sha256` does not match `shasum -a 256 <file>`, that is a **trust
compromise** and should be reported as critical.

## Cryptographic Material

- `modex/license.py` uses **ed25519** for license signature verification.
- The `EMBEDDED_PUBLIC_KEY_HEX` placeholder is for development/testing.
- Production deployments **must rotate the public key** before issuing licenses.

See [`modex/LICENSE-SYSTEM.md`](modex/LICENSE-SYSTEM.md) for the full
ed25519 license mechanism (issuance, verification, revocation, offline grace).

## Secrets Policy (HARD RULE)

**No real credentials are ever committed to this repository.**

The CI pipeline (`/.github/workflows/test.yml`) **automatically rejects** PRs
that contain:
- `ghp_*` / `gho_*` / `ghs_*` / `ghr_*` / `ghu_*` (GitHub tokens)
- `sk-*` / `sk_*` with 20+ chars (real API keys, not `sk_test_*` / `sk_example_*`)
- `.env` files (only `.env.example` is allowed)
- `password = "..."` literals

If a secret is **accidentally** pushed:
1. **Revoke the credential immediately** at the source (GitHub, Stripe, etc.)
2. **Generate a new credential** following the platform's rotation policy
3. **Purge the history** with `git filter-repo` or `BFG Repo-Cleaner`
4. **Force-push** the cleaned history
5. **Notify** `security@selectess.dev` and any affected users

## License File Security

Customer `license.json` files contain PII (email, license_id, public_key). **Never commit them**:

- Use a private object store (S3, GCS, Azure Blob)
- Or distribute via signed download URLs (1-hour expiry)
- Or email as attachment (PGP-encrypted)

## MCP Server Beta Limitations (Out of Scope)

The `mcp-server/` Beta is **for local development only**:
- Localhost-only CORS
- Fail-closed admin keys (env var, never hardcoded)
- Mock Stripe (use real Stripe API key only in production env)
- No persistence (SQLite, in-memory)
- No rate limiting (use Cloudflare/AWS WAF in production)

## Architecture Security

- All Python code in `skill/` and `modex/` uses **stdlib only** (zero external deps)
- MCP tools are **stdio transport** only (no HTTP exposure)
- Skills ship with **checksums** via SHA-256 chain in `registry/`
- Independent Certifier re-derives FDE Assurance Score from raw evidence (no self-attestation)

## Audit

- Internal security review: every commit
- External audit: planned for V1.2 (post first customer)
- Bug bounty: planned for V1.2 (post $10K MRR)

## Contact

- **Email**: `security@selectess.dev`
- **PGP key**: TODO (will be published before V1.2)
- **GitHub Security Advisories**: <https://github.com/selectess/fde-consultants-protocoles/security/advisories/new>

---

<sub>This document follows the [GitHub Security Advisories spec](https://docs.github.com/en/code-security/security-advisories).</sub>
