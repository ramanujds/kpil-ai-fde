"""Calibrate the judges against human labels (note 04, section 7).

    uv run --group evals python -m evals.judges.calibrate [--judge faithfulness]

calibration.yaml holds labelled examples: judge, label (pass/fail), question, answer, evidence, params.
Add REAL agent outputs that you labelled yourself; the planted examples are only a starting point.
"""

import argparse
from pathlib import Path

import yaml

from evals.judges.judge import JUDGE_MODEL, JudgeInput, get_judge_llm, run_judge

PATH = Path(__file__).with_name("calibration.yaml")


def cohens_kappa(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    agree = sum(h == j for h, j in pairs) / n
    p_h = sum(h for h, _ in pairs) / n
    p_j = sum(j for _, j in pairs) / n
    expected = p_h * p_j + (1 - p_h) * (1 - p_j)
    return 1.0 if expected == 1 else (agree - expected) / (1 - expected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", help="only calibrate this judge")
    args = parser.parse_args()

    items = [i for i in yaml.safe_load(PATH.read_text()) if not args.judge or i["judge"] == args.judge]
    llm = get_judge_llm()
    by_judge: dict[str, list[tuple[bool, bool]]] = {}
    errors = 0

    for item in items:
        inp = JudgeInput(item["question"], item["answer"], item.get("evidence", ""), item.get("params", {}))
        res = run_judge(item["judge"], inp, llm)
        human = item["label"] == "pass"
        if res.error:
            errors += 1
            print(f"ERROR  {item['judge']:<18} {item['id']}: {res.error}")
            continue
        by_judge.setdefault(item["judge"], []).append((human, res.passed))
        flag = "ok" if human == res.passed else "DISAGREE"
        print(f"{flag:<9}{item['judge']:<18} {item['id']:<28} human={'pass' if human else 'fail'} judge={'pass' if res.passed else 'fail'}")

    print(f"\nJudge model: {JUDGE_MODEL}   (judge errors excluded: {errors})")
    print(f"{'judge':<20}{'n':>3} {'agree':>7} {'kappa':>7} {'TPR':>6} {'TNR':>6}")
    for name, pairs in by_judge.items():
        pos = [j for h, j in pairs if h]
        neg = [j for h, j in pairs if not h]
        tpr = sum(pos) / len(pos) if pos else float("nan")
        tnr = sum(not j for j in neg) / len(neg) if neg else float("nan")
        agree = sum(h == j for h, j in pairs) / len(pairs)
        print(f"{name:<20}{len(pairs):>3} {agree:>7.0%} {cohens_kappa(pairs):>7.2f} {tpr:>6.0%} {tnr:>6.0%}")
    print("\nTNR (bad outputs the judge correctly fails) matters most: a lenient judge makes every dashboard look healthy.")


if __name__ == "__main__":
    main()
