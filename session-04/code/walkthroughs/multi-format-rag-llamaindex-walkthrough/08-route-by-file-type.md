# Step 8 — Route by File Type

> Back to index · Previous: Load Excel and CSV by Row · Next: Embed and Store

## Goal

Finish `loaders.py`: keep location metadata out of the embedded text, and add one function
that sends each file in `docs/` to the right loader by its extension.

## Why this matters

Two jobs are left, and both are about making five loaders behave as one.

The first is **metadata hygiene**. At the end of Step 7 the embedding view of a spreadsheet
row began with four lines: `file_name`, `file_type`, `sheet` and `row`. The embedding model
turns text into a vector that stands for its meaning, and `row: 4` and `file_type: xlsx` have
no bearing on the meaning of a hotel limit. Worse, they are the same in many nodes, so they
pull unrelated rows closer together. We still want that metadata, for filtering and for
showing sources. We just do not want it inside the text that gets embedded, or the text that
the chat model reads. LlamaIndex lets each node list the metadata keys to hide from each.

The second is **routing**. Ingest should not need to know that there are five formats. It
should say "load everything in `docs/`", and the loaders module decides, by file extension,
which function to call. That is a dictionary from extension to function. A new format is one
new function and one new line in the dictionary, and a file with no loader is skipped with a
message instead of crashing.

## 1. Add the Module Docstring and the Path Import

At the very top of the file, before `import csv`, add the docstring that states the rule for
each format:

```python
"""Reads each file type and cuts it into nodes (LlamaIndex's word for chunks).

The point of this file: one chunking rule does not fit every format. Each function below
picks the natural unit of its format.

    .md    one node per heading
    .docx  converted to markdown first, then one node per heading
    .pdf   one document per page, then size-based chunks with overlap
    .xlsx  one node per row, written out as "column: value" text
    .csv   one node per row, written out as a question and answer
"""
```

Then add `from pathlib import Path` right after `import csv`:

```python
from pathlib import Path
```

## 2. Hide Location Metadata From the Text

Between the imports and `base_metadata`, add:

```python
# Metadata that helps filtering and showing sources, but that we do not want mixed into the
# text that gets embedded.
NO_EMBED = ["file_type", "page", "row", "sheet"]
```

Then, right after `base_metadata`, add:

```python
def finish(nodes):
    """Keep location metadata out of the embedded text and out of the prompt text."""
    for node in nodes:
        node.excluded_embed_metadata_keys = NO_EMBED
        node.excluded_llm_metadata_keys = NO_EMBED
    return nodes
```

| Key | Stays visible? | Why |
|---|---|---|
| `file_name` | Yes | The name often carries meaning, such as "travel_policy" |
| `header_path`, `category` | Yes | They describe what the node is about |
| `file_type`, `page`, `row`, `sheet` | No | They say where the node came from, not what it says |

The metadata is not deleted. `node.metadata` still holds everything, so filters and the
source list still work. Only the two text views change.

## 3. Add the Router

Add at the very end of the file:

```python
# File extension -> the function that knows how to read and chunk it.
LOADERS = {
    ".md": markdown_nodes,
    ".docx": docx_nodes,
    ".pdf": pdf_nodes,
    ".xlsx": xlsx_nodes,
    ".csv": csv_nodes,
}


def load_nodes(docs_dir):
    nodes = []
    for path in sorted(Path(docs_dir).iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            print(f"Skipping {path.name}: no loader for {path.suffix}")
            continue
        nodes.extend(finish(loader(path)))
    return nodes
```

The functions are stored in the dictionary without brackets. `LOADERS.get(".pdf")` gives back
the function `pdf_nodes` itself, and `loader(path)` then calls it.

## Try it

```bash
uv run python -c "
from collections import Counter
from llama_index.core.schema import MetadataMode
from loaders import load_nodes
nodes = load_nodes('docs')
print(len(nodes), dict(sorted(Counter(n.metadata['file_type'] for n in nodes).items())))
x = [n for n in nodes if n.metadata['file_type'] == 'xlsx'][2]
print('EMBED VIEW:'); print(x.get_content(metadata_mode=MetadataMode.EMBED))
print('METADATA STILL THERE:', x.metadata)
"
```

```text
41 {'csv': 12, 'docx': 6, 'md': 7, 'pdf': 6, 'xlsx': 10}
EMBED VIEW:
file_name: expense_limits.xlsx

Sheet: Travel Limits. Grade: L3. Hotel Limit Per Night (INR): 6000. Meal Allowance Per Day (INR): 1500. Local Travel Per Day (INR): 1200. Flight Class: Economy.
METADATA STILL THERE: {'file_name': 'expense_limits.xlsx', 'file_type': 'xlsx', 'sheet': 'Travel Limits', 'row': 4}
```

Forty-one nodes: 12 + 6 + 7 + 6 + 10. The embedding view is now the file name and the row text.
`file_type`, `sheet` and `row` are gone from it, but still in `metadata`.

Check the skip message too. Make a file the app has no loader for, load, and remove it:

```bash
touch docs/notes.txt
uv run python -c "from loaders import load_nodes; load_nodes('docs')"
rm docs/notes.txt
```

```text
Skipping notes.txt: no loader for .txt
```

## Checkpoint

<details>
<summary>Full <code>loaders.py</code></summary>

```python
"""Reads each file type and cuts it into nodes (LlamaIndex's word for chunks).

The point of this file: one chunking rule does not fit every format. Each function below
picks the natural unit of its format.

    .md    one node per heading
    .docx  converted to markdown first, then one node per heading
    .pdf   one document per page, then size-based chunks with overlap
    .xlsx  one node per row, written out as "column: value" text
    .csv   one node per row, written out as a question and answer
"""
import csv
from pathlib import Path

from docx import Document as WordDocument
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.readers.file import PDFReader
from openpyxl import load_workbook

# Metadata that helps filtering and showing sources, but that we do not want mixed into the
# text that gets embedded.
NO_EMBED = ["file_type", "page", "row", "sheet"]


def base_metadata(path):
    return {"file_name": path.name, "file_type": path.suffix.lstrip(".").lower()}


def finish(nodes):
    """Keep location metadata out of the embedded text and out of the prompt text."""
    for node in nodes:
        node.excluded_embed_metadata_keys = NO_EMBED
        node.excluded_llm_metadata_keys = NO_EMBED
    return nodes


def markdown_nodes(path):
    document = Document(text=path.read_text(encoding="utf-8"), metadata=base_metadata(path))
    return MarkdownNodeParser().get_nodes_from_documents([document])


def docx_nodes(path):
    # A Word file read as plain text loses its headings, so the markdown parser would have
    # nothing to split on. We rebuild the headings as "## " lines first.
    lines = []
    for paragraph in WordDocument(path).paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        style = paragraph.style.name
        if style.startswith("Heading"):
            level = int(style.split()[-1])
            lines.append("#" * level + " " + text)
        elif style.startswith("List"):
            lines.append("- " + text)
        else:
            lines.append(text)
    document = Document(text="\n\n".join(lines), metadata=base_metadata(path))
    return MarkdownNodeParser().get_nodes_from_documents([document])


def pdf_nodes(path):
    # One document per page, so every node knows its page number.
    pages = PDFReader().load_data(path)
    documents = [
        Document(text=page.text, metadata={**base_metadata(path), "page": int(page.metadata["page_label"])})
        for page in pages
    ]
    # A PDF has no reliable headings, so we cut by size. The overlap repeats the end of one
    # chunk at the start of the next, so a sentence on the boundary is not lost.
    return SentenceSplitter(chunk_size=256, chunk_overlap=40).get_nodes_from_documents(documents)


def xlsx_nodes(path):
    # Cutting a spreadsheet by size would split a row in the middle. A row is the natural
    # unit, and it must carry its column names or the numbers mean nothing.
    nodes = []
    for sheet in load_workbook(path, data_only=True).worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        headers = rows[0]
        for number, values in enumerate(rows[1:], start=2):
            if all(value is None for value in values):
                continue
            fields = ". ".join(f"{header}: {value}" for header, value in zip(headers, values))
            nodes.append(
                TextNode(
                    text=f"Sheet: {sheet.title}. {fields}.",
                    metadata={**base_metadata(path), "sheet": sheet.title, "row": number},
                )
            )
    return nodes


def csv_nodes(path):
    # Each row is already one question and its answer, so it is one node.
    nodes = []
    with open(path, newline="", encoding="utf-8") as f:
        for number, record in enumerate(csv.DictReader(f), start=2):
            nodes.append(
                TextNode(
                    text=f"Question: {record['question']}\nAnswer: {record['answer']}",
                    metadata={**base_metadata(path), "category": record["category"], "row": number},
                )
            )
    return nodes


# File extension -> the function that knows how to read and chunk it.
LOADERS = {
    ".md": markdown_nodes,
    ".docx": docx_nodes,
    ".pdf": pdf_nodes,
    ".xlsx": xlsx_nodes,
    ".csv": csv_nodes,
}


def load_nodes(docs_dir):
    nodes = []
    for path in sorted(Path(docs_dir).iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            print(f"Skipping {path.name}: no loader for {path.suffix}")
            continue
        nodes.extend(finish(loader(path)))
    return nodes
```

</details>

This matches the reference project's `loaders.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| The count is not 41 | A document is missing or was edited, or `docs/` holds an extra file with a loader | List `docs/` and compare with Step 3 |
| `file_type`, `row` still appear in the embedding view | `finish` was not applied, for example `nodes.extend(loader(path))` without `finish(...)` | Wrap it: `nodes.extend(finish(loader(path)))` |
| `NameError: name 'Path' is not defined` | The `from pathlib import Path` line was not added | Add it below `import csv` |
| A `.PDF` file in capitals is skipped | The extension was not lower-cased | `path.suffix.lower()`, as shown |
| `TypeError: 'NoneType' object is not callable` | The dictionary lookup returned `None` and was called anyway | Keep the `if loader is None` check |

Next: **Step 9 — Embed and Store**.
