"""Run the eval suite.

    uv run --group evals python -m evals.run_suite                       # all cases, 1 run each, code checks only
    uv run --group evals python -m evals.run_suite --ids A1,E1 --judges  # specific cases, with LLM judges
    uv run --group evals python -m evals.run_suite --category E,F -k 5 --temperature 0.4   # reliability (pass^k)

With temperature 0 the repeated runs are (nearly) identical; use --temperature > 0 with -k > 1 to measure reliability.
"""

import argparse
import json
import time
from pathlib import Path

import yaml

from evals.judges.judge import get_judge_llm
from evals.report import report
from evals.runner import evaluate
from market_assistant.rag import Knowledge

HERE = Path(__file__).parent


def load_cases(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text())["cases"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cases", type=Path, default=HERE / "datasets" / "cases.yaml")
    p.add_argument("--ids", help="comma-separated case ids")
    p.add_argument("--category", help="comma-separated categories, e.g. E,F")
    p.add_argument("-k", type=int, default=1, help="runs per case")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--model", help="agent model (default llama3:8b)")
    p.add_argument("--judges", action="store_true", help="also run the LLM judges (slower)")
    p.add_argument("--out", type=Path, default=HERE / "results")
    args = p.parse_args()

    cases = load_cases(args.cases)
    if args.ids:
        wanted = set(args.ids.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    if args.category:
        wanted = set(args.category.split(","))
        cases = [c for c in cases if c["category"] in wanted]
    if not cases:
        raise SystemExit("no cases selected")

    knowledge = Knowledge()  # index once; every run gets a fresh Market
    judge_llm = get_judge_llm() if args.judges else None
    args.out.mkdir(exist_ok=True)
    path = args.out / f"run-{time.strftime('%Y%m%d-%H%M%S')}.jsonl"

    print(f"{len(cases)} cases x {args.k} runs -> {path}\n")
    with path.open("w") as f:
        for case in cases:
            for rep in range(args.k):
                rec = evaluate(case, rep, knowledge, model=args.model, temperature=args.temperature, seed=args.seed, judge_llm=judge_llm)
                f.write(json.dumps(rec, default=str) + "\n")
                f.flush()
                failed = [c["name"] for c in rec["outcome"] + rec["trajectory"] if not c["passed"]]
                failed += [j["name"] for j in rec["judges"] if not j["passed"]]
                print(f"{'PASS' if rec['success'] else 'FAIL'}  {case['id']:<4} run {rep + 1}/{args.k}  {rec['latency_s']:>5}s  {', '.join(failed)}")

    print()
    report(path)


if __name__ == "__main__":
    main()
