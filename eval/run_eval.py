"""
Evaluation harness — runs the test question set against a running instance
of the API (local or deployed) and measures accuracy per category.

Usage:
    python eval/run_eval.py                          # tests http://127.0.0.1:8000
    python eval/run_eval.py --url https://your-app.onrender.com   # tests deployed version
"""
import argparse
import json
import os
import time
import requests

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "questions.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.md")


def run_eval(base_url: str):
    with open(QUESTIONS_PATH) as f:
        questions = json.load(f)

    results = []
    for q in questions:
        try:
            resp = requests.post(f"{base_url}/query", json={"question": q["question"]}, timeout=60)
            if resp.status_code != 200:
                answer = f"[ERROR {resp.status_code}: {resp.text}]"
            else:
                answer = resp.json().get("answer", "")
        except Exception as e:
            answer = f"[ERROR: {e}]"

        answer_lower = answer.lower()
        numeric_kws = [kw for kw in q["expected_keywords"] if kw.replace(".", "").isdigit()]
        other_kws = [kw for kw in q["expected_keywords"] if kw not in numeric_kws]

        numeric_ok = any(kw.lower() in answer_lower for kw in numeric_kws) if numeric_kws else True
        other_ok = all(kw.lower() in answer_lower for kw in other_kws) if other_kws else True
        passed = numeric_ok and other_ok

        results.append({
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "expected_keywords": q["expected_keywords"],
            "answer": answer,
            "passed": passed,
        })
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] #{q['id']} ({q['category']}): {q['question']}")
        time.sleep(3)

    return results


def write_report(results: list, base_url: str):
    categories = {}
    for r in results:
        categories.setdefault(r["category"], []).append(r)

    lines = [
        "# Evaluation Results",
        "",
        f"Tested against: `{base_url}`",
        "",
        "## Summary",
        "",
        "| Category | Passed | Total | Accuracy |",
        "|---|---|---|---|",
    ]

    total_passed, total_count = 0, 0
    for cat, items in categories.items():
        passed = sum(1 for i in items if i["passed"])
        total = len(items)
        total_passed += passed
        total_count += total
        lines.append(f"| {cat} | {passed} | {total} | {passed/total*100:.0f}% |")

    lines.append(f"| **Overall** | **{total_passed}** | **{total_count}** | **{total_passed/total_count*100:.0f}%** |")
    lines.append("")
    lines.append("## Details")
    lines.append("")

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"### [{status}] #{r['id']} ({r['category']})")
        lines.append(f"**Q:** {r['question']}")
        lines.append(f"**Expected keywords:** {', '.join(r['expected_keywords'])}")
        lines.append(f"**Answer:** {r['answer']}")
        lines.append("")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nReport written to {RESULTS_PATH}")
    print(f"Overall: {total_passed}/{total_count} ({total_passed/total_count*100:.0f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL of the running API")
    args = parser.parse_args()

    results = run_eval(args.url)
    write_report(results, args.url)