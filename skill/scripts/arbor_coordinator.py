"""
Compatibility wrapper for earlier FDE Skill builds.

The real FDE-native logic now lives in `scientific_search.py`: competing
hypotheses, held-out promotion, and failure-to-insight lessons. This wrapper only
redirects older calls so legacy Arbor-labeled docs do not run a misleading demo.
"""

from __future__ import annotations

from scientific_search import main


if __name__ == "__main__":
    raise SystemExit(main())
