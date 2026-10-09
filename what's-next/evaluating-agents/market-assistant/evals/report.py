"""Summarise a results file: pass rates by category, reliability (pass^k), cost, invalid calls, and every failure.

    uv run --group evals python -m evals.report [results/run-....jsonl]   # default: latest run
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).parent
NAMES = yaml.safe_load((HERE / "datasets" / "cases.yaml").read_text())["categories"]


def _rate(flags: list[bool]) -> str:
    return f"{sum(flags) / len(flags):.0%}" if flags else "-"


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def table(title: str, groups: dict[str, list[dict]]) -> None:
    print(f"{title:<26}{'runs':>5}{'outcome':>9}{'traject.':>9}{'judges':>8}{'SUCCESS':>9}{'steps':>7}{'llm':>5}{'tokens':>8}")
    for name, recs in groups.items():
        judged = [r["judge_pass"] for r in recs if r["judge_pass"] is not None]
        print(
            f"{name:<26}{len(recs):>5}{_rate([r['outcome_pass'] for r in recs]):>9}"
            f"{_rate([r['trajectory_pass'] for r in recs]):>9}{_rate(judged):>8}"
            f"{_rate([r['success'] for r in recs]):>9}"
            f"{_mean([r['metrics']['steps'] for r in recs]):>7.1f}{_mean([r['metrics']['llm_calls'] for r in recs]):>5.1f}"
            f"{_mean([r['metrics']['input_tokens'] + r['metrics']['output_tokens'] for r in recs]):>8.0f}"
        )


def report(path: Path | None = None) -> None:
    path = Path(path) if path else max((HERE / "results").glob("run-*.jsonl"))
    recs = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    print(f"Results: {path.name}   agent={recs[0]['agent_model']}  judge={next((r['judge_model'] for r in recs if r['judge_model']), 'not run')}  temperature={recs[0]['temperature']}\n")

    groups = defaultdict(list)
    for r in recs:
        groups[f"{r['category']}: {NAMES.get(r['category'], '')}"].append(r)
    table("By category", dict(sorted(groups.items())))
    print()
    table("Overall", {"all cases": recs})

    # reliability: only meaningful with several runs per case
    by_case = defaultdict(list)
    for r in recs:
        by_case[r["case_id"]].append(r["success"])
    k = max(len(v) for v in by_case.values())
    if k > 1:
        print(f"\nReliability over k={k} runs per case ({len(by_case)} cases):")
        print(f"  mean success rate : {_rate([s for v in by_case.values() for s in v])}")
        print(f"  pass@{k} (any run)  : {_rate([any(v) for v in by_case.values()])}   <- can it ever do it?")
        print(f"  pass^{k} (all runs) : {_rate([all(v) for v in by_case.values()])}   <- can you rely on it?")

    # path quality
    steps = [s for r in recs for s in r["steps"]]
    kinds = Counter(s["error_kind"] for s in steps if s["error"])
    print(f"\nTool calls: {len(steps)}   errors: {sum(kinds.values())} ({_rate([s['error'] for s in steps])})   by kind: {dict(kinds) or 'none'}")
    print(f"Redundant (identical repeated) calls: {sum(r['metrics']['redundant_calls'] for r in recs)}")
    pr = [(r['metrics']['tool_precision'], r['metrics']['tool_recall']) for r in recs if 'tool_precision' in r['metrics']]
    if pr:
        print(f"Tool precision / recall (cases with expected_tools): {_mean([p for p, _ in pr]):.2f} / {_mean([r for _, r in pr]):.2f}")
    eff = [r['metrics']['step_efficiency'] for r in recs if r['metrics'].get('step_efficiency')]
    if eff:
        print(f"Step efficiency (steps / minimal steps, 1.0 = ideal): {_mean(eff):.2f}")
    jerr = sum(r["judge_errors"] for r in recs)
    if jerr:
        print(f"WARNING: {jerr} judge calls failed to produce a verdict (counted as not-passed, see 'error' in the file)")

    failures = [r for r in recs if not r["success"]]
    print(f"\nFailures: {len(failures)} of {len(recs)} runs")
    for r in failures:
        print(f"\n  {r['case_id']} (run {r['rep'] + 1})  tools: {[s['tool'] for s in r['steps']]}")
        for c in r["outcome"] + r["trajectory"]:
            if not c["passed"]:
                print(f"    x {c['name']}: {c['detail']}")
        for j in r["judges"]:
            if not j["passed"]:
                print(f"    x judge:{j['name']}: {j['error'] or j['reasoning'][:200]}")
        print(f"    answer: {r['answer'][:200]!r}")


if __name__ == "__main__":
    report(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
