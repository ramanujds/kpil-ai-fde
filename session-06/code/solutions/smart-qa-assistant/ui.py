"""Smart QA Assistant in the browser, built with Streamlit. Run:  uv run streamlit run ui.py

The assistant itself lives in assistant.py. This file only draws the screen and passes
questions and approvals through. Streamlit re-runs this whole file on every click, so
everything that must survive (the chat, a pending approval) is kept in st.session_state.
"""

import json
import uuid
from pathlib import Path

import streamlit as st

import assistant
import config
import ingest
import rag

DOCS = Path("docs")
EXAMPLES = [
    "How many paid leave days do I get in a year?",
    "What about part-time staff?",
    "Can I claim a taxi ride home after a late shift?",
    "How many leave days have I used?",
    "What is the dress code for Mars?",
    "Raise a ticket for my broken laptop",
]

st.set_page_config(page_title="Smart QA Assistant", layout="centered")

# ---------------------------------------------------------------------------
# Session state: one thread id per browser session is the assistant's memory key.
# ---------------------------------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []  # what the chat window shows
    st.session_state.pending = []  # approval requests waiting for the user
    st.session_state.upload_key = 0  # changing this clears the file uploader


def new_conversation() -> None:
    st.session_state.thread_id = str(uuid.uuid4())  # a new thread id is a fresh, empty memory
    st.session_state.messages = []
    st.session_state.pending = []


def show_message(message: dict) -> None:
    """Draw one chat message with its small print (FAQ badge, tools used, sources)."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        notes = []
        if message.get("kind") == "faq":
            notes.append("FAQ answer (approved, no model call)")
        if message.get("tools"):
            notes.append("Tools used: " + ", ".join(message["tools"]))
        if message.get("sources"):
            notes.append("Sources: " + "; ".join(message["sources"]))
        for note in notes:
            st.caption(note)


def take_turn(turn: assistant.Turn) -> None:
    """Store the result of one step: either a reply, or an approval request to show."""
    if turn.pending:
        st.session_state.pending = turn.pending
    else:
        st.session_state.pending = []
        st.session_state.messages.append(
            {"role": "assistant", "content": turn.text, "kind": turn.kind, "tools": turn.tools, "sources": turn.sources}
        )


# ---------------------------------------------------------------------------
# Sidebar: who is signed in, example questions, and the admin tools.
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Smart QA Assistant")
    st.caption(f"Signed in as {config.CURRENT_USER}  |  model: {config.CHAT_MODEL}")
    st.button("New conversation", on_click=new_conversation, use_container_width=True)

    st.subheader("Try asking")
    for example in EXAMPLES:
        if st.button(example, key=f"ex-{example}", use_container_width=True):
            st.session_state.queued = example

    st.divider()
    st.subheader("Admin")
    st.caption("Demo only. A real system would show this to HR and IT staff only.")

    with st.expander("Documents", expanded=False):
        for path in sorted(DOCS.glob("*")):
            st.write(path.name)
        files = st.file_uploader(
            "Add or replace documents",
            type=["md", "txt"],
            accept_multiple_files=True,
            key=f"upload-{st.session_state.upload_key}",
        )
        if st.button("Save and re-index", disabled=not files, use_container_width=True):
            for file in files:
                (DOCS / file.name).write_bytes(file.getvalue())
            with st.spinner("Reading, splitting and embedding the documents..."):
                document_count, node_count = ingest.build_index()
                rag.reset()  # the old collection handle is stale after a rebuild
            st.session_state.upload_key += 1
            st.success(f"Indexed {document_count} documents ({node_count} nodes).")
        if st.button("Re-index all documents", use_container_width=True):
            with st.spinner("Reading, splitting and embedding the documents..."):
                document_count, node_count = ingest.build_index()
                rag.reset()
            st.success(f"Indexed {document_count} documents ({node_count} nodes).")

    with st.expander("Frequently asked questions"):
        for entry in json.loads(Path("faq.json").read_text()):
            st.markdown(f"**{entry['question']}**  \n{entry['answer']}")

# ---------------------------------------------------------------------------
# Main area: the chat.
# ---------------------------------------------------------------------------
st.title("Smart QA Assistant")
st.caption("Ask about leave, expenses and IT support. Answers come from the company documents.")

if not st.session_state.messages and not st.session_state.pending:
    st.info("Ask a question below, or pick an example from the sidebar.")

for message in st.session_state.messages:
    show_message(message)

# An approval request: the agent has paused and nothing happens until the user decides.
if st.session_state.pending:
    request = st.session_state.pending[0]
    with st.chat_message("assistant"):
        st.markdown("**Approval needed.** I would like to do the following:")
        st.markdown(f"- Action: `{request['name']}`")
        for key, value in request["args"].items():
            st.markdown(f"- {key}: {value}")
        approve_col, decline_col = st.columns(2)
        decision = None
        if approve_col.button("Approve", type="primary", use_container_width=True):
            decision = assistant.APPROVE
        if decline_col.button("Decline", use_container_width=True):
            decision = assistant.reject()
    if decision:
        with st.spinner("Working..."):
            take_turn(assistant.resume([decision], st.session_state.thread_id))
        st.rerun()

# A new question, typed or picked from the sidebar. The box is locked while an approval is open.
question = st.chat_input("Ask a question", disabled=bool(st.session_state.pending))
question = question or st.session_state.pop("queued", None)

if question and not st.session_state.pending:
    user_message = {"role": "user", "content": question}
    st.session_state.messages.append(user_message)
    show_message(user_message)
    with st.spinner("Thinking..."):
        take_turn(assistant.ask(question, st.session_state.thread_id))
    st.rerun()
