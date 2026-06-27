#!/usr/bin/env python3
"""
FDE Reconnaissance — Stage 0 codebase & business scanner
========================================================

The FDE operating rule is: *never scope from imagination — scrutinize the real
artifact first*. This script "passes the codebase under the microscope" before
any FDE deliverable is produced, and turns raw findings into 6-Q signals.

Zero third-party dependencies (Python stdlib only), like every FDE script.

Usage:
    python fde_recon.py --path /path/to/repo
    python fde_recon.py --path . --output recon.json

Output:
    A structured reconnaissance dossier (languages, size, dependencies, tests,
    tech-debt, AI/ML signals, ontology candidates, git hotspots, risk flags)
    plus 6-Q pre-fill signals and a short narrative summary.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Optional

SCHEMA = "fde-recon-v1"

# Directories we never descend into (noise / vendored / generated).
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".next", ".nuxt", "target",
    "vendor", ".idea", ".vscode", "coverage", ".cache", "out", ".gradle",
    "Pods", "DerivedData", ".terraform", "bin", "obj",
}

# Extension -> language label, with a rough "is code" flag.
LANG_BY_EXT = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby", ".php": "PHP", ".c": "C", ".h": "C/C++ header", ".cpp": "C++",
    ".cc": "C++", ".cs": "C#", ".swift": "Swift", ".m": "Objective-C", ".scala": "Scala",
    ".sh": "Shell", ".sql": "SQL", ".r": "R", ".jl": "Julia", ".dart": "Dart",
    ".vue": "Vue", ".svelte": "Svelte", ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
}
CODE_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".rb",
    ".php", ".c", ".h", ".cpp", ".cc", ".cs", ".swift", ".m", ".scala", ".sh",
    ".sql", ".r", ".jl", ".dart", ".vue", ".svelte",
}
# Language labels that count as "code" (vs docs/markup like Markdown/JSON/YAML).
CODE_LANG_LABELS = {LANG_BY_EXT[e] for e in CODE_EXTS}

# Dependency manifests -> parser key.
DEP_MANIFESTS = {
    "requirements.txt": "requirements",
    "pyproject.toml": "pyproject",
    "package.json": "package_json",
    "go.mod": "go_mod",
    "Cargo.toml": "cargo",
    "Gemfile": "gemfile",
    "pom.xml": "pom",
    "composer.json": "composer",
}

# Libraries that signal an existing AI/ML system (Q5 "current system" signal).
AI_ML_LIBS = {
    "torch", "tensorflow", "keras", "scikit-learn", "sklearn", "transformers",
    "langchain", "llama-index", "llama_index", "openai", "anthropic", "cohere",
    "huggingface_hub", "sentence-transformers", "xgboost", "lightgbm", "spacy",
    "onnxruntime", "vllm", "ollama", "pinecone", "chromadb", "weaviate", "faiss",
    "@anthropic-ai/sdk", "ai", "@langchain/core", "openai-node",
}

DEBT_MARKERS = ("TODO", "FIXME", "HACK", "XXX", "BUG", "DEPRECATED")
# Heuristic secret patterns (Q4 cost-of-error / risk signal).
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),          # OpenAI-style
    re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b"),      # Stripe live
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),              # AWS access key
    re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}\b"),       # Google API key
    re.compile(r"(?i)(password|passwd|secret|api[_-]?key)\s*[:=]\s*[\"'][^\"']{6,}[\"']"),
]

LARGE_FILE_LOC = 600   # a single file over this is a complexity hotspot
MAX_FILES = 25000      # safety cap so huge monorepos don't hang


def _iter_files(root: Path):
    """Yield files under root, skipping ignored dirs. Capped at MAX_FILES."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
                       or d in (".github",)]  # keep .github, drop other dotdirs
        for name in filenames:
            yield Path(dirpath) / name
            count += 1
            if count >= MAX_FILES:
                return


def _count_loc(path: Path) -> int:
    """Count lines of a text file; 0 on binary/read error."""
    try:
        with path.open("rb") as fh:
            chunk = fh.read()
        if b"\x00" in chunk[:1024]:
            return 0  # binary
        return chunk.count(b"\n") + (0 if chunk.endswith(b"\n") or not chunk else 1)
    except OSError:
        return 0


def _read_text(path: Path, limit: int = 400_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


# --------------------------------------------------------------------------- #
# Dependency parsing (best-effort, stdlib only)
# --------------------------------------------------------------------------- #
def _parse_dependencies(root: Path) -> dict[str, Any]:
    found: dict[str, list[str]] = {}
    for manifest, kind in DEP_MANIFESTS.items():
        path = root / manifest
        if not path.exists():
            continue
        text = _read_text(path)
        deps: list[str] = []
        try:
            if kind == "requirements":
                for line in text.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        deps.append(re.split(r"[=<>!~;\[ ]", line)[0])
            elif kind == "package_json" or kind == "composer":
                data = json.loads(text or "{}")
                for section in ("dependencies", "devDependencies", "require", "require-dev"):
                    deps.extend((data.get(section) or {}).keys())
            elif kind == "pyproject":
                # naive: catch [project] dependencies and poetry deps
                for m in re.findall(r'["\']([A-Za-z0-9_.\-]+)["\']\s*[,\]]', text):
                    deps.append(m)
                for line in re.findall(r"^([A-Za-z0-9_.\-]+)\s*=\s*", text, re.M):
                    deps.append(line)
            elif kind == "go_mod":
                deps.extend(re.findall(r"^\s+([\w./\-]+)\s+v", text, re.M))
            elif kind == "cargo":
                in_deps = False
                for line in text.splitlines():
                    s = line.strip()
                    if s.startswith("[") and "dependencies" in s:
                        in_deps = True; continue
                    if s.startswith("["):
                        in_deps = False
                    if in_deps and "=" in s:
                        deps.append(s.split("=")[0].strip())
            elif kind == "gemfile":
                deps.extend(re.findall(r"gem\s+['\"]([^'\"]+)['\"]", text))
            elif kind == "pom":
                deps.extend(re.findall(r"<artifactId>([^<]+)</artifactId>", text))
        except (json.JSONDecodeError, ValueError):
            pass
        deps = sorted({d for d in deps if d and len(d) < 80})
        if deps:
            found[manifest] = deps
    all_deps = sorted({d for lst in found.values() for d in lst})
    ai_ml = sorted({d for d in all_deps if d.lower() in {x.lower() for x in AI_ML_LIBS}})
    return {
        "manifests": sorted(found.keys()),
        "by_manifest": found,
        "total_unique": len(all_deps),
        "ai_ml_libraries": ai_ml,
        "is_existing_ai_system": bool(ai_ml),
    }


# --------------------------------------------------------------------------- #
# Git intelligence (optional — skipped gracefully if unavailable)
# --------------------------------------------------------------------------- #
def _git(root: Path, *args: str) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _git_intel(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {"is_git_repo": False}
    commits = _git(root, "rev-list", "--count", "HEAD")
    authors = _git(root, "shortlog", "-sne", "HEAD")
    last = _git(root, "log", "-1", "--format=%ci")
    # churn: most-changed files (a hotspot signal for where the value/risk lives)
    churn_raw = _git(root, "log", "--name-only", "--pretty=format:", "-n", "400")
    hotspots: list[dict[str, Any]] = []
    if churn_raw:
        c = Counter(l.strip() for l in churn_raw.splitlines() if l.strip())
        hotspots = [{"file": f, "changes": n} for f, n in c.most_common(10)]
    return {
        "is_git_repo": True,
        "total_commits": int(commits.strip()) if commits and commits.strip().isdigit() else None,
        "contributors": len([l for l in (authors or "").splitlines() if l.strip()]) or None,
        "last_commit": (last or "").strip() or None,
        "churn_hotspots": hotspots,
    }


# --------------------------------------------------------------------------- #
# Main scan
# --------------------------------------------------------------------------- #
def scan_codebase(root: Path) -> dict[str, Any]:
    """Scan a codebase and return the FDE reconnaissance dossier."""
    root = Path(root).resolve()
    if not root.exists():
        return {"schema": SCHEMA, "error": f"Path not found: {root}"}

    lang_files: Counter = Counter()
    lang_loc: Counter = Counter()
    total_files = 0
    total_loc = 0
    largest: list[tuple[int, str]] = []
    debt = Counter()
    test_files = 0
    code_files = 0
    secret_hits: list[str] = []
    dir_names: Counter = Counter()
    class_names: list[str] = []
    has = {"readme": False, "dockerfile": False, "ci": False, "license": False,
           "data_dir": False, "docs": False}

    for path in _iter_files(root):
        total_files += 1
        rel = str(path.relative_to(root))
        low = path.name.lower()
        ext = path.suffix.lower()

        if low.startswith("readme"):
            has["readme"] = True
        if low in ("dockerfile",) or low.endswith(".dockerfile"):
            has["dockerfile"] = True
        if low.startswith("license") or low.startswith("licence"):
            has["license"] = True
        if ".github/workflows" in rel or low in ("ci.yml", ".gitlab-ci.yml", "jenkinsfile"):
            has["ci"] = True
        if ext in (".csv", ".parquet", ".jsonl", ".tsv") or "/data/" in f"/{rel}/":
            has["data_dir"] = True
        if rel.startswith("docs/") or "/docs/" in rel:
            has["docs"] = True

        if ext in LANG_BY_EXT:
            lang = LANG_BY_EXT[ext]
            lang_files[lang] += 1
            loc = _count_loc(path)
            lang_loc[lang] += loc
            if ext in CODE_EXTS:
                code_files += 1
                total_loc += loc
                largest.append((loc, rel))
                if loc > LARGE_FILE_LOC:
                    pass
                if any(seg in low for seg in ("test", "spec")) or "/tests/" in f"/{rel}":
                    test_files += 1

        # cheap content scan only for code/text files of reasonable size
        if ext in CODE_EXTS:
            text = _read_text(path, limit=200_000)
            for marker in DEBT_MARKERS:
                debt[marker] += len(re.findall(rf"\b{marker}\b", text))
            for pat in SECRET_PATTERNS:
                if pat.search(text):
                    secret_hits.append(rel)
                    break
            # ontology candidates: class / type / struct / interface names
            for m in re.findall(r"\b(?:class|struct|interface|type|model)\s+([A-Z][A-Za-z0-9_]{2,})", text):
                class_names.append(m)

        top = rel.split(os.sep)[0]
        if top and not top.startswith("."):
            dir_names[top] += 1

    largest.sort(reverse=True)
    hotspot_files = [{"file": f, "loc": loc} for loc, f in largest[:10]]
    big_files = [{"file": f, "loc": loc} for loc, f in largest if loc > LARGE_FILE_LOC][:15]
    primary_langs = [{"language": l, "files": n, "loc": lang_loc[l],
                      "is_code": l in CODE_LANG_LABELS}
                     for l, n in lang_files.most_common(10)]
    code_langs = [l for l in primary_langs if l["is_code"]]
    ontology = [{"entity": e, "mentions": n}
                for e, n in Counter(class_names).most_common(20)]

    deps = _parse_dependencies(root)
    git = _git_intel(root)

    # Risk flags (feed Q4 cost-of-error + general due diligence)
    risks: list[str] = []
    if not has["readme"]:
        risks.append("No README — undocumented project")
    if test_files == 0 and code_files > 5:
        risks.append("No tests detected — change is high-risk, no safety net")
    if not has["ci"] and code_files > 20:
        risks.append("No CI pipeline — no automated quality gate")
    if secret_hits:
        risks.append(f"Possible hard-coded secrets in {len(secret_hits)} file(s) — security exposure")
    if big_files:
        risks.append(f"{len(big_files)} oversized file(s) >{LARGE_FILE_LOC} LOC — complexity hotspots")
    debt_total = sum(debt.values())
    if debt_total > 50:
        risks.append(f"{debt_total} debt markers (TODO/FIXME/...) — accumulated tech debt")

    test_ratio = round(test_files / code_files, 3) if code_files else 0.0

    # 6-Q pre-fill signals: what reconnaissance can already say about each question.
    six_q = {
        "q1_process_hint": (
            f"Primary stack: {code_langs[0]['language']} "
            f"({code_files} code files, {total_loc} LOC). Top areas: "
            + ", ".join(d for d, _ in dir_names.most_common(5))
        ) if code_langs else "Empty or non-code repository.",
        "q3_data_hint": ("Data artifacts present (csv/parquet/jsonl or /data)."
                         if has["data_dir"] else "No obvious dataset in-repo — confirm data source/volume."),
        "q5_current_system_hint": (
            "Existing AI/ML system: " + ", ".join(deps["ai_ml_libraries"])
            if deps["ai_ml_libraries"] else
            "No AI/ML libraries detected — likely a greenfield AI use case on a "
            f"{'tested' if test_ratio > 0 else 'no-test'} codebase."
        ),
        "q4_cost_of_error_hint": (
            "Elevated: " + "; ".join(risks) if risks else
            "Baseline hygiene OK (README+tests+CI present)."
        ),
        "q6_measurement_hint": (
            "Tests + CI exist — measurable baseline available."
            if (test_ratio > 0 and has["ci"]) else
            "Weak measurement infra — establish evals/baseline before claiming KPI movement."
        ),
    }

    summary = _narrative(root.name, code_files, total_loc, code_langs,
                         deps, test_ratio, risks, git)

    return {
        "schema": SCHEMA,
        "root": str(root),
        "summary": summary,
        "size": {
            "total_files": total_files,
            "code_files": code_files,
            "total_loc": total_loc,
            "top_level_dirs": [d for d, _ in dir_names.most_common(12)],
        },
        "languages": primary_langs,
        "dependencies": deps,
        "tests": {
            "test_files": test_files,
            "test_to_code_ratio": test_ratio,
            "has_ci": has["ci"],
        },
        "tech_debt": {"markers": dict(debt), "total": debt_total,
                      "oversized_files": big_files},
        "hotspots": {"largest_files": hotspot_files,
                     "git_churn": git.get("churn_hotspots", [])},
        "ontology_candidates": ontology,
        "project_hygiene": has,
        "git": git,
        "risk_flags": risks,
        "six_q_signals": six_q,
    }


def _narrative(name, code_files, loc, langs, deps, test_ratio, risks, git) -> str:
    stack = ", ".join(f"{l['language']}" for l in langs[:3]) or "no detected code"
    ai = ("an existing AI/ML system (" + ", ".join(deps["ai_ml_libraries"][:4]) + ")"
          if deps["ai_ml_libraries"] else "a non-AI codebase (greenfield AI opportunity)")
    test_state = ("with a test safety net" if test_ratio >= 0.2
                  else "with weak/no test coverage")
    commits = git.get("total_commits")
    maturity = (f"~{commits} commits" if commits else "unknown history")
    risk_line = (f" {len(risks)} risk flag(s) to address before scoping."
                 if risks else " No major hygiene risks.")
    return (
        f"'{name}' is {ai}, {code_files} code files / {loc} LOC in {stack}, "
        f"{test_state} ({maturity}).{risk_line} "
        "Use these findings to ground the 6-Q decomposition instead of guessing."
    )


def format_report(dossier: dict[str, Any]) -> str:
    """Human-readable reconnaissance report."""
    if "error" in dossier:
        return f"ERROR: {dossier['error']}"
    s = dossier["size"]
    lines = [
        "=" * 72,
        "FDE RECONNAISSANCE — Stage 0 (scrutinize before you scope)",
        "=" * 72,
        dossier["summary"],
        "",
        f"SIZE: {s['code_files']} code files, {s['total_loc']} LOC, "
        f"{s['total_files']} files total",
        "LANGUAGES: " + ", ".join(f"{l['language']} ({l['loc']} LOC)"
                                  for l in dossier["languages"][:5]),
        f"DEPENDENCIES: {dossier['dependencies']['total_unique']} unique "
        f"(manifests: {', '.join(dossier['dependencies']['manifests']) or 'none'})",
    ]
    if dossier["dependencies"]["ai_ml_libraries"]:
        lines.append("  AI/ML: " + ", ".join(dossier["dependencies"]["ai_ml_libraries"]))
    t = dossier["tests"]
    lines.append(f"TESTS: {t['test_files']} files, ratio {t['test_to_code_ratio']}, "
                 f"CI={'yes' if t['has_ci'] else 'no'}")
    if dossier["ontology_candidates"]:
        lines.append("ONTOLOGY CANDIDATES: " +
                     ", ".join(e["entity"] for e in dossier["ontology_candidates"][:10]))
    if dossier["risk_flags"]:
        lines.append("\nRISK FLAGS:")
        lines += [f"  ⚠ {r}" for r in dossier["risk_flags"]]
    lines.append("\n6-Q SIGNALS (pre-fill the decomposition):")
    for k, v in dossier["six_q_signals"].items():
        lines.append(f"  • {k}: {v}")
    lines.append("=" * 72)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="FDE Stage 0 reconnaissance — scrutinize a codebase before scoping")
    parser.add_argument("--path", default=".", help="Path to the repository to scan")
    parser.add_argument("--output", default=None, help="Write JSON dossier to this file")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of report")
    args = parser.parse_args()

    dossier = scan_codebase(Path(args.path))
    if args.output:
        Path(args.output).write_text(json.dumps(dossier, indent=2), encoding="utf-8")
        print(f"Reconnaissance dossier written to {args.output}")
    if args.json:
        print(json.dumps(dossier, indent=2))
    else:
        print(format_report(dossier))
    return 0 if "error" not in dossier else 1


if __name__ == "__main__":
    sys.exit(main())
