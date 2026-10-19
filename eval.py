"""Evaluation script for the CogniSphere agent API.

Sends a fixed set of test questions to the running API (/chat), checks which
tools the agent used and what the answer contains, then prints a pass rate and
saves details to eval_results.json.

Usage (API must be running, locally or deployed):
    python eval.py                                   # tests http://localhost:8000
    python eval.py --url https://your-api.onrender.com
    python eval.py --only policy                     # run only cases whose id contains "policy"

Groq's free tier has a low tokens-per-minute limit, so the script waits between
questions (--delay) and retries when it gets a rate-limit style error.
"""

import argparse
import json
import os
import re
import time
import uuid
from collections import defaultdict

import requests

# ---------------------------------------------------------------------------
# Test cases
#   expected_tools : tools that must appear in tools_used.  [] means NO tool may be used.
#                    Leave the key out to skip the tool check.
#   contains_any   : answer must contain at least one of these (case-insensitive)
#   contains_all   : answer must contain every one of these (case-insensitive)
#   regex          : answer must match this pattern (case-insensitive)
#   not_contains   : answer must contain none of these
#   turns          : optional list of earlier messages sent in the same session first;
#                    only the final "question" is graded.
# ---------------------------------------------------------------------------
CASES = [
    # --- policy questions (document_search) ---
    {"id": "policy-expense-500", "category": "policy",
     "question": "Tell me about expenses above $500",
     "expected_tools": ["document_search"],
     "contains_any": ["pre-approval", "pre approval", "approval"]},
    {"id": "policy-receipt-deadline", "category": "policy",
     "question": "What is the deadline to submit expense receipts?",
     "expected_tools": ["document_search"],
     "contains_any": ["15 days", "15 calendar days", "fifteen days"]},
    {"id": "policy-reimbursement-time", "category": "policy",
     "question": "How long does reimbursement take?",
     "expected_tools": ["document_search"],
     "contains_any": ["10 working days", "10 business days", "ten working days"]},
    {"id": "policy-working-hours", "category": "policy",
     "question": "What are the working hours?",
     "expected_tools": ["document_search"],
     "contains_all": ["9:30", "6:30"]},
    {"id": "policy-leave-notice", "category": "policy",
     "question": "How early must leave requests be submitted?",
     "expected_tools": ["document_search"],
     "contains_any": ["3 working days", "three working days", "3 days"]},
    {"id": "policy-reviews", "category": "policy",
     "question": "When are performance reviews held?",
     "expected_tools": ["document_search"],
     "contains_all": ["june", "december"]},
    {"id": "policy-incident", "category": "policy",
     "question": "How fast must a security incident be reported?",
     "expected_tools": ["document_search"],
     "contains_any": ["1 hour", "one hour", "within an hour"]},

    # --- employee tools ---
    {"id": "employee-role", "category": "employee",
     "question": "What is Arjun Mehta's role?",
     "expected_tools": ["employee_lookup"],
     "contains_any": ["ml engineer"]},
    {"id": "employee-email", "category": "employee",
     "question": "What is Jane Smith's email?",
     "expected_tools": ["employee_lookup"],
     "contains_any": ["jane@company.com"]},
    {"id": "employee-count-sales", "category": "employee",
     "question": "How many employees are in Sales?",
     "expected_tools": ["employee_count_by_department"],
     "regex": r"\b1\b|\bone\b"},
    {"id": "employee-count-zero", "category": "employee",
     "question": "How many employees are in Marketing?",
     "expected_tools": ["employee_count_by_department"],
     "regex": r"\b0\b|\bno\b|\bnone\b|\bzero\b"},

    # --- calculation and multi-step chaining ---
    {"id": "calc-percent-of", "category": "calculation",
     "question": "What is 15% of 200?",
     "expected_tools": ["percentage_calculation"],
     "contains_any": ["30"]},
    # TODO: once you confirm the name of your "what percent is X of Y" tool, add it
    # to expected_tools below, e.g. ["employee_count_by_department", "percentage_of_calculation"].
    {"id": "chain-engineering-percent", "category": "chaining",
     "question": "What percentage of employees are in Engineering?",
     "expected_tools": ["employee_count_by_department"],
     "regex": r"66\.?6|67"},

    # --- out-of-scope (should refuse, with no tool calls) ---
    {"id": "out-of-scope-cricket", "category": "out_of_scope",
     "question": "Who won the cricket world cup?",
     "expected_tools": [],
     "contains_any": ["don't know", "outside what i can help"]},
    {"id": "out-of-scope-capital", "category": "out_of_scope",
     "question": "What is the capital of France?",
     "expected_tools": [],
     "contains_any": ["don't know", "outside what i can help"]},

    # --- memory ---
    {"id": "memory-follow-up", "category": "memory",
     "turns": ["What department is John Doe in?"],
     "question": "What's his email?",
     "contains_any": ["john@company.com"]},
    {"id": "memory-isolated-session", "category": "memory",
     "question": "What's his email?",
     "not_contains": ["john@company.com"]},
]


def norm(text: str) -> str:
    """Lowercase and normalise curly apostrophes so comparisons are stable."""
    return text.replace("’", "'").replace("‘", "'").lower()


def ask(url: str, message: str, session_id: str, timeout: int, retries: int = 3):
    """POST one message to /chat. Retries on timeouts and rate-limit style errors."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                f"{url}/chat",
                json={"message": message, "session_id": session_id},
                timeout=timeout,
            )
            if r.status_code == 200:
                return r.json(), None
            last_error = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code not in (429, 502, 503, 504):
                break
        except requests.RequestException as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(20 * attempt)  # back off; free-tier limits reset per minute
    return None, last_error


def check(case: dict, answer: str, tools: list) -> list:
    """Return a list of problems. An empty list means the case passed."""
    problems = []
    a = norm(answer)

    expected = case.get("expected_tools")
    if expected is not None:
        if expected == []:
            if tools:
                problems.append(f"expected no tool calls, got {tools}")
        else:
            missing = [t for t in expected if t not in tools]
            if missing:
                problems.append(f"missing tool(s) {missing}, used {tools}")

    if case.get("contains_any") and not any(norm(s) in a for s in case["contains_any"]):
        problems.append(f"answer has none of {case['contains_any']}")
    if case.get("contains_all"):
        absent = [s for s in case["contains_all"] if norm(s) not in a]
        if absent:
            problems.append(f"answer is missing {absent}")
    if case.get("regex") and not re.search(case["regex"], a, re.IGNORECASE):
        problems.append(f"answer does not match /{case['regex']}/")
    for s in case.get("not_contains", []):
        if norm(s) in a:
            problems.append(f"answer should not contain '{s}'")
    return problems


def run_case(url: str, case: dict, timeout: int, delay: float) -> dict:
    session_id = f"eval-{uuid.uuid4()}"  # fresh session per case so cases don't leak into each other
    started = time.time()

    for earlier in case.get("turns", []):
        _, err = ask(url, earlier, session_id, timeout)
        if err:
            return {"id": case["id"], "category": case["category"], "passed": False,
                    "problems": [f"setup turn failed: {err}"], "answer": "", "tools_used": [],
                    "seconds": round(time.time() - started, 1)}
        time.sleep(delay)

    data, err = ask(url, case["question"], session_id, timeout)
    seconds = round(time.time() - started, 1)
    if err:
        return {"id": case["id"], "category": case["category"], "passed": False,
                "problems": [f"request failed: {err}"], "answer": "", "tools_used": [],
                "seconds": seconds}

    problems = check(case, data["answer"], data["tools_used"])
    return {"id": case["id"], "category": case["category"], "passed": not problems,
            "problems": problems, "answer": data["answer"],
            "tools_used": data["tools_used"], "seconds": seconds}


def main():
    parser = argparse.ArgumentParser(description="Evaluate the CogniSphere agent API")
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8000"))
    parser.add_argument("--delay", type=float, default=15,
                        help="seconds to wait between questions (Groq free-tier limits)")
    parser.add_argument("--timeout", type=int, default=120,
                        help="seconds to wait for one answer (a sleeping Render service is slow)")
    parser.add_argument("--only", default="", help="run only cases whose id contains this text")
    parser.add_argument("--min-pass", type=float, default=0.0,
                        help="exit with code 1 if the pass rate (0-1) is below this")
    args = parser.parse_args()

    url = args.url.rstrip("/")
    cases = [c for c in CASES if args.only in c["id"]]
    print(f"Testing {url} with {len(cases)} cases\n")

    try:
        requests.get(f"{url}/health", timeout=args.timeout)  # wakes a sleeping service
    except requests.RequestException as exc:
        print(f"Cannot reach {url}/health: {exc}")
        raise SystemExit(2)

    results = []
    for i, case in enumerate(cases, 1):
        res = run_case(url, case, args.timeout, args.delay)
        results.append(res)
        print(f"[{i:>2}/{len(cases)}] {'PASS' if res['passed'] else 'FAIL'}  {res['id']}  ({res['seconds']}s)")
        for p in res["problems"]:
            print(f"        - {p}")
        if not res["passed"] and res["answer"]:
            print(f"        answer: {res['answer'][:160]!r}")
        if i < len(cases):
            time.sleep(args.delay)

    passed = sum(r["passed"] for r in results)
    rate = passed / len(results) if results else 0.0

    by_cat = defaultdict(lambda: [0, 0])
    for r in results:
        by_cat[r["category"]][1] += 1
        by_cat[r["category"]][0] += r["passed"]

    print("\n=== Summary ===")
    for cat, (ok, total) in by_cat.items():
        print(f"{cat:<14} {ok}/{total}")
    print(f"{'OVERALL':<14} {passed}/{len(results)}  ({rate:.0%})")

    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump({"url": url, "pass_rate": rate, "results": results}, f, indent=2)
    print("\nDetails saved to eval_results.json")

    if rate < args.min_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
