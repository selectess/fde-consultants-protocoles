"""Acceptance requirement: cancelled orders do not count as paid revenue."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
from revenue import revenue

actual = revenue([("paid", 120), ("cancelled", 80)])
print(f"Paid revenue: expected 120, observed {actual}")
sys.exit(0 if actual == 120 else 1)
