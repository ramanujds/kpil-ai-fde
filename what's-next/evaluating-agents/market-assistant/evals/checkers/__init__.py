from evals.checkers import outcome, trajectory
from evals.context import CaseRun, CheckResult


def run_spec(spec, registry: dict, ctx: CaseRun) -> CheckResult:
    """A spec is {check_name: params}: params is a dict (keyword args) or a single value."""
    (name, params), = spec.items()
    fn = registry[name]
    return fn(ctx, **params) if isinstance(params, dict) else fn(ctx, params)


def run_outcome(ctx: CaseRun) -> list[CheckResult]:
    return [run_spec(s, outcome.CHECKS, ctx) for s in ctx.case.get("outcome", [])]


def run_trajectory(ctx: CaseRun) -> list[CheckResult]:
    universal = [fn(ctx) for fn in trajectory.UNIVERSAL]
    return universal + [run_spec(s, trajectory.CHECKS, ctx) for s in ctx.case.get("trajectory", [])]
