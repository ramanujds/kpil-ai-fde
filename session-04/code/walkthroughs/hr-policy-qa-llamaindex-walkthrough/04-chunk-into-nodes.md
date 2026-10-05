# Step 4 — Chunk into Nodes

> Back to index · Previous: Load the Documents · Next: Embed and Store with an Index

## Goal

Add the second half of loading to `ingest.py`: cut each document into nodes, one per
heading, and see exactly what text the embedding model will receive for each.

## Why this matters

In the hand-built app, chunking was the most code in the file: split on `"\n## "`, split the
heading from the body, build a string, and fill two parallel lists. It also had a quiet
weakness. It worked only because every file used `##` headings exactly as the code
expected.

A **node parser** does the same job from a ready-made rule. `MarkdownNodeParser` cuts a
Markdown document at every heading. A **node** is LlamaIndex's word for a chunk, with one
difference: it is a single object that carries its own text and its own metadata, so the
two parallel lists, and the risk of them drifting out of step, are gone.

Two differences from your hand-built chunks matter, and both come up in this step.

The first is where the document title goes. Your hand-built chunk began with `Leave Policy >
Carry Forward of Leave`, so the card made sense on its own. The node parser keeps the
section's own heading in the text and records the title above it as `header_path` metadata.
When the node is embedded, LlamaIndex puts that metadata in front of the text. The model
receives the same information, arranged differently.

The second is the count. You will get 46 nodes, not 40 chunks.

## 1. Add the Parser

Add one import under the existing one, and then the parser call at the end of the loading
code:

```python
from llama_index.core.node_parser import MarkdownNodeParser
```

```python
# Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
nodes = MarkdownNodeParser().get_nodes_from_documents(documents)
print(f"Made {len(nodes)} nodes from {len(documents)} documents.")
```

Delete the three lines that printed the documents in Step 3. You no longer need them.

## 2. See What the Model Will Receive

To look at one node the way the embedding step will see it, add this import and line at
the end of the file. You will remove them in Step 5:

```python
from llama_index.core.schema import MetadataMode
```

```python
print(nodes[8].get_content(metadata_mode=MetadataMode.EMBED))
```

`metadata_mode=MetadataMode.EMBED` asks for the node's text as the embedding model sees it:
the metadata that LlamaIndex includes for embedding, followed by the text.

## Try it

```bash
uv run ingest.py
```

```text
Made 46 nodes from 6 documents.
header_path: /Leave Policy/

## Paid Leave Entitlement
Every confirmed and probationary employee earns 12 days of paid leave per year. Paid leave accrues at 1 day for each completed month of service, so a new joiner builds up leave gradually through the year. Paid leave can be taken only after it has accrued.
```

Compare this with the hand-built chunk, which began `Leave Policy > Paid Leave Entitlement`.
The title (`/Leave Policy/`) and the section heading are both there. Look at what is not there:
`file_name`. It is stored with the node so that `ask.py` can print it, but the reader
marks it as hidden from embedding, so it does not add noise to the vector.

Now change `nodes[8]` to `nodes[0]` and run again:

```text
Made 46 nodes from 6 documents.
header_path: /

# HR Handbook
Department: HR
Version: 2025
Effective: 1 April 2025
```

This is the answer to the 46: each of the six files starts with a title and three labelled
lines before its first `##` heading, and the parser turns that opening block into a node
of its own. Six of those plus the 40 sections make 46. The hand-built code threw the
opening block away. Here it becomes a node, and so the `Department` and `Version` lines are
now searchable. In Step 9 you will decide whether that is a gain or clutter. When such a
node is retrieved in Step 6, the "Retrieved from" list shows the document title in place
of a section name, for example `03_laptop_policy.md > Laptop and Equipment Policy`.

## Checkpoint

<details>
<summary>Full <code>ingest.py</code> after this step</summary>

```python
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import MetadataMode

# Step 1: load every file in docs/. With the llama-index-readers-file package added, it also reads PDF and Word.
# We keep only the file name as metadata. The default also holds the full file path, which would get embedded.
documents = SimpleDirectoryReader(
    "docs", file_metadata=lambda path: {"file_name": Path(path).name}
).load_data()

# Step 2: cut each document into nodes (LlamaIndex's word for chunks), one per heading.
nodes = MarkdownNodeParser().get_nodes_from_documents(documents)
print(f"Made {len(nodes)} nodes from {len(documents)} documents.")

print(nodes[8].get_content(metadata_mode=MetadataMode.EMBED))
```

</details>

This file is not finished. Step 5 adds to it, removes the last line, and holds the final
version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Made 6 nodes` | The documents were loaded, but the parser was applied to the wrong object, or the files use no `##` headings | Check the line `MarkdownNodeParser().get_nodes_from_documents(documents)` and that each file has `##` headings |
| `ImportError` for `MetadataMode` | The import path is wrong | It is `from llama_index.core.schema import MetadataMode` |
| The count is not 46 | A document is missing or edited, or the count was compared with the hand-built 40 | Each file gives one node for its opening block plus one per `##` heading. Check `docs/` against Step 3 of the hand-built walkthrough |
| `IndexError: list index out of range` | Fewer than 9 nodes were made | Check that all six documents loaded in Step 3 |
| The printed text has no `header_path` line | The text was printed with `nodes[8].text` instead of the embedding view | Use `get_content(metadata_mode=MetadataMode.EMBED)` |

Next: **Step 5 — Embed and Store with an Index**.
