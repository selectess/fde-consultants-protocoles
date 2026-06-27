"""
Compatibility wrapper for earlier FDE Consultant builds.

The canonical FDE-native implementation is now `scientific_search.py`. This
wrapper keeps older docs, tests, and agent memories working without keeping
Arbor as the public identity of the method.
"""

from __future__ import annotations

from scientific_search import main


if __name__ == "__main__":
    raise SystemExit(main())
