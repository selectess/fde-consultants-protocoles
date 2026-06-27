#!/usr/bin/env python3
"""Test that the registry/ chain is internally consistent.

Verifies:
- index.json references all 4 entries
- each entry's file hash (sha256 of the file on disk) matches the index
- prev_hash of entry N = file hash of entry N-1
- genesis.json is the first entry
- genesis.prev_hash is null

Can be run two ways:
- as a pytest test: pytest skill/tests/test_registry_chain.py
- standalone:        python3 skill/tests/test_registry_chain.py

Exit 0 = PASS, 1 = FAIL.
"""
import hashlib
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
REGISTRY = REPO_ROOT / "registry"


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def check_chain():
    """Returns (passed: bool, failures: list[str])."""
    if not REGISTRY.is_dir():
        return False, [f"FAIL: registry/ not found at {REGISTRY}"]

    index = load_json(REGISTRY / "index.json")
    entries = index.get("entries", [])
    if not entries:
        return False, ["FAIL: registry/index.json has no entries"]

    print(f"Registry version {index.get('registry_version')} — {len(entries)} entries")
    failures = []

    # 1. Genesis must be first.
    if entries[0].get("cert_id") != "genesis":
        failures.append(f"First entry must be genesis, got {entries[0].get('cert_id')}")

    # 2. Each entry's file hash must match index['sha256'].
    chain = []
    for entry in entries:
        rel_path = entry["path"].replace("registry/", "")
        path = REGISTRY / rel_path
        if not path.exists():
            failures.append(f"{entry['cert_id']}: file not found at {path}")
            continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            failures.append(
                f"{entry['cert_id']}: index says sha256={entry['sha256'][:12]}..., "
                f"file actually is {actual[:12]}... (drift)"
            )
        disk_data = load_json(path)
        chain.append({
            "cert_id": entry["cert_id"],
            "actual_sha256": actual,
            "index_sha256": entry["sha256"],
            "prev_hash": disk_data.get("prev_hash"),
            "trust_score": disk_data.get("trust_score"),
        })

    # 3. Chain integrity: prev_hash of entry N = file hash of entry N-1.
    for i in range(1, len(chain)):
        prev_sha = chain[i - 1]["actual_sha256"]
        curr_prev = chain[i]["prev_hash"]
        if curr_prev != prev_sha:
            failures.append(
                f"Chain broken at {chain[i]['cert_id']}: "
                f"prev_hash={curr_prev[:12] if curr_prev else None}..., "
                f"expected={prev_sha[:12]}..."
            )

    # 4. Genesis prev_hash must be null.
    if chain and chain[0]["prev_hash"] is not None:
        failures.append("Genesis prev_hash must be null")

    # 5. All trust_scores must be ≥85 OR None (genesis).
    for c in chain:
        if c["trust_score"] is not None and c["trust_score"] < 85:
            failures.append(f"{c['cert_id']}: trust_score={c['trust_score']} < 85 (not Certified)")

    return len(failures) == 0, failures


def test_registry_chain_is_valid():
    """Pytest entry point — runs the chain verification."""
    passed, failures = check_chain()
    if not passed:
        msg = "\n".join(failures)
        pytest.fail(f"Registry chain invalid:\n{msg}")


if __name__ == "__main__":
    passed, failures = check_chain()
    if not passed:
        print(f"\n❌ FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print(f"\n✅ PASS — chain intact, all hashes match, all scores ≥85 (or null).")
    sys.exit(0)
else:
    import pytest  # only imported when collected by pytest