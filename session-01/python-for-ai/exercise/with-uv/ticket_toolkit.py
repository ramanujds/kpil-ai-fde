"""Ticket Triage Toolkit -- Day 1, Block 3: Python for AI.

A small set of functions ("tools") over a list of synthetic site/service
tickets. Each function is single-purpose and works on plain Python data
structures (lists, dicts) -- no LLM involved yet.

The TOOLS registry at the bottom gives each function a name and a
description. That is the same shape an AI agent later uses to decide
which function to call for a given request (Day 5). For now, you call
them yourself and read the output.

Fill in every TODO. See walkthrough.md for step-by-step guidance and
how to run this file.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TICKETS_FILE = Path(__file__).parent / "tickets.json"
REPORT_LIMIT = int(os.getenv("REPORT_LIMIT", "5"))
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def load_tickets(path: Path) -> list[dict]:
    """Read the JSON file at `path` and return a list of ticket dicts.

    Return an empty list if the file is missing or the JSON is malformed --
    do not let either error crash the program.
    """
    # TODO: open `path` in read mode and parse it with json.load(...).
    # TODO: catch FileNotFoundError -> print a friendly message, return [].
    # TODO: catch json.JSONDecodeError -> print a friendly message, return [].
    pass


def filter_by_status(tickets: list[dict], status: str) -> list[dict]:
    """Return only the tickets whose status matches `status` (case-insensitive)."""
    # TODO: use a list comprehension. Compare ticket["status"].lower() to status.lower().
    pass


def count_by_priority(tickets: list[dict]) -> dict:
    """Return counts like {"High": 3, "Medium": 2, "Low": 1}."""
    # TODO: start from {"High": 0, "Medium": 0, "Low": 0} and increment as you loop.
    pass


def format_ticket_summary(ticket: dict) -> str:
    """Return a one-line summary, for example:

    "[TCK-1042] HIGH - Electrical @ Site A - Residential Tower 3 (2 days open)"
    """
    # TODO: build this with an f-string using ticket["id"], ticket["priority"],
    # ticket["category"], ticket["site"], ticket["days_open"].
    pass


def top_priority_report(tickets: list[dict], limit: int = REPORT_LIMIT) -> list[str]:
    """Return formatted summaries for the `limit` highest-priority open tickets.

    Steps: filter to status == "Open", sort by priority (High before Medium
    before Low -- PRIORITY_ORDER above gives you the sort key), keep the
    first `limit`, and format each one with format_ticket_summary.
    """
    # TODO: implement using filter_by_status, sorted(..., key=...), and
    # format_ticket_summary.
    pass


# A tool registry: name -> (function, description).
# This is the exact shape an agent framework uses to pick a function to
# call for a given request. You will meet this pattern again on Day 5.
TOOLS = {
    "count_by_priority": (count_by_priority, "Count open tickets by priority level"),
    "filter_by_status": (filter_by_status, "Filter tickets by their status"),
    "top_priority_report": (
        top_priority_report,
        "List the top N highest-priority open tickets",
    ),
}


if __name__ == "__main__":
    tickets = load_tickets(TICKETS_FILE)
    report = top_priority_report(tickets)
    print(json.dumps(report, indent=2))
