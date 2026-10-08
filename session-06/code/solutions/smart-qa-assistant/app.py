"""Smart QA Assistant in the terminal. The assistant itself lives in assistant.py."""

import assistant
import config


def ask_person(request: dict) -> dict:
    """Show the pending action and ask the user to approve it. Returns a decision for the agent."""
    print("\n  ----- APPROVAL NEEDED -----")
    print(f"  Action : {request['name']}")
    for key, value in request["args"].items():
        print(f"  {key:<7}: {value}")
    try:
        answer = input("  Create this ticket? [y/N]: ").strip().lower()
    except EOFError:
        answer = ""  # nobody there: the safe default is to decline
    print("  ---------------------------\n")
    return assistant.APPROVE if answer in ("y", "yes") else assistant.reject()


def answer(question: str, thread_id: str) -> str:
    """Ask one question, handling approval pauses, and return the text to print."""
    turn = assistant.ask(question, thread_id)
    while turn.pending:  # the agent paused: ask the person, then let it continue
        turn = assistant.resume([ask_person(r) for r in turn.pending], thread_id)
    if turn.kind == "faq":
        return f"{turn.text}\n(FAQ answer. Source: {turn.sources[0]})"
    if turn.sources:
        return f"{turn.text}\n(Retrieved from: {'; '.join(turn.sources)})"
    return turn.text


def main() -> None:
    thread_number = 1
    print(f"Smart QA Assistant (model: {config.CHAT_MODEL}). Signed in as {config.CURRENT_USER}.")
    print("Type 'reset' to start a new conversation, 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if question.lower() == "reset":
            thread_number += 1  # a new thread id is a fresh, empty memory
            print("Conversation cleared.\n")
            continue
        print("\nAI:", answer(question, f"chat-{thread_number}"), "\n")


if __name__ == "__main__":
    main()
