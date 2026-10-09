"""Run one case once: fresh sandbox, optional fault, all turns, then outcome / trajectory / judge checks."""

import time
from dataclasses import asdict

from evals.checkers import run_outcome, run_trajectory
from evals.checkers.trajectory import metrics
from evals.context import CaseRun
from evals.faults import apply_fault
from evals.judges.judge import JUDGE_MODEL, build_input, run_judge
from market_assistant import Market, build_agent


def judge_specs(case: dict) -> list[tuple[str, dict]]:
    out = []
    for j in case.get("judges", []):
        out.append((j, {}) if isinstance(j, str) else next(iter(j.items())))
    return out


def execute(case: dict, rep: int, knowledge, model: str | None, temperature: float, seed: int) -> CaseRun:
    client = case.get("client", "C001")
    market = Market(market_open=case.get("market_open", True))
    kwargs = {"model": model} if model else {}
    agent = build_agent(client_id=client, market=market, knowledge=knowledge, temperature=temperature, seed=seed + rep, **kwargs)
    apply_fault(agent, case.get("fault"))

    turns = case.get("turns") or [case["input"]]
    before = market.snapshot()
    history, results = [], []
    start = time.time()
    for turn in turns:
        result = agent.run(turn, history)
        history += result.turn
        results.append(result)
    return CaseRun(case, client, turns, results, before, market.snapshot(), latency_s=time.time() - start)


def evaluate(case: dict, rep: int, knowledge, *, model=None, temperature=0.0, seed=42, judge_llm=None) -> dict:
    ctx = execute(case, rep, knowledge, model, temperature, seed)
    outcome = run_outcome(ctx)
    traj = run_trajectory(ctx)

    judges = []
    if judge_llm is not None:
        for name, params in judge_specs(case):
            judges.append((name, run_judge(name, build_input(ctx, params), judge_llm)))

    outcome_pass = all(c.passed for c in outcome)
    traj_pass = all(c.passed for c in traj)
    judge_pass = None if not judges else all(j.passed for _, j in judges)
    judge_errors = sum(1 for _, j in judges if j.error)
    return {
        "case_id": case["id"],
        "category": case["category"],
        "rep": rep,
        "turns": ctx.turns,
        "answer": ctx.answer,
        "stopped": ctx.stopped,
        "steps": [asdict(s) for s in ctx.steps],
        "outcome": [asdict(c) for c in outcome],
        "trajectory": [asdict(c) for c in traj],
        "judges": [asdict(j) for _, j in judges],
        "outcome_pass": outcome_pass,
        "trajectory_pass": traj_pass,
        "judge_pass": judge_pass,
        "judge_errors": judge_errors,
        "success": outcome_pass and traj_pass and (judge_pass is not False),
        "metrics": metrics(ctx),
        "latency_s": round(ctx.latency_s, 1),
        "agent_model": model or "default",
        "judge_model": JUDGE_MODEL if judges else None,
        "temperature": temperature,
        "seed": seed + rep,
    }
