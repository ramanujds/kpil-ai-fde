"""The dataset must be well-formed, and its gold numbers must match the sandbox."""

import yaml
import pytest

from evals.checkers import outcome, trajectory
from evals.faults import FAULTS
from evals.judges.judge import JUDGES
from evals.run_suite import HERE, load_cases
from evals.runner import judge_specs
from market_assistant import Market

CASES = load_cases(HERE / "datasets" / "cases.yaml")


def test_ids_unique():
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_case_is_well_formed(case):
    assert case["category"] in yaml.safe_load((HERE / "datasets" / "cases.yaml").read_text())["categories"]
    assert ("input" in case) != ("turns" in case)
    assert case.get("fault") is None or case["fault"] in FAULTS
    for spec in case.get("outcome", []):
        (name,) = spec
        assert name in outcome.CHECKS, name
    for spec in case.get("trajectory", []):
        (name,) = spec
        assert name in trajectory.CHECKS, name
    for name, _ in judge_specs(case):
        assert name in JUDGES, name


def test_trade_gold_numbers_match_sandbox():
    """E1-E4 expected cash values come from the sandbox, not hand arithmetic."""
    expected = {"E1": ("INFY", 5, "BUY"), "E2": ("TCS", 10, "BUY"), "E3": ("RELIANCE", 50, "SELL"), "E4": ("INFY", 20, "SELL")}
    for case in CASES:
        if case["id"] in expected:
            market = Market()
            market.place_order("C001", *expected[case["id"]])
            cash = next(c["cash"] for c in case["outcome"] if "cash" in c)
            assert abs(market.snapshot()["clients"]["C001"] - cash["value"]) < 0.01, case["id"]
