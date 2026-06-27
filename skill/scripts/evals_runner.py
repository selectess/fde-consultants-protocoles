#!/usr/bin/env python3
"""
Evals Runner — LLM-as-Judge for FDE Deliverables
==================================================

Scores any FDE deliverable on the 6-trait rubric using Claude as judge.
Output: 6 individual scores + overall verdict + actionable feedback.

Usage:
    # Score a deliverable from a file
    python3 evals_runner.py --deliverable scoping-report.md \\
        --context "Manufacturing quality control AI"

    # Score from stdin
    cat deliverable.md | python3 evals_runner.py --stdin

    # Use a different model (default: claude-sonnet-4-5)
    python3 evals_runner.py --deliverable x.md --model claude-opus-4

Requirements:
    ANTHROPIC_API_KEY environment variable

Output format:
    JSON with scores per trait + overall verdict + recommendations
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


# The 6-trait rubric prompt (loaded from references/eval-rubric.md style)
RUBRIC_PROMPT = """You are an expert FDE evaluator scoring a deliverable on 6 traits.

# The Deliverable
{deliverable}

# The Context
{context}

# The 6 Traits — Score 1-5 each

### 1. Customer Curiosity (1-5)
- Does it show real understanding of the user's world?
- Does it reference specific industry facts, regulations, or competitive dynamics?
- Or is it generic advice that could apply to anyone?

### 2. Ownership (1-5)
- Does it commit to a concrete outcome?
- Are there specific dates, numbers, deliverables?
- Or is it hedged with "could", "might", "potentially"?

### 3. Decomposition (1-5)
- Is the problem broken into testable sub-problems?
- Are the 6-Qs (specific process, decision, data, cost of error, current system, success metric) answered?
- Or is the problem restated vaguely?

### 4. Empathy (1-5)
- Does it acknowledge stakeholder realities (political, technical, organizational)?
- Does it propose changes the customer can actually adopt?
- Or does it ignore how the organization works?

### 5. Product Sense (1-5)
- Is the recommendation shippable?
- Is there code, configuration, runbook — or just slides?
- Can a team start building tomorrow?

### 6. Communication (1-5)
- Is there both an executive summary AND technical detail?
- Is it jargon-free where possible, precise where needed?
- Or is it either too high-level or too in-the-weeds?

# Anti-Pattern Detection
Check for these. If any present, flag as REJECT:
- "AI will transform" / "leverage AI" / "ML magic" (buzzword)
- No quantified trade-offs (€/time/%)
- Slide-only deliverable (no code, no runbook)
- "We'll figure it out later" (security/scale/scale punted)
- "Add auth later" / "Add observability later"
- Single-option recommendation (no alternatives)
- No failure mode discussion

# Output Format (JSON)
{{
  "scores": {{
    "customer_curiosity": <1-5>,
    "ownership": <1-5>,
    "decomposition": <1-5>,
    "empathy": <1-5>,
    "product_sense": <1-5>,
    "communication": <1-5>
  }},
  "overall_pass": <true|false>,
  "verdict": "<PASS|FAIL>",
  "anti_patterns_detected": [<list>],
  "top_3_improvements": [<list of 3 specific changes>],
  "justification": "<one paragraph>"
}}

Hard rules:
- PASS only if all 6 scores >= 3, ownership >= 4, decomposition >= 4, no anti-patterns
- FAIL otherwise
- If FAIL, top_3_improvements MUST contain 3 specific, actionable changes

Return ONLY the JSON, no other text.
"""


def heuristic_score(deliverable: str, context: str = "") -> dict:
    """
    Heuristic scoring when no API key is available.
    Useful for development/testing without burning API calls.
    """
    text_lower = deliverable.lower()

    # Heuristic scores
    scores = {
        "customer_curiosity": 3,
        "ownership": 3,
        "decomposition": 3,
        "empathy": 3,
        "product_sense": 3,
        "communication": 3,
    }

    # Customer curiosity — look for industry-specific terms
    industry_signals = ['gdpr', 'hipaa', 'soc 2', 'ai act', 'eu ai act', 'iso 9001',
                        'iatf', 'pci-dss', 'rbac', 'rls', 'b2b', 'b2c', 'saas',
                        'manufacturing', 'fintech', 'healthcare']
    found = sum(1 for s in industry_signals if s in text_lower)
    if found >= 3:
        scores["customer_curiosity"] = 5
    elif found >= 1:
        scores["customer_curiosity"] = 4
    else:
        scores["customer_curiosity"] = 2

    # Ownership — look for specific dates, numbers, percentages
    has_numbers = bool(re.search(r'\d+%|\$\d+|\€\d+|\d+ days|\d+ weeks|\d+ months', deliverable))
    has_dates = bool(re.search(r'by \d{4}|day \d+|week \d+|q[1-4] \d{4}', text_lower))
    if has_numbers and has_dates:
        scores["ownership"] = 5
    elif has_numbers:
        scores["ownership"] = 4
    else:
        scores["ownership"] = 2

    # Decomposition — look for 6-Q answers
    q_keywords = {
        'q1': ['process', 'specific process', 'volume'],
        'q2': ['decision', 'classification', 'latency', 'accuracy'],
        'q3': ['data', 'volume', 'compliance'],
        'q4': ['cost', 'error', 'regulatory'],
        'q5': ['current', 'baseline', 'manual'],
        'q6': ['success', 'metric', 'roi', 'kpi'],
    }
    qs_found = 0
    for keywords in q_keywords.values():
        if any(k in text_lower for k in keywords):
            qs_found += 1
    if qs_found >= 6:
        scores["decomposition"] = 5
    elif qs_found >= 4:
        scores["decomposition"] = 4
    elif qs_found >= 2:
        scores["decomposition"] = 3
    else:
        scores["decomposition"] = 2

    # Empathy — look for stakeholder names, change management
    empathy_signals = ['stakeholder', 'change management', 'team', 'training',
                       'adoption', 'champion', 'ramp']
    if sum(1 for s in empathy_signals if s in text_lower) >= 2:
        scores["empathy"] = 4
    elif any(s in text_lower for s in empathy_signals):
        scores["empathy"] = 3
    else:
        scores["empathy"] = 2

    # Product sense — look for code, runbooks, configs
    code_signals = ['```', '```python', '```yaml', '```bash', 'runbook', 'deployment',
                    'config', 'implementation', 'mvp']
    if sum(1 for s in code_signals if s in text_lower) >= 2:
        scores["product_sense"] = 5
    elif any(s in text_lower for s in code_signals):
        scores["product_sense"] = 4
    else:
        scores["product_sense"] = 2

    # Communication — look for executive summary + technical detail
    has_exec = 'executive summary' in text_lower or 'summary' in text_lower[:500]
    has_technical = '```' in deliverable or 'api' in text_lower or 'architecture' in text_lower
    if has_exec and has_technical:
        scores["communication"] = 5
    elif has_exec or has_technical:
        scores["communication"] = 4
    else:
        scores["communication"] = 3

    # Anti-patterns
    anti_patterns = []
    if 'ai will transform' in text_lower or 'leverage ai' in text_lower:
        anti_patterns.append("AI buzzword without substance")
    if not has_numbers:
        anti_patterns.append("No quantified trade-offs")
    if '```' not in deliverable and 'code' not in text_lower:
        anti_patterns.append("No code or runbook artifacts")
    if 'add auth later' in text_lower or 'figure it out later' in text_lower:
        anti_patterns.append("Hidden assumptions / punted decisions")

    # Verdict
    all_pass = all(s >= 3 for s in scores.values())
    hard_pass = scores["ownership"] >= 4 and scores["decomposition"] >= 4
    no_anti = len(anti_patterns) == 0

    overall_pass = all_pass and hard_pass and no_anti

    # Improvements
    improvements = []
    if scores["ownership"] < 4:
        improvements.append("Add specific dates, numbers, and deliverables (not 'could' or 'might')")
    if scores["decomposition"] < 4:
        improvements.append("Decompose the problem into the 6-Q framework with concrete answers")
    if scores["product_sense"] < 4:
        improvements.append("Add code, runbook, or implementation artifact (not just slides)")
    if scores["customer_curiosity"] < 4:
        improvements.append("Reference specific industry facts, regulations, or competitive dynamics")
    if not improvements:
        improvements.append("Consider adding more quantified sensitivity analysis")

    while len(improvements) < 3:
        improvements.append("Add more specific examples and trade-offs")

    return {
        "scores": scores,
        "overall_pass": overall_pass,
        "verdict": "PASS" if overall_pass else "FAIL",
        "anti_patterns_detected": anti_patterns,
        "top_3_improvements": improvements[:3],
        "justification": f"Heuristic scoring. Ownership={scores['ownership']}, "
                        f"Decomposition={scores['decomposition']}, "
                        f"Product Sense={scores['product_sense']}. "
                        f"{'Strong deliverable.' if overall_pass else 'Needs improvement.'}",
        "scoring_method": "heuristic",
    }


def llm_score(deliverable: str, context: str, model: str = "claude-sonnet-4-5") -> dict:
    """
    Score using Claude as LLM-as-judge.

    Requires ANTHROPIC_API_KEY.
    """
    try:
        import anthropic
    except ImportError:
        return {
            "error": "anthropic package not installed. Run: pip install anthropic",
            "scoring_method": "llm_skipped",
        }

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "error": "ANTHROPIC_API_KEY not set. Falling back to heuristic.",
            "scoring_method": "llm_skipped",
        }

    client = anthropic.Anthropic(api_key=api_key)

    prompt = RUBRIC_PROMPT.format(
        deliverable=deliverable[:15000],  # Truncate to avoid token limits
        context=context or "Not specified",
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        # Extract JSON from response
        text = response.content[0].text

        # Try to parse JSON directly
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            result["scoring_method"] = "llm"
            result["model"] = model
            return result
        else:
            return {
                "error": "Could not parse JSON from LLM response",
                "raw_response": text[:500],
                "scoring_method": "llm_failed",
            }

    except Exception as e:
        return {
            "error": f"LLM call failed: {str(e)}",
            "scoring_method": "llm_failed",
        }


def main():
    parser = argparse.ArgumentParser(description="Score FDE deliverable on 6-trait rubric")
    parser.add_argument("--deliverable", help="Path to deliverable file")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--context", default="", help="Engagement context")
    parser.add_argument("--model", default="claude-sonnet-4-5", help="LLM model for judging")
    parser.add_argument("--method", choices=["heuristic", "llm", "auto"], default="auto",
                        help="Scoring method")
    parser.add_argument("--output", help="Save JSON to file")
    args = parser.parse_args()

    # Read deliverable
    if args.stdin:
        deliverable = sys.stdin.read()
    elif args.deliverable:
        with open(args.deliverable) as f:
            deliverable = f.read()
    else:
        parser.print_help()
        sys.exit(1)

    # Decide method
    method = args.method
    if method == "auto":
        if os.environ.get("ANTHROPIC_API_KEY") and args.method != "heuristic":
            method = "llm"
        else:
            method = "heuristic"

    # Score
    if method == "llm":
        result = llm_score(deliverable, args.context, args.model)
        if "error" in result and result.get("scoring_method") == "llm_failed":
            print(f"LLM scoring failed: {result['error']}", file=sys.stderr)
            print("Falling back to heuristic...", file=sys.stderr)
            result = heuristic_score(deliverable, args.context)
    else:
        result = heuristic_score(deliverable, args.context)

    # Pretty print
    print()
    print("=" * 70)
    print("FDE DELIVERABLE EVAL — 6-Trait Rubric")
    print("=" * 70)
    print()
    print(f"Scoring method: {result.get('scoring_method', 'unknown')}")
    if "model" in result:
        print(f"Model: {result['model']}")
    print()

    scores = result.get("scores", {})
    if scores:
        print("Trait Scores (1-5):")
        for trait, score in scores.items():
            bar = "█" * score + "░" * (5 - score)
            print(f"  {trait:<22} {bar} {score}/5")
        print()

    verdict = result.get("verdict", "?")
    if verdict == "PASS":
        print(f"Verdict: ✅ PASS")
    else:
        print(f"Verdict: ❌ FAIL")
    print()

    if result.get("anti_patterns_detected"):
        print("Anti-patterns detected:")
        for ap in result["anti_patterns_detected"]:
            print(f"  ⚠ {ap}")
        print()

    if result.get("top_3_improvements"):
        print("Top improvements:")
        for i, imp in enumerate(result["top_3_improvements"], 1):
            print(f"  {i}. {imp}")
        print()

    if result.get("justification"):
        print(f"Justification: {result['justification']}")
        print()

    print("=" * 70)

    # Save JSON
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to {args.output}")

    # Exit code
    sys.exit(0 if result.get("overall_pass") else 1)


if __name__ == "__main__":
    main()
