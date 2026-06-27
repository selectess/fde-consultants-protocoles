
"""
Unit tests for fde-consultant skill Python scripts.
"""
import json
import subprocess
import sys
from pathlib import Path

# Skill root directory
SKILL_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
EXAMPLES_DIR = SKILL_ROOT / "examples"


def test_decompose_problem_valid_input():
    """Test decompose_problem.py with valid input."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "decompose_problem.py"),
            "--problem",
            str(EXAMPLES_DIR / "customer-service-triage.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0


def test_roi_calculator_valid_input():
    """Test roi_calculator.py with valid input."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "roi_calculator.py"),
            "--problem",
            str(EXAMPLES_DIR / "customer-service-roi.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0


def test_ontology_extractor_valid_input():
    """Test ontology_extractor.py with valid input."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "ontology_extractor.py"),
            "--input",
            str(EXAMPLES_DIR / "manufacturing-notes.md"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0


def test_all_examples_valid_json():
    """Verify all JSON example files are valid."""
    for json_file in EXAMPLES_DIR.glob("*.json"):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert len(data) > 0


def test_new_saas_example_valid():
    """Test the new SaaS churn prediction example."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "decompose_problem.py"),
            "--problem",
            str(EXAMPLES_DIR / "saas-churn-prediction.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0


def test_new_fintech_example_valid():
    """Test the new Fintech fraud detection example."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "decompose_problem.py"),
            "--problem",
            str(EXAMPLES_DIR / "fintech-fraud-detection.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0


def test_new_healthcare_example_valid():
    """Test the new Healthcare patient triage example."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "decompose_problem.py"),
            "--problem",
            str(EXAMPLES_DIR / "healthcare-patient-triage.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0


def test_new_retail_example_valid():
    """Test the new Retail demand forecasting example."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "decompose_problem.py"),
            "--problem",
            str(EXAMPLES_DIR / "retail-demand-forecasting.json"),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0


def test_scientific_search_runs():
    """Test that scientific_search.py runs end-to-end with a real held-out gate."""
    lessons_out = SKILL_ROOT / ".pytest_scientific_lessons.json"
    if lessons_out.exists():
        lessons_out.unlink()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "scientific_search.py"),
            "--problem",
            str(EXAMPLES_DIR / "fintech-fraud-detection.json"),
            "--golden-set",
            str(EXAMPLES_DIR / "fintech-fraud-golden-set.json"),
            "--lessons-out",
            str(lessons_out),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0
    assert "FDE SCIENTIFIC SEARCH" in result.stdout
    assert "Coordinator" in result.stdout
    assert "HELD-OUT GATE" in result.stdout
    assert "Best hypothesis" in result.stdout
    assert lessons_out.exists()
    lessons = json.loads(lessons_out.read_text(encoding="utf-8"))
    assert lessons["schema"] == "fde-scientific-search-lessons-v1"
    assert len(lessons["lessons"]) >= 1
    lessons_out.unlink()


def test_scientific_search_picks_winner():
    """Test that scientific_search.py promotes only after held-out validation passes."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "scientific_search.py"),
            "--problem",
            str(EXAMPLES_DIR / "healthcare-patient-triage.json"),
            "--lessons-out",
            "/tmp/fde-healthcare-lessons-test.json",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0
    assert "PROMOTED" in result.stdout
    assert "Held-out score" in result.stdout


def test_scientific_search_blocks_when_held_out_gate_fails(tmp_path):
    """A candidate cannot be promoted when the separate golden set is impossible."""
    golden_set = tmp_path / "impossible-golden-set.json"
    lessons_out = tmp_path / "lessons.json"
    golden_set.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": "must-run-with-verified-hardware-attestation",
                        "description": "No generated hypothesis currently has this trait.",
                        "required_traits": ["verified_hardware_attestation"],
                        "minimum_score": 100,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "scientific_search.py"),
            "--problem",
            str(EXAMPLES_DIR / "fintech-fraud-detection.json"),
            "--golden-set",
            str(golden_set),
            "--lessons-out",
            str(lessons_out),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )

    assert result.returncode == 0
    assert "No hypothesis passed the held-out merge gate" in result.stdout
    lessons = json.loads(lessons_out.read_text(encoding="utf-8"))
    assert lessons["promoted_hypothesis_id"] is None
    assert len(lessons["lessons"]) == 4


def test_arbor_fde_wrapper_still_runs():
    """Legacy Arbor-labeled entrypoint remains as a compatibility wrapper."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "arbor_fde.py"),
            "--problem",
            str(EXAMPLES_DIR / "fintech-fraud-detection.json"),
            "--golden-set",
            str(EXAMPLES_DIR / "fintech-fraud-golden-set.json"),
            "--lessons-out",
            "/tmp/fde-arbor-wrapper-lessons-test.json",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_ROOT),
    )
    assert result.returncode == 0
    assert "FDE SCIENTIFIC SEARCH" in result.stdout


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
