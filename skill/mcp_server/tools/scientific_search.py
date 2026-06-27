"""MCP tool: fde_scientific_search

Wraps skill/scripts/scientific_search.py as an MCP tool.
Generates 4 architecture hypotheses, applies the held-out promotion gate,
writes lessons from rejected hypotheses.
"""
import json
import pathlib
import sys
from typing import Any

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mcp.server.fastmcp import FastMCP

# Import the main function from scientific_search
from scientific_search import main as ss_main


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="fde_scientific_search",
        description=(
            "Stage 2 (Prototyping) tool: generate 4 architecture hypotheses, "
            "score on development evidence, require a held-out promotion gate, "
            "and write rejected-hypothesis lessons. The only executable gate "
            "in the FDE Skill. Use this to choose an architecture with rigor."
        ),
    )
    def fde_scientific_search(
        problem_json: str,
        golden_set_json: str = "",
        lessons_out_path: str = "/tmp/fde_lessons.json",
    ) -> dict[str, Any]:
        """Run FDE scientific hypothesis search with held-out gate.

        Args:
            problem_json: JSON string with the 6-Q problem spec.
            golden_set_json: Optional JSON string of held-out cases for the gate.
            lessons_out_path: Where to write the lessons JSON.

        Returns:
            dict with promoted_hypothesis_id, lessons_count, summary, schema.
        """
        import os, tempfile, subprocess

        # Write inputs to temp files (the underlying CLI reads paths)
        temp_inputs = []
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as pf:
            pf.write(problem_json)
            problem_path = pf.name
        temp_inputs.append(problem_path)
        try:
            # The CLI declares --problem as required (argparse, required=True);
            # the flag must precede the path or argparse exits with code 2.
            args = ["--problem", problem_path, "--lessons-out", lessons_out_path]
            if golden_set_json:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as gf:
                    gf.write(golden_set_json)
                    golden_path = gf.name
                temp_inputs.append(golden_path)
                args.extend(["--golden-set", golden_path])

            # Call the CLI as a subprocess (avoids side-effects of in-process import).
            # Use sys.executable so it runs under the same interpreter as the server.
            cli_path = str(SKILL_ROOT / "scripts" / "scientific_search.py")
            result = subprocess.run(
                [sys.executable, cli_path] + args,
                capture_output=True, text=True, timeout=30,
            )

            # Parse the lessons file produced by the CLI.
            lessons_data = {"schema": None, "lessons": [], "promoted_hypothesis_id": None}
            if os.path.exists(lessons_out_path):
                try:
                    with open(lessons_out_path) as f:
                        lessons_data = json.load(f)
                except (OSError, json.JSONDecodeError):
                    pass

            return {
                "promoted_hypothesis_id": lessons_data.get("promoted_hypothesis_id"),
                "lessons_count": len(lessons_data.get("lessons", [])),
                "lessons": lessons_data.get("lessons", []),
                "schema": lessons_data.get("schema"),
                "summary": result.stdout[-500:] if result.stdout else result.stderr[-500:],
                "exit_code": result.returncode,
            }
        finally:
            # Clean up only the temp INPUT files; keep the user's lessons output.
            for p in temp_inputs:
                try:
                    os.unlink(p)
                except OSError:
                    pass