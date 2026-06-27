"""Tests for the independent Certifier (modex/certify_skill.py)."""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def test_certify_skill_returns_100_for_local_skill():
    """Certify the local FDE Skill and assert Trust Score >=85."""
    from modex.certify_skill import certify_skill
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        out_path = f.name
    try:
        cert = certify_skill(REPO_ROOT / "skill", Path(out_path))
        score = cert["trust_score"]["trust_score"]
        verdict = cert["trust_score"]["verdict"]
        assert score >= 85, f"Trust Score {score} should be >=85 (Certified)"
        assert verdict == "certified"
        # Independent certification marker
        assert cert["independent_of_lead"] is True
        # All 4 components present
        assert cert["components_checked"]["claim_present"] is True
        assert cert["components_checked"]["has_3_failure_modes"] is True
        assert cert["components_checked"]["has_evidence_trail"] is True
        assert cert["components_checked"]["antipatterns_clean"] is True
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_certify_skill_produces_valid_json():
    """The certification JSON is valid and has required fields."""
    from modex.certify_skill import certify_skill
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        out_path = f.name
    try:
        cert = certify_skill(REPO_ROOT / "skill", Path(out_path))
        # Required fields
        assert cert["schema"] == "fde-skill-certification-v1"
        assert "trust_score" in cert
        assert "components_checked" in cert
        assert "evidence_references" in cert
        assert "certified_at" in cert
        # File written successfully
        loaded = json.loads(Path(out_path).read_text())
        assert loaded == cert
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_certify_skill_includes_sha256():
    """The certification includes the SHA-256 of SKILL.md."""
    from modex.certify_skill import certify_skill
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        out_path = f.name
    try:
        cert = certify_skill(REPO_ROOT / "skill", Path(out_path))
        assert "skill_md_sha256" in cert
        sha = cert["skill_md_sha256"]
        # SHA-256 should be 64 hex chars
        assert len(sha) == 64
        # Should match actual SHA of SKILL.md
        import hashlib
        expected = hashlib.sha256((REPO_ROOT / "skill" / "SKILL.md").read_bytes()).hexdigest()
        assert sha == expected
    finally:
        Path(out_path).unlink(missing_ok=True)


def test_certify_skill_writes_output_file():
    """certify_skill writes the output file at the specified path."""
    from modex.certify_skill import certify_skill
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        out_path = f.name
    try:
        certify_skill(REPO_ROOT / "skill", Path(out_path))
        assert Path(out_path).exists()
        # File contains valid JSON
        data = json.loads(Path(out_path).read_text())
        assert "trust_score" in data
    finally:
        Path(out_path).unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))