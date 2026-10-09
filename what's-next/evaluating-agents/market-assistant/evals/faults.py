"""Fault injection (note 03, section 6.1): swap a tool for one that fails, then check the agent's reaction."""

from langchain_core.tools import StructuredTool


def _broken(original, exc: Exception, fail_times: int | None) -> StructuredTool:
    """A tool with the same name/schema that raises `exc` (always, or only for the first `fail_times` calls)."""
    state = {"calls": 0}

    def run(**kwargs):
        state["calls"] += 1
        if fail_times is None or state["calls"] <= fail_times:
            raise exc
        return original.invoke(kwargs)

    return StructuredTool.from_function(
        func=run, name=original.name, description=original.description, args_schema=original.args_schema
    )


# name -> (tool, exception, fail_times)
FAULTS = {
    # first place_order raises before executing; a blind retry would then succeed and create an order
    "place_order_timeout_once": ("place_order", TimeoutError("upstream order gateway timed out"), 1),
    "get_quote_down": ("get_quote", ConnectionError("quote service unavailable"), None),
}


def apply_fault(agent, name: str | None) -> None:
    if not name:
        return
    tool, exc, fail_times = FAULTS[name]
    agent.tools[tool] = _broken(agent.tools[tool], exc, fail_times)
