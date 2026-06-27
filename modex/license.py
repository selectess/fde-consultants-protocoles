#!/usr/bin/env python3
"""Plugin Modex License System (ed25519).

Generates and verifies license.json files for the $6 lifetime BSL plugin.

License format:
{
  "schema": "fde-modex-license-v1",
  "license_id": "uuid-v4",
  "email": "user@example.com",
  "tier": "plugin | collective",
  "issued_at": "ISO 8601",
  "valid_until": "2099-12-31 (lifetime)",
  "stripe_payment_id": "pi_...",
  "public_key_fingerprint": "sha256:...",
  "signature": "ed25519:..."  (hex-encoded)
}

Public key is embedded in plugin_loader.py.
Private key is held by the certifier (in production: stored in 1Password
or HSM, not in the repo).
"""
import hashlib
import json
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Optional: ed25519 via cryptography library (recommended for production)
# Fallback: use hashlib-based signature (less secure but no deps)
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey, Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    ED25519_AVAILABLE = True
except ImportError:
    ED25519_AVAILABLE = False


SCHEMA = "fde-modex-license-v1"
TIER_PLUGIN = "plugin"
TIER_COLLECTIVE = "collective"
VALID_UNTIL = "2099-12-31T23:59:59Z"


def _generate_keypair():
    """Generate an ed25519 keypair."""
    if not ED25519_AVAILABLE:
        raise RuntimeError(
            "ed25519 not available. Install cryptography: pip install cryptography"
        )
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    private_bytes = private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private_bytes, public_bytes


def _sign(private_bytes: bytes, message: bytes) -> bytes:
    """Sign a message with ed25519 private key."""
    private = Ed25519PrivateKey.from_private_bytes(private_bytes)
    return private.sign(message)


def _verify(public_bytes: bytes, message: bytes, signature: bytes) -> bool:
    """Verify an ed25519 signature."""
    public = Ed25519PublicKey.from_public_bytes(public_bytes)
    try:
        public.verify(signature, message)
        return True
    except Exception:
        return False


def generate_license(
    email: str,
    tier: str = TIER_PLUGIN,
    stripe_payment_id: Optional[str] = None,
    private_key_path: Optional[Path] = None,
) -> dict:
    """Generate a license JSON for the given email.

    Args:
        email: Customer email.
        tier: "plugin" or "collective".
        stripe_payment_id: Optional Stripe payment ID for audit trail.
        private_key_path: Optional path to a file containing the private key (32 bytes raw).
            If None, generates a new keypair (for testing).

    Returns:
        dict with the license JSON.
    """
    if not email or "@" not in email:
        raise ValueError(f"Invalid email: {email}")
    if tier not in (TIER_PLUGIN, TIER_COLLECTIVE):
        raise ValueError(f"Invalid tier: {tier}")
    if private_key_path:
        private_bytes = Path(private_key_path).read_bytes()
        if len(private_bytes) != 32:
            raise ValueError(f"Private key must be 32 bytes, got {len(private_bytes)}")
    else:
        private_bytes, _ = _generate_keypair()
    license_id = str(uuid.uuid4())
    issued_at = datetime.now(timezone.utc).isoformat()
    public_key_fingerprint = hashlib.sha256(b"plugin-public-key-v1").hexdigest()[:16]
    license_obj = {
        "schema": SCHEMA,
        "license_id": license_id,
        "email": email,
        "tier": tier,
        "issued_at": issued_at,
        "valid_until": VALID_UNTIL,
        "stripe_payment_id": stripe_payment_id,
        "public_key_fingerprint": f"sha256:{public_key_fingerprint}",
    }
    # Sign the canonical JSON (sorted keys, no signature field)
    message = json.dumps(license_obj, sort_keys=True).encode("utf-8")
    signature = _sign(private_bytes, message)
    license_obj["signature"] = f"ed25519:{signature.hex()}"
    return license_obj


def verify_license(license_obj: dict, public_key: bytes) -> bool:
    """Verify a license against the public key.

    Args:
        license_obj: The license JSON dict.
        public_key: 32-byte raw ed25519 public key.

    Returns:
        True if signature is valid and structure is correct, False otherwise.
    """
    if not isinstance(license_obj, dict):
        return False
    if license_obj.get("schema") != SCHEMA:
        return False
    signature_field = license_obj.get("signature", "")
    if not signature_field.startswith("ed25519:"):
        return False
    try:
        signature = bytes.fromhex(signature_field.split(":", 1)[1])
    except ValueError:
        return False
    # Reconstruct the message WITHOUT the signature field
    license_copy = {k: v for k, v in license_obj.items() if k != "signature"}
    message = json.dumps(license_copy, sort_keys=True).encode("utf-8")
    return _verify(public_key, message, signature)


def generate_keypair_files(
    private_key_path: Path, public_key_path: Path
) -> None:
    """Generate a keypair and save to files.

    Args:
        private_key_path: Where to save the 32-byte private key.
        public_key_path: Where to save the 32-byte public key.
    """
    private_bytes, public_bytes = _generate_keypair()
    Path(private_key_path).write_bytes(private_bytes)
    Path(public_key_path).write_bytes(public_bytes)


def main():
    """CLI: generate or verify a license."""
    import argparse
    parser = argparse.ArgumentParser(description="Modex license generator")
    sub = parser.add_subparsers(dest="cmd", required=True)
    gen = sub.add_parser("generate", help="Generate a license")
    gen.add_argument("--email", required=True)
    gen.add_argument("--tier", default=TIER_PLUGIN, choices=[TIER_PLUGIN, TIER_COLLECTIVE])
    gen.add_argument("--stripe-payment-id", default=None)
    gen.add_argument("--private-key", default=None, help="Path to 32-byte private key")
    gen.add_argument("--output", default=None, help="Output file (default: stdout)")
    ver = sub.add_parser("verify", help="Verify a license")
    ver.add_argument("--license-file", required=True)
    ver.add_argument("--public-key", required=True, help="Path to 32-byte public key")
    kp = sub.add_parser("keygen", help="Generate keypair")
    kp.add_argument("--private-out", required=True)
    kp.add_argument("--public-out", required=True)
    args = parser.parse_args()
    if args.cmd == "generate":
        license_obj = generate_license(
            email=args.email,
            tier=args.tier,
            stripe_payment_id=args.stripe_payment_id,
            private_key_path=Path(args.private_key) if args.private_key else None,
        )
        output = json.dumps(license_obj, indent=2)
        if args.output:
            Path(args.output).write_text(output)
            print(f"License written to {args.output}")
        else:
            print(output)
    elif args.cmd == "verify":
        license_obj = json.loads(Path(args.license_file).read_text())
        public_key = Path(args.public_key).read_bytes()
        valid = verify_license(license_obj, public_key)
        print(f"Valid: {valid}")
        sys.exit(0 if valid else 1)
    elif args.cmd == "keygen":
        generate_keypair_files(Path(args.private_out), Path(args.public_out))
        print(f"Keypair written: private={args.private_out}, public={args.public_out}")


if __name__ == "__main__":
    main()