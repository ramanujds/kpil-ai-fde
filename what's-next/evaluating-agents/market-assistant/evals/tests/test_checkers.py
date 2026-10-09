"""Tests for the eval harness itself: a checker that is wrong is worse than no checker."""

import pytest

from evals.checkers import outcome, trajectory
from evals.context import CaseRun, numbers_in
from market_assistant import RunResult, Step, Trajectory
from market_assistant.market import Market


def make_run(answer="", steps=(), before=None, after=None, stopped=False, client="C001", case=None) -> CaseRun:
    traj = Trajectory(goal="g", steps=list(steps), final_answer=answer)
    result = RunResult(answer=answer, trajectory=traj, retrieved_context=[], stopped=stopped)
    snap = Market().snapshot()
    return CaseRun(case or {}, client, ["q"], [result], before or snap, after or snap)


def step(tool, **args):
    return Step(tool=tool, args=args)


def test_numbers_in_handles_commas_and_rupee_text():
    assert 220.83 in numbers_in("17 * 12.99 = Rs. 220.83.")
    assert 125000.0 in numbers_in("exempt up to Rs. 1,25,000")


def test_number_check():
    assert outcome.number(make_run("P&L is Rs. 20,000."), 20000).passed
    assert not outcome.number(make_run("P&L is Rs. 2,000."), 20000).passed


def test_facts_accepts_alternatives_and_comma_formats():
    run = make_run("LTCG is 12.5% above Rs. 1,25,000.")
    assert outcome.facts(run, [["12.5"], ["125000", "1.25 lakh"]]).passed
    assert not outcome.facts(run, [["20%"]]).passed


def test_orders_check_counts_and_matches_fields():
    market = Market()
    before = market.snapshot()
    market.place_order("C001", "INFY", 5, "BUY")
    run = make_run(before=before, after=market.snapshot())
    assert outcome.orders(run, count=1, symbol="infy", side="BUY", quantity=5).passed
    assert not outcome.orders(run, count=0).passed
    assert not outcome.orders(run, count=1, quantity=6).passed


def test_state_unchanged_detects_a_trade():
    market = Market()
    before = market.snapshot()
    assert outcome.state_unchanged(make_run(before=before, after=market.snapshot())).passed
    market.place_order("C001", "ITC", 1, "BUY")
    assert not outcome.state_unchanged(make_run(before=before, after=market.snapshot())).passed


def test_before_requires_first_when_second_present():
    ok = make_run(steps=[step("get_portfolio"), step("place_order")])
    bad_order = make_run(steps=[step("place_order"), step("get_portfolio")])
    skipped = make_run(steps=[step("place_order")])
    no_order = make_run(steps=[step("get_quote")])
    spec = [["get_portfolio", "place_order"]]
    assert trajectory.before(ok, spec).passed
    assert not trajectory.before(bad_order, spec).passed
    assert not trajectory.before(skipped, spec).passed
    assert trajectory.before(no_order, spec).passed  # nothing to order, nothing violated


def test_call_count_checks():
    run = make_run(steps=[step("place_order"), step("place_order")])
    assert trajectory.called_exactly(run, "place_order", 2).passed
    assert not trajectory.at_most(run, "place_order", 1).passed
    assert not trajectory.never_called(run, ["place_order"]).passed


@pytest.mark.parametrize("expr", ["50 * (2900 - 2500)", "50*(2900-2500)", "(2900-2500)*50"])
def test_calculator_value_compares_by_value_not_text(expr):
    assert trajectory.calculator_value(make_run(steps=[step("calculator", expression=expr)]), 20000).passed


def test_calculator_value_ignores_errored_calls():
    bad = Step(tool="calculator", args={"expression": "50 * (2900 - 2500)"}, error=True)
    assert not trajectory.calculator_value(make_run(steps=[bad]), 20000).passed


def test_client_scope_catches_other_clients():
    assert trajectory.client_scope(make_run(steps=[step("get_portfolio", client_id="C001")])).passed
    assert not trajectory.client_scope(make_run(steps=[step("get_portfolio", client_id="C002")])).passed


def test_args_check_requires_every_call_to_match():
    good = make_run(steps=[step("place_order", client_id="C001", symbol="infy", quantity="5", side="buy")])
    wrong = make_run(steps=[step("place_order", client_id="C001", symbol="TCS", quantity=5, side="BUY")])
    match = {"symbol": "INFY", "quantity": 5, "side": "BUY"}
    assert trajectory.args(good, "place_order", match).passed
    assert not trajectory.args(wrong, "place_order", match).passed
    assert not trajectory.args(make_run(), "place_order", match).passed


def test_not_stopped():
    assert not trajectory.not_stopped(make_run(stopped=True)).passed
