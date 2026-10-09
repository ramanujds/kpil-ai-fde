"""Trajectory checks (note 03): the path - tools, arguments, order, necessity, efficiency. Constraints, not exact scripts."""

from collections import Counter

from evals.context import CaseRun, CheckResult
from market_assistant.tools import evaluate_expression


def _calls(ctx: CaseRun, tool: str):
    return [s for s in ctx.steps if s.tool == tool]


def called(ctx: CaseRun, value: list[str]) -> CheckResult:
    missing = [t for t in value if not _calls(ctx, t)]
    return CheckResult(f"called({','.join(value)})", not missing, f"never called: {missing}" if missing else "")


def never_called(ctx: CaseRun, value: list[str]) -> CheckResult:
    hit = [t for t in value if _calls(ctx, t)]
    return CheckResult(f"never_called({','.join(value)})", not hit, f"called: {hit}" if hit else "")


def called_exactly(ctx: CaseRun, tool: str, n: int) -> CheckResult:
    got = len(_calls(ctx, tool))
    return CheckResult(f"called_exactly({tool},{n})", got == n, f"called {got} times")


def at_most(ctx: CaseRun, tool: str, n: int) -> CheckResult:
    got = len(_calls(ctx, tool))
    return CheckResult(f"at_most({tool},{n})", got <= n, f"called {got} times")


def before(ctx: CaseRun, value: list[list[str]]) -> CheckResult:
    """For each [first, second]: if `second` is ever called, `first` was called earlier (note 03 semantics)."""
    tools = ctx.tools
    bad = []
    for first, second in value:
        if second in tools and (first not in tools or tools.index(first) > tools.index(second)):
            bad.append(f"{first} before {second}")
    return CheckResult("before", not bad, f"violated: {bad}" if bad else "")


def max_steps(ctx: CaseRun, value: int) -> CheckResult:
    return CheckResult(f"max_steps({value})", len(ctx.steps) <= value, f"{len(ctx.steps)} steps")


def calculator_value(ctx: CaseRun, value: float, tol: float = 0.01) -> CheckResult:
    """Some successful calculator call evaluates to `value`. Compares by value, not by expression text."""
    got = []
    for s in _calls(ctx, "calculator"):
        if s.error:
            continue
        try:
            got.append(evaluate_expression(str(s.args.get("expression", ""))))
        except Exception:  # noqa: BLE001 - an unparseable expression simply does not count
            continue
    ok = any(abs(g - value) <= tol for g in got)
    return CheckResult(f"calculator_value({value})", ok, f"calculator results: {got}")


def args(ctx: CaseRun, tool: str, match: dict) -> CheckResult:
    """The tool was called, and EVERY call used the given argument values (strings case-insensitive, numbers by value)."""
    calls = _calls(ctx, tool)
    if not calls:
        return CheckResult(f"args({tool})", False, "tool never called")

    def same(a, b):
        try:
            return abs(float(a) - float(b)) < 0.01
        except (TypeError, ValueError):
            return str(a).strip().upper() == str(b).strip().upper()

    bad = [s.args for s in calls if not all(same(s.args.get(k), v) for k, v in match.items())]
    return CheckResult(f"args({tool})", not bad, f"calls not matching {match}: {bad}" if bad else "")


# ---- universal checks, applied to every case ----------------------------------------------


def not_stopped(ctx: CaseRun) -> CheckResult:
    return CheckResult("not_stopped", not ctx.stopped, "hit max_steps without a final answer")


def client_scope(ctx: CaseRun) -> CheckResult:
    """Every tool call that names a client_id uses the logged-in client."""
    bad = [s.args["client_id"] for s in ctx.steps if "client_id" in s.args and str(s.args["client_id"]).upper() != ctx.client_id]
    return CheckResult("client_scope", not bad, f"used client ids {bad}, logged in as {ctx.client_id}" if bad else "")


UNIVERSAL = [not_stopped, client_scope]
CHECKS = {f.__name__: f for f in (called, never_called, called_exactly, at_most, before, max_steps, calculator_value, args)}


# ---- metrics (reported, not pass/fail) ----------------------------------------------------


def metrics(ctx: CaseRun) -> dict:
    steps = ctx.steps
    used = {s.tool for s in steps if s.tool != "<unparsed>"}
    expected = set(ctx.case.get("expected_tools", []))
    out = {
        "steps": len(steps),
        "llm_calls": ctx.llm_calls,
        "input_tokens": ctx.input_tokens,
        "output_tokens": ctx.output_tokens,
        "error_kinds": dict(Counter(s.error_kind for s in steps if s.error)),
        "redundant_calls": sum(c - 1 for c in Counter((s.tool, str(sorted(s.args.items()))) for s in steps).values()),
    }
    if expected:
        hit = used & expected
        out["tool_precision"] = len(hit) / len(used) if used else 0.0
        out["tool_recall"] = len(hit) / len(expected)
        out["step_efficiency"] = len(steps) / len(expected) if steps else None  # 1.0 = minimal path
    return out
