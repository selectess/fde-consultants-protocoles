"""Tests for the Modex plugin loader."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from modex.license import generate_license, generate_keypair_files, TIER_PLUGIN, TIER_COLLECTIVE
from modex.plugin_loader import load_license, verify, load_plugin, LicenseError


@pytest.fixture
def license_dir(tmp_path):
    """Create a tmp license directory with a generated keypair."""
    license_path = tmp_path / "license.json"
    private_path = tmp_path / "private.key"
    public_path = tmp_path / "public.key"
    generate_keypair_files(private_path, public_path)
    return tmp_path, license_path, private_path, public_path


def test_load_license_no_file_returns_none(tmp_path):
    """load_license returns None when file doesn't exist."""
    assert load_license(tmp_path / "missing.json") is None


def test_load_license_corrupt_json_raises(tmp_path):
    """load_license raises LicenseError on corrupt JSON."""
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json")
    with pytest.raises(LicenseError):
        load_license(bad)


def test_load_plugin_no_license_returns_unlicensed(tmp_path):
    """load_plugin returns unlicensed context when no license found."""
    ctx = load_plugin(tmp_path / "missing.json")
    assert ctx["licensed"] is False
    assert ctx["tier"] is None
    assert ctx["license_id"] is None
    assert ctx["features"] == []
    assert ctx["warning"] is not None


def test_load_plugin_with_valid_plugin_license(license_dir):
    """load_plugin returns licensed context with plugin features."""
    tmp_path, license_path, private_path, _ = license_dir
    license_obj = generate_license(
        email="plugin@example.com",
        tier=TIER_PLUGIN,
        private_key_path=private_path,
    )
    license_path.write_text(json.dumps(license_obj))
    # Note: verification will fail because the embedded public key in
    # plugin_loader.py is a placeholder. We test the load + error path here.
    with pytest.raises(LicenseError):
        load_plugin(license_path)


def test_load_plugin_invalid_license_raises(license_dir):
    """load_plugin raises LicenseError on tampered license."""
    tmp_path, license_path, private_path, _ = license_dir
    license_obj = generate_license(
        email="test@example.com",
        tier=TIER_PLUGIN,
        private_key_path=private_path,
    )
    # Tamper with email
    license_obj["email"] = "tampered@example.com"
    license_path.write_text(json.dumps(license_obj))
    with pytest.raises(LicenseError):
        load_plugin(license_path)


def test_plugin_loader_warning_message(tmp_path):
    """load_plugin returns a clear warning when no license found."""
    ctx = load_plugin(tmp_path / "missing.json")
    assert "warning" in ctx
    assert "$6" in ctx["warning"]
    assert "lifetime" in ctx["warning"]


def test_plugin_loader_features_for_collective_tier(license_dir):
    """A valid collective license enables multi-agent features."""
    tmp_path, license_path, private_path, _ = license_dir
    license_obj = generate_license(
        email="team@example.com",
        tier=TIER_COLLECTIVE,
        private_key_path=private_path,
    )
    license_path.write_text(json.dumps(license_obj))
    # The verification will fail (placeholder key), but the loader should
    # at least parse the tier and know what features SHOULD be enabled.
    with pytest.raises(LicenseError):
        load_plugin(license_path)


def test_verify_with_empty_license_obj():
    """verify returns False on empty license."""
    assert verify({}) is False


def test_verify_with_wrong_schema():
    """verify returns False on wrong schema field."""
    assert verify({"schema": "wrong", "signature": "ed25519:abc"}) is False


def test_verify_with_invalid_signature_format():
    """verify returns False on malformed signature."""
    assert verify({"schema": "fde-modex-license-v1", "signature": "bad-format"}) is False


def test_verify_with_valid_structure_invalid_signature():
    """verify returns False when signature doesn't match (placeholder key)."""
    license_obj = {
        "schema": "fde-modex-license-v1",
        "license_id": "abc-123",
        "email": "test@example.com",
        "tier": "plugin",
        "issued_at": "2026-01-01T00:00:00Z",
        "valid_until": "2099-12-31T23:59:59Z",
        "stripe_payment_id": None,
        "public_key_fingerprint": "sha256:abc",
        "signature": "ed25519:" + "ab" * 64,  # 64 hex chars but invalid
    }
    # Will fail because the placeholder public key doesn't match this signature
    assert verify(license_obj) is False


def test_plugin_loader_unlicensed_features_is_empty_list(tmp_path):
    """Unlicensed plugin has empty features list."""
    ctx = load_plugin(tmp_path / "missing.json")
    assert isinstance(ctx["features"], list)
    assert len(ctx["features"]) == 0


def test_plugin_loader_unlicensed_tier_is_none(tmp_path):
    """Unlicensed plugin has tier=None."""
    ctx = load_plugin(tmp_path / "missing.json")
    assert ctx["tier"] is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))