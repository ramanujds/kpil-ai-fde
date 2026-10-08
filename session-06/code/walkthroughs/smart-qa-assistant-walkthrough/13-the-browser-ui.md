# Step 13 — The Browser UI

> Back to index · Previous: Checks Without a Model · Next: Recap and Exercises

## Goal

Put the same assistant behind a browser chat window with an approval card, example questions and
a small admin area for adding documents.

## Why this matters

Most staff will not use a terminal. The good news is that almost nothing in the project changes:
`assistant.py` was written without a screen in mind (that is why `ask` returns a `Turn` and not
printed text), so the browser needs only a new front end. The terminal asked for approval with
`input()`. A browser cannot pause and wait like that, so the approval has to become something the
page can **show** and **remember**.

Streamlit works by re-running the whole `ui.py` file from top to bottom every time the user
clicks anything. That has one big consequence: normal variables are forgotten between clicks.
Anything that must survive, such as the chat so far or a pending approval, is kept in
`st.session_state`, a dictionary that Streamlit keeps for each browser tab.

So the approval flow becomes:

1. `ask` returns a `Turn` with `pending` set. The UI stores it in `session_state`.
2. The page re-runs. Because `pending` is set, it draws an **Approve / Decline card** and locks
   the message box.
3. A click calls `resume` with the decision, clears `pending`, and re-runs again.

It is the same pause and resume as Step 8, drawn instead of typed.

The admin area also needs two small changes underneath: `ingest.py` becomes a function the UI can
call, and `rag.py` learns to forget its open collection after a rebuild.

## 1. Turn `ingest.py` Into a Function

Replace `ingest.py` with this version. The body is the same as before; it is wrapped in
`build_index()`, and the script part moves under `if __name__ == "__main__":`:

<details>
<summary>Full <code>ingest.py</code></summary>

```python
"""Document ingestion: read everything in docs/, cut it into nodes, embed it, store it in Chroma.

Run this once, and again whenever a file in docs/ is added or changed. The browser UI calls
build_index() too, from its Re-index button.
"""

from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.vector_stores.chroma import ChromaVectorStore

import config


def build_index() -> tuple[int, int]:
    """Rebuild the Chroma collection from docs/. Returns (documents, nodes)."""
    # Step 1: load every file in docs/. Keep only the file name as metadata.
    documents = SimpleDirectoryReader(
        "docs", file_metadata=lambda path: {"file_name": Path(path).name}
    ).load_data()

    # Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
    nodes = MarkdownNodeParser().get_nodes_from_documents(documents)

    # Steps 3 and 4: embed every node and store the vectors in Chroma. We start from an empty
    # collection so that running this twice does not store duplicates, and an updated policy
    # replaces the old version cleanly. "cosine" makes the score a similarity from 0 to 1.
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    try:
        client.delete_collection(config.COLLECTION)
    except Exception:
        pass  # first run: there is nothing to delete yet
    collection = client.create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})

    storage_context = StorageContext.from_defaults(
        vector_store=ChromaVectorStore(chroma_collection=collection)
    )
    VectorStoreIndex(nodes, storage_context=storage_context)
    return len(documents), collection.count()


if __name__ == "__main__":
    document_count, node_count = build_index()
    print(f"Made {node_count} nodes from {document_count} documents and stored them in Chroma. Now run app.py or ui.py.")
```

</details>

| Change | Why |
|---|---|
| `def build_index() -> tuple[int, int]` | The UI can call it and show "Indexed 3 documents (18 nodes)" |
| `show_progress=True` removed | A progress bar printed in a function called from a web page is noise |
| `if __name__ == "__main__":` | `uv run ingest.py` still works exactly as before |

## 2. Teach `rag.py` to Reopen the Collection

`build_index()` deletes and recreates the collection. The open handle `rag.py` is holding then
points at something that no longer exists. Add a `reset()` function between `_get_retriever` and
`search`:

```python
def reset() -> None:
    """Forget the open collection. Call after ingest.py rebuilds it, so the next search reopens it."""
    global _retriever
    _retriever = None
```

The next call to `search` sees `_retriever is None` and opens the new collection (Step 4).

<details>
<summary>Full <code>rag.py</code></summary>

```python
"""Retrieval: find the passages in the Chroma collection that best match a question."""

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

_retriever = None


def _get_retriever():
    """Open the Chroma collection that ingest.py filled, the first time it is needed."""
    global _retriever
    if _retriever is None:
        collection = chromadb.PersistentClient(path=config.CHROMA_PATH).get_collection(config.COLLECTION)
        index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))
        _retriever = index.as_retriever(similarity_top_k=config.TOP_K)
    return _retriever


def reset() -> None:
    """Forget the open collection. Call after ingest.py rebuilds it, so the next search reopens it."""
    global _retriever
    _retriever = None


def search(question: str) -> list[dict]:
    """Return the matching passages as {source, text, score}, best first.

    Weak matches are dropped. An empty list means "the documents do not cover this".
    """
    passages = []
    for hit in _get_retriever().retrieve(question):
        if hit.score is None or hit.score < config.MIN_SCORE:
            continue
        heading = hit.node.get_content().splitlines()[0].lstrip("# ")
        passages.append(
            {
                "source": f"{hit.node.metadata['file_name']} > {heading}",
                "text": hit.node.get_content(),
                "score": hit.score,
            }
        )
    return passages
```

</details>

## 3. Write `ui.py`

Create `ui.py`. It is long but has four clear parts. Type them in order.

**Part 1: imports, constants and page setup.**

```python
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
```

**Part 2: session state and three small helpers.**

```python
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
```

| Part | What it does |
|---|---|
| `thread_id = str(uuid.uuid4())` | A unique id per browser session is the assistant's memory key, exactly as `chat-1` was in the terminal |
| `messages` | What the chat window shows. Separate from the assistant's own saved memory |
| `new_conversation` | A fresh id, an empty window. The same trick as `reset` in the terminal |
| `show_message` | Draws one message, with small print underneath: an FAQ badge, the tools used and the sources, which are the `Turn` fields built in Steps 9 and 10 |
| `take_turn` | Either stores the approval request, or adds the assistant's reply to the window |

**Part 3: the sidebar** with the signed-in user, example questions and the admin area.

```python
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
```

| Part | What it does |
|---|---|
| `on_click=new_conversation` | Runs the reset when the button is clicked |
| `st.session_state.queued = example` | A click on an example saves the question, and the main area picks it up below |
| `file_uploader(type=["md", "txt"])` | Only text documents, because the ingest in Step 3 reads these two kinds without extra packages |
| `ingest.build_index()` then `rag.reset()` | Rebuild the store, then make search reopen it |
| `key=f"upload-{...upload_key}"` | Streamlit has no "clear the uploader" call. Changing its key makes it a new, empty widget |
| The FAQ expander | Read-only here. Editing the FAQ is left as an exercise |

The Admin label says "Demo only", and it means it. Anyone who can open the page can change the
documents. A real system would show this area to HR and IT staff only.

**Part 4: the chat itself**, with the approval card and the message box.

```python
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
```

| Part | What it does |
|---|---|
| `if st.session_state.pending:` | If the agent is waiting for a person, draw the approval card |
| `approve_col, decline_col = st.columns(2)` and the two buttons | Set `decision` when one is clicked |
| `take_turn(assistant.resume([decision], thread_id))` and `st.rerun()` | Send the decision, store the result, redraw the page |
| `disabled=bool(st.session_state.pending)` | The message box is locked while an approval is open, so a new question cannot slip past the pause |
| `question or st.session_state.pop("queued", None)` | A typed question, or one picked in the sidebar |
| `st.spinner("Thinking...")` | Shows progress while the model works; local models take a few seconds |
| `st.rerun()` after the turn | Redraws the page so the new message appears in the history loop |

## Try it

```bash
uv run streamlit run ui.py
```

Streamlit opens `http://localhost:8501` in your browser. Try these:

| Do this | You should see |
|---|---|
| Click "How many paid leave days do I get in a year?" | An answer with a small "FAQ answer (approved, no model call)" line |
| Click "What about part-time staff?" | An answer with "Tools used: search_documents" and a list of sources |
| Click "How many leave days have I used?" | "Tools used: get_leave_balance" |
| Click "Raise a ticket for my broken laptop" | An approval card with the team and summary, and a locked message box |
| Click Decline, then ask again and click Approve | A "ticket was not created" reply the first time; a created ticket the second |
| Click New conversation, then ask "What about part-time staff?" | The agent cannot tell what "that" refers to: memory is gone |

Then try the admin area. Open `docs/leave_policy.md` on your machine, change "10 days of paid sick
leave" to "12 days of paid sick leave" and save a copy. In the sidebar, open Documents, upload the
changed file and click "Save and re-index". Ask "How many days of sick leave do I get?" and the
answer now says 12.

Now ask the paid-leave question that the FAQ answers, "How many paid leave days do I get in a
year?". It still gives the old FAQ text. That is the lesson from Step 10 made visible: the FAQ
is a separate, reviewed list, and somebody has to review it when a policy changes.

## Checkpoint

<details>
<summary>Full <code>ui.py</code></summary>

```python
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
```

</details>

`ingest.py`, `rag.py` and `ui.py` now match the reference files exactly. Every file in the project
now matches the reference.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `streamlit: command not found` | Run outside the environment | Use `uv run streamlit run ui.py` |
| The page says the module `ingest` has no `build_index` | `ingest.py` is still the Step 3 script | Replace it with the Step 13 version |
| Search returns nothing after re-indexing | `rag.reset()` is missing | Call it after `build_index()`, as in the sidebar code |
| Approve and Decline do nothing | The page was not re-run after the click | Keep the `st.rerun()` after `take_turn` |
| The chat clears itself | A new tab or a page reload creates a new session | Expected: each tab has its own session state and thread id |
| An error mentions `collection company_docs` | You started the UI from another folder | Run from the project folder, where `.chroma` lives |

Next: **Step 14 — Recap and Exercises**.
