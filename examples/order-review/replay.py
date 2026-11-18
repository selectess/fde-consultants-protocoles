"""Reproduce both reviews from a checkout; write portable, CI-friendly evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = Path(__file__).resolve().parent


def main():
    results = []
    with tempfile.TemporaryDirectory() as temp:
        for variant, expected in (("correct", True), ("regression", False)):
            cmd = [sys.executable, "-m", "modex.engage", "--governed",
                   "--project", str(EXAMPLE / variant), "--memory-dir", f"{temp}/{variant}",
                   "--acceptance-command", sys.executable, str(EXAMPLE / "check.py")]
            run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                 env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            review = json.loads(run.stdout)
            if review["delivery_accepted"] != expected or run.returncode != (0 if expected else 2):
                raise RuntimeError(f"Unexpected {variant} verdict: {review}")
            check = review["acceptance_check"]
            results.append({"variant": variant, "dossier_score": review["assurance_score"],
                            "check_exit": check["exit_code"], "accepted": review["delivery_accepted"],
                            "observation": next(line for line in run.stderr.splitlines()
                                                if line.startswith("Paid revenue:"))})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
