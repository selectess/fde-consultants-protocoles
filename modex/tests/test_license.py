"""Tests for the Modex license system (ed25519)."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from modex.license import (
    SCHEMA,
    TIER_PLUGIN,
    TIER_COLLECTIVE,
    VALID_UNTIL,
    generate_license,
    verify_license,
    generate_keypair_files,
    _generate_keypair,
)


# Skip all tests if cryptography is not installed
cryptography = pytest.importorskip("cryptography")


@pytest.fixture
def keypair_files(tmp_path):
    """Generate a fresh keypair in tmp_path for testing."""
    private_path = tmp_path / "test_private.key"
    public_path = tmp_path / "test_public.key"
    generate_keypair_files(private_path, public_path)
    return private_path, public_path


def test_generate_license_returns_valid_dict(keypair_files):
    """generate_license returns a dict with all required fields."""
    private_path, _ = keypair_files
    license_obj = generate_license(
        email="test@example.com",
        tier=TIER_PLUGIN,
        stripe_payment_id="pi_test_123",
        private_key_path=private_path,
    )
    assert isinstance(license_obj, dict)
    assert license_obj["schema"] == SCHEMA
    assert license_obj["tier"] == TIER_PLUGIN
    assert license_obj["email"] == "test@example.com"
    assert license_obj["stripe_payment_id"] == "pi_test_123"
    assert license_obj["valid_until"] == VALID_UNTIL
    assert "license_id" in license_obj
    assert "issued_at" in license_obj
    assert license_obj["signature"].startswith("ed25519:")


def test_generate_license_validates_email():
    """generate_license raises ValueError on invalid email."""
    private_bytes, _ = _generate_keypair()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(private_bytes)
        private_path = f.name
    try:
        with pytest.raises(ValueError, match="Invalid email"):
            generate_license(email="not-an-email", private_key_path=private_path)
        with pytest.raises(ValueError, match="Invalid email"):
            generate_license(email="", private_key_path=private_path)
    finally:
        Path(private_path).unlink()


def test_generate_license_validates_tier():
    """generate_license raises ValueError on invalid tier."""
    private_bytes, _ = _generate_keypair()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(private_bytes)
        private_path = f.name
    try:
        with pytest.raises(ValueError, match="Invalid tier"):
            generate_license(email="test@example.com", tier="invalid", private_key_path=private_path)
    finally:
        Path(private_path).unlink()


def test_round_trip_license(keypair_files):
    """License generated then verified with same keypair returns True."""
    private_path, public_path = keypair_files
    license_obj = generate_license(
        email="alice@example.com", tier=TIER_PLUGIN, private_key_path=private_path,
    )
    public_key = public_path.read_bytes()
    assert verify_license(license_obj, public_key) is True


def test_tampered_license_fails_verification(keypair_files):
    """Modifying the license email breaks the signature."""
    private_path, public_path = keypair_files
    license_obj = generate_license(
        email="alice@example.com", tier=TIER_PLUGIN, private_key_path=private_path,
    )
    public_key = public_path.read_bytes()
    # Tamper with the email
    license_obj["email"] = "hacker@example.com"
    assert verify_license(license_obj, public_key) is False


def test_wrong_public_key_fails_verification(keypair_files, tmp_path):
    """Verifying with a different public key returns False."""
    private_path, _ = keypair_files
    license_obj = generate_license(
        email="alice@example.com", tier=TIER_PLUGIN, private_key_path=private_path,
    )
    # Generate a DIFFERENT keypair
    other_private = tmp_path / "other_private.key"
    other_public = tmp_path / "other_public.key"
    generate_keypair_files(other_private, other_public)
    wrong_public = other_public.read_bytes()
    assert verify_license(license_obj, wrong_public) is False


def test_invalid_license_schema_fails():
    """A license with wrong schema field fails verification."""
    private_bytes, public_bytes = _generate_keypair()
    license_obj = {
        "schema": "wrong-schema",
        "email": "test@example.com",
        "tier": TIER_PLUGIN,
        "license_id": "abc",
        "issued_at": "2026-01-01T00:00:00Z",
        "valid_until": VALID_UNTIL,
        "stripe_payment_id": None,
        "public_key_fingerprint": "sha256:abc",
        "signature": "ed25519:abcd",
    }
    assert verify_license(license_obj, public_bytes) is False


def test_invalid_signature_format_fails():
    """A license with malformed signature fails verification."""
    private_bytes, public_bytes = _generate_keypair()
    license_obj = {
        "schema": SCHEMA,
        "email": "test@example.com",
        "tier": TIER_PLUGIN,
        "license_id": "abc",
        "issued_at": "2026-01-01T00:00:00Z",
        "valid_until": VALID_UNTIL,
        "stripe_payment_id": None,
        "public_key_fingerprint": "sha256:abc",
        "signature": "not-a-valid-signature-format",
    }
    assert verify_license(license_obj, public_bytes) is False


def test_collective_tier_supported(keypair_files):
    """License can be generated for collective tier."""
    private_path, public_path = keypair_files
    license_obj = generate_license(
        email="team@example.com", tier=TIER_COLLECTIVE, private_key_path=private_path,
    )
    assert license_obj["tier"] == TIER_COLLECTIVE
    public_key = public_path.read_bytes()
    assert verify_license(license_obj, public_key) is True


def test_license_id_is_unique_across_generations(keypair_files):
    """Two licenses have different license_ids."""
    private_path, _ = keypair_files
    lic1 = generate_license(email="a@example.com", private_key_path=private_path)
    lic2 = generate_license(email="b@example.com", private_key_path=private_path)
    assert lic1["license_id"] != lic2["license_id"]


def test_license_persists_to_disk(keypair_files, tmp_path):
    """License can be written to and read from disk."""
    private_path, public_path = keypair_files
    license_obj = generate_license(
        email="persist@example.com", tier=TIER_PLUGIN, private_key_path=private_path,
    )
    # Write to disk
    license_file = tmp_path / "license.json"
    license_file.write_text(json.dumps(license_obj, indent=2))
    # Read back
    loaded = json.loads(license_file.read_text())
    # Verify still works
    assert verify_license(loaded, public_path.read_bytes()) is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))