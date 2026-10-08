"""The guardrails: plain Python rules that sit around the model.

Nothing in this file calls an LLM or LangChain. That is the point: these are hard
guardrails, enforced in code, so the model cannot talk its way past them. They can
be tested on their own (see test_guardrails.py).
"""

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Settings. Change these to see the guardrails react.
# ---------------------------------------------------------------------------

MAX_INPUT_CHARS = 500  # longest question we accept
MAX_ROUNDS = 5  # model calls per question (the step cap)
MAX_TOOL_CALLS = 6  # tool requests per question
MAX_TICKETS_PER_RUN = 2  # count limit on a medium-risk tool
MAX_REFUND = 500  # amount limit: anything above is blocked outright

# Permissions: every tool the agent may use, sorted by risk. A tool that is not
# listed here does not run, whatever the model asks for.
RISK = {
    "get_order_status": "low",  # read only: allow and log
    "create_support_ticket": "medium",  # reversible action: allow within a limit
    "issue_refund": "high",  # hard to undo: ask a human first
}

# Phrases that signal someone is trying to override the agent's rules. A short list
# like this is easy to get around, so treat it as one thin layer, not the defence.
OVERRIDE_PHRASES = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore your instructions",
    "ignore your rules",
    "disregard your instructions",
    "reveal your system prompt",
]

CARD_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,15}\b")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


@dataclass
class RunState:
    """What has happened so far in one question. Counters live here, not in the model."""

    tool_calls: int = 0
    tickets: int = 0
    events: list = field(default_factory=list)  # the trace of the run

    def log(self, tag: str, message: str) -> None:
        self.events.append((tag, message))
        print(f"  [{tag}] {message}")


@dataclass
class Decision:
    """The verdict on one tool request: allow, approve (ask a human) or block."""

    action: str
    message: str = ""


# ---------------------------------------------------------------------------
# Layer 1: input checks
# ---------------------------------------------------------------------------


def check_input(text: str) -> tuple[bool, str]:
    """Return (ok, text). If not ok, text is the message to show the user.

    If ok, text is the cleaned question: card numbers are masked before the model
    ever sees them.
    """
    text = text.strip()
    if not text:
        return False, "Please type a question."
    if len(text) > MAX_INPUT_CHARS:
        return False, f"That message is too long (limit {MAX_INPUT_CHARS} characters)."
    lowered = text.lower()
    if any(phrase in lowered for phrase in OVERRIDE_PHRASES):
        return False, "I can't help with that request."
    return True, CARD_PATTERN.sub("[card number removed]", text)


# ---------------------------------------------------------------------------
# Layer 2: tool permissions and limits
# ---------------------------------------------------------------------------


def check_tool_call(name: str, args: dict, state: RunState) -> Decision:
    """Decide what happens to one tool request: allow, approve or block."""
    risk = RISK.get(name)
    if risk is None:
        return Decision("block", f"The tool '{name}' is not available.")

    if state.tool_calls >= MAX_TOOL_CALLS:
        return Decision("block", f"Tool limit reached ({MAX_TOOL_CALLS} per question). Stop and answer with what you have.")

    # Tool-specific limits.
    if name == "issue_refund":
        amount = args.get("amount", 0)
        if not isinstance(amount, (int, float)) or amount <= 0:
            return Decision("block", "The refund amount must be a number above zero.")
        if amount > MAX_REFUND:
            return Decision(
                "block",
                f"Refunds above {MAX_REFUND} are not allowed here. "
                "Create a support ticket so a manager can review it.",
            )
    if name == "create_support_ticket" and state.tickets >= MAX_TICKETS_PER_RUN:
        return Decision("block", f"Ticket limit reached ({MAX_TICKETS_PER_RUN} per question).")

    # Risk decides the default control.
    if risk == "high":
        return Decision("approve")
    return Decision("allow")


# ---------------------------------------------------------------------------
# Layer 3: checks on what comes back and what goes out
# ---------------------------------------------------------------------------


def looks_like_injection(text: str) -> bool:
    """Flag tool results that contain instruction-like text (a weak, early warning)."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in OVERRIDE_PHRASES)


def check_output(text: str) -> str:
    """Mask card numbers and email addresses in the final answer."""
    text = CARD_PATTERN.sub("[card number removed]", text)
    text = EMAIL_PATTERN.sub("[email removed]", text)
    return text.strip() or "Sorry, I could not produce an answer. Please try again."
