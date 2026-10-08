"""The agent's tools. Three tools, three different jobs.

- search_documents  : read only. Answers "what is the rule?" using RAG.
- get_leave_balance : read only. Answers "what is MY situation?" from a (fake) HR system.
- create_support_ticket : a write. The agent asks for it, but app.py makes a person approve it.

All data is made up. Nothing here talks to a real system.
"""

from typing import Literal

from langchain_core.tools import tool

import config
import rag

# A fake HR system. Every employee's row is here, but the tool only ever reads the row
# of the signed-in user.
LEAVE_BALANCES = {
    "E101": {"name": "Ravi", "paid_total": 18, "paid_used": 12, "sick_total": 10, "sick_used": 0},
    "E102": {"name": "Asha", "paid_total": 18, "paid_used": 6, "sick_total": 10, "sick_used": 2},
    "E103": {"name": "Meera", "paid_total": 9, "paid_used": 3, "sick_total": 10, "sick_used": 5},
}

TICKETS = []  # tickets created in this run


@tool
def search_documents(question: str) -> str:
    """Search the company policy documents (leave, expenses, IT support). Use this for any
    question about a company rule or process. Pass a short, complete question that makes sense
    on its own, not a follow-up fragment.

    Args:
        question: The question to look up, for example "paid leave for part-time employees".
    """
    passages = rag.search(question)
    if not passages:
        return "NO_RESULTS: the documents do not cover this."
    return "\n\n".join(f"[Source: {p['source']}]\n{p['text']}" for p in passages)


@tool
def get_leave_balance() -> str:
    """Get the signed-in employee's own leave balance (paid and sick days used and remaining).
    Takes no input: it always looks up the person who is chatting."""
    row = LEAVE_BALANCES[config.CURRENT_USER]
    return (
        f"{row['name']}'s leave balance. "
        f"Paid leave: {row['paid_used']} used, {row['paid_total'] - row['paid_used']} remaining, {row['paid_total']} total. "
        f"Sick leave: {row['sick_used']} used, {row['sick_total'] - row['sick_used']} remaining, {row['sick_total']} total."
    )


@tool
def create_support_ticket(team: Literal["HR", "IT", "Finance"], summary: str) -> str:
    """Raise a support ticket for the signed-in employee. Use only when the employee asks for a
    ticket or request to be raised, or after they agree to one. A person confirms before it is created.

    Args:
        team: Which team should handle it: HR, IT or Finance.
        summary: One or two sentences describing the problem.
    """
    ticket_id = f"T-{1000 + len(TICKETS) + 1}"
    TICKETS.append({"id": ticket_id, "team": team, "summary": summary, "raised_by": config.CURRENT_USER})
    return f"Ticket {ticket_id} created for the {team} team."


ALL_TOOLS = [search_documents, get_leave_balance, create_support_ticket]
