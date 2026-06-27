"""Tests for fde_recon — Stage 0 reconnaissance scanner (script + MCP tool)."""
import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skill" / "scripts"))

from fde_recon import scan_codebase, SCHEMA  # noqa: E402


def _make_project(tmp_path: Path) -> Path:
    """Create a fake project: >5 Python files using an AI lib, no tests."""
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text(
        "import anthropic\n\n"
        "class OrderProcessor:\n"
        "    def run(self):\n"
        "        # TODO: handle retries\n"
        "        return 1\n"
    )
    # Extra modules so code_files > 5 (the threshold for the no-tests risk flag).
    for i in range(6):
        (tmp_path / "app" / f"mod{i}.py").write_text(f"VALUE_{i} = {i}\n")
    (tmp_path / "requirements.txt").write_text("anthropic==0.39.0\nfastapi==0.115.0\n")
    return tmp_path


def test_scan_returns_expected_schema_and_keys(tmp_path):
    dossier = scan_codebase(_make_project(tmp_path))
    assert dossier["schema"] == SCHEMA
    for key in ("summary", "size", "languages", "dependencies", "tests",
                "tech_debt", "ontology_candidates", "risk_flags", "six_q_signals"):
        assert key in dossier, f"missing key {key}"


def test_scan_detects_python_and_ai_library(tmp_path):
    dossier = scan_codebase(_make_project(tmp_path))
    langs = {l["language"] for l in dossier["languages"]}
    assert "Python" in langs
    assert dossier["dependencies"]["is_existing_ai_system"] is True
    assert "anthropic" in dossier["dependencies"]["ai_ml_libraries"]


def test_scan_flags_missing_tests_and_extracts_ontology(tmp_path):
    dossier = scan_codebase(_make_project(tmp_path))
    # No tests present -> risk flag mentions tests
    assert any("test" in r.lower() for r in dossier["risk_flags"])
    # Ontology candidate extracted from `class OrderProcessor`
    entities = {e["entity"] for e in dossier["ontology_candidates"]}
    assert "OrderProcessor" in entities
    # Debt marker counted
    assert dossier["tech_debt"]["total"] >= 1


def test_scan_missing_path_returns_error():
    dossier = scan_codebase(Path("/no/such/path/xyz123"))
    assert "error" in dossier


def test_fde_recon_registered_as_mcp_tool(tmp_path):
    from skill.mcp_server.server import mcp
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert "fde_recon" in names, f"fde_recon missing from {names}"
    # Call it end-to-end on a temp project
    result = asyncio.run(mcp.call_tool("fde_recon", {"path": str(_make_project(tmp_path))}))
    obj = result
    for _ in range(3):
        if isinstance(obj, (list, tuple)) and obj:
            obj = obj[0]
        else:
            break
    text = getattr(obj, "text", obj) if not isinstance(obj, str) else obj
    data = json.loads(text)
    assert data["schema"] == SCHEMA
    assert data["size"]["code_files"] >= 1
