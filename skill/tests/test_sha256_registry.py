"""
SHA-256 non-regression test for the 3 certified case studies.

Prevents the "stale hash" bug: if a case study is edited, this test fails
until case-studies/README.md is updated with the new hash.

Run: python3 -m pytest skill/tests/test_sha256_registry.py -q
"""
import hashlib
import re
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
CASE_STUDIES_DIR = SKILL_ROOT / "examples" / "case-studies"
README = CASE_STUDIES_DIR / "README.md"

CASE_STUDIES = [
    "case-study-saas-churn.md",
    "case-study-retail-forecasting.md",
    "case-study-fintech-fraud.md",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _readme_hashes() -> dict:
    """Extract the 3 hashes from the 'Expected:' block in README.md."""
    text = README.read_text(encoding="utf-8")
    hashes = {}
    for filename in CASE_STUDIES:
        match = re.search(r"([0-9a-f]{64})\s+" + re.escape(filename), text)
        if match:
            hashes[filename] = match.group(1)
    return hashes


def test_case_studies_exist():
    """All 3 case study files must exist."""
    for filename in CASE_STUDIES:
        assert (CASE_STUDIES_DIR / filename).exists(), f"Missing: {filename}"


def test_sha256_matches_readme():
    """Each case study's real SHA-256 must match the hash published in README.md.

    If this fails, the case study was edited after the README was last updated.
    Fix: recompute `shasum -a 256` and update README.md 'Expected:' block.
    """
    readme_hashes = _readme_hashes()
    assert len(readme_hashes) == 3, (
        f"README.md should list 3 hashes, found {len(readme_hashes)}. "
        "Check the 'Expected:' block in case-studies/README.md."
    )
    for filename in CASE_STUDIES:
        real_hash = _sha256(CASE_STUDIES_DIR / filename)
        published_hash = readme_hashes[filename]
        assert real_hash == published_hash, (
            f"SHA-256 mismatch for {filename}.\n"
            f"  README says:  {published_hash}\n"
            f"  Actual is:   {real_hash}\n"
            f"Fix: update README.md with the actual hash."
        )


if __name__ == "__main__":
    test_case_studies_exist()
    test_sha256_matches_readme()
    print("✅ SHA-256 registry: all 3 case studies match README.md")
