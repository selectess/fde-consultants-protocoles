#!/usr/bin/env python3
"""Modex Plugin Loader.

Loads the Modex runtime ONLY if a valid license is present.
Without a license: open-source fallback (1-agent local only, no commercial features).

Workflow:
1. Look for license at ~/.fde-modex/license.json (default)
2. If found, verify with embedded public key
3. If valid: enable commercial features (collective tier)
4. If invalid: refuse to load, print error message

Public key is EMBEDDED here for offline verification (no network calls).
In production, this would be a different public key per release.
"""
import json
import sys
from pathlib import Path
from typing import Optional

# The embedded public key (32 bytes raw, hex-encoded = 64 chars) for license
# verification. The matching private key lives at modex/.keys/modex_private.key
# (gitignored via `*.key`). For production hardening, move the private key into
# 1Password / an HSM, regenerate via `python3 modex/license.py keygen`, re-embed
# the new public key here, and rotate yearly.
EMBEDDED_PUBLIC_KEY_HEX = (
    "5c4b362043f71f5c48325795b7e5d8e91f0fdbb425a51df240588847327dcd8d"
)

# Optional: ed25519 verification
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    ED25519_AVAILABLE = True
except ImportError:
    ED25519_AVAILABLE = False


DEFAULT_LICENSE_PATH = Path.home() / ".fde-modex" / "license.json"


class LicenseError(Exception):
    """Raised when the plugin license is missing or invalid."""


def load_license(license_path: Optional[Path] = None) -> Optional[dict]:
    """Load the plugin license from disk.

    Args:
        license_path: Optional override path. Defaults to ~/.fde-modex/license.json.

    Returns:
        License dict if found, None if not found (which is OK for open-source fallback).
    """
    path = Path(license_path) if license_path else DEFAULT_LICENSE_PATH
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        raise LicenseError(f"Failed to read license at {path}: {e}")


def verify(license_obj: dict) -> bool:
    """Verify the license signature using the embedded public key.

    Args:
        license_obj: License dict from load_license().

    Returns:
        True if license is valid, False otherwise.
    """
    if not ED25519_AVAILABLE:
        return False
    try:
        public_key_bytes = bytes.fromhex(EMBEDDED_PUBLIC_KEY_HEX)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signature_field = license_obj.get("signature", "")
        if not signature_field.startswith("ed25519:"):
            return False
        signature = bytes.fromhex(signature_field.split(":", 1)[1])
        # Reconstruct the canonical message WITHOUT the signature field
        license_copy = {k: v for k, v in license_obj.items() if k != "signature"}
        message = json.dumps(license_copy, sort_keys=True).encode("utf-8")
        public_key.verify(signature, message)
        # Check tier
        tier = license_obj.get("tier")
        return tier in ("plugin", "collective")
    except Exception:
        return False


def load_plugin(license_path: Optional[Path] = None) -> dict:
    """Load the Modex plugin.

    Returns a context dict with:
        - "licensed": bool (True if a valid license is present)
        - "tier": str ("plugin" | "collective" | None)
        - "license_id": str | None
        - "email": str | None
        - "features": list[str] (available commercial features)

    Raises LicenseError if a license file exists but is invalid.
    """
    license_obj = load_license(license_path)
    if license_obj is None:
        # Open-source fallback
        return {
            "licensed": False,
            "tier": None,
            "license_id": None,
            "email": None,
            "features": [],
            "warning": (
                "No license found. Running in open-source mode. "
                "Get a $6 lifetime license (see modex/PRICING.md)."
            ),
        }
    if not verify(license_obj):
        raise LicenseError(
            f"License file found but signature is invalid. "
            f"Please check ~/.fde-modex/license.json or contact support@fde-consultant.com"
        )
    tier = license_obj.get("tier")
    features = []
    if tier == "plugin":
        features = ["trust_score_audit", "registry_access", "priority_support"]
    elif tier == "collective":
        features = [
            "trust_score_audit",
            "registry_access",
            "priority_support",
            "multi_agent_orchestration",
            "shared_memory",
        ]
    return {
        "licensed": True,
        "tier": tier,
        "license_id": license_obj.get("license_id"),
        "email": license_obj.get("email"),
        "features": features,
        "warning": None,
    }


def main():
    """CLI: check license status."""
    import argparse
    parser = argparse.ArgumentParser(description="Modex plugin loader")
    parser.add_argument("--check", action="store_true", help="Check license status")
    parser.add_argument("--license-path", default=None)
    args = parser.parse_args()
    try:
        ctx = load_plugin(Path(args.license_path) if args.license_path else None)
        if ctx["licensed"]:
            print(f"✓ Licensed ({ctx['tier']})")
            print(f"  License ID: {ctx['license_id']}")
            print(f"  Email: {ctx['email']}")
            print(f"  Features: {', '.join(ctx['features']) or '(none)'}")
        else:
            print("✗ No license found (open-source mode)")
            if ctx.get("warning"):
                print(f"  {ctx['warning']}")
    except LicenseError as e:
        print(f"✗ License error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()