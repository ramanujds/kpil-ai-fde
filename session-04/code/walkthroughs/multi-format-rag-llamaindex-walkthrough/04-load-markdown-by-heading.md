# Step 4 — Load Markdown by Heading

> Back to index · Previous: Make the Sample Data · Next: Load Word Through Markdown

## Goal

Start `loaders.py` with the simplest format: read a Markdown file and cut it into one node
per heading, each carrying the file name and file type as metadata.

## Why this matters

`loaders.py` has one job: for each file type, return nodes. Every loader will be a function
that takes a file path and returns a list of nodes, so that ingest can treat them all the
same. Markdown goes first because it needs the least: a Markdown file is already divided by
its author at every heading, and `MarkdownNodeParser` cuts there.

Two choices here matter later.

The first is the **metadata**. Every node records `file_name` and `file_type`. The file name
lets `ask.py` say where an answer came from. The file type lets a user say "search only the
PDF" in Step 14, so it must be stored now, in a form that a filter can match exactly: the
extension without its dot, in lower case.

The second is that the loader receives a `Path`, not a string, because `base_metadata` uses
`path.name` and `path.suffix`.

## 1. Create the File With One Loader

Create `loaders.py`:

```python
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser


def base_metadata(path):
    return {"file_name": path.name, "file_type": path.suffix.lstrip(".").lower()}


def markdown_nodes(path):
    document = Document(text=path.read_text(encoding="utf-8"), metadata=base_metadata(path))
    return MarkdownNodeParser().get_nodes_from_documents([document])
```

| Line | What it does |
|---|---|
| `base_metadata` | The facts every node of every format will carry |
| `Document(text=..., metadata=...)` | Builds a LlamaIndex document by hand. The earlier app used a directory reader for this, which cannot treat each format differently |
| `MarkdownNodeParser().get_nodes_from_documents([document])` | One node per heading, as in the earlier app |

## Try it

Call the loader from the command line, without writing a script:

```bash
uv run python -c "
from pathlib import Path
from loaders import markdown_nodes
nodes = markdown_nodes(Path('docs/employee_handbook.md'))
print(len(nodes))
for i in (0, 2):
    print('--- node', i, nodes[i].metadata)
    print(nodes[i].text)
"
```

```text
7
--- node 0 {'file_name': 'employee_handbook.md', 'file_type': 'md', 'header_path': '/'}
# Employee Handbook
Department: HR
Version: 2025
--- node 2 {'file_name': 'employee_handbook.md', 'file_type': 'md', 'header_path': '/Employee Handbook/'}
## Working Hours
The standard working week is Monday to Friday, 9:30 AM to 6:00 PM, with a 45 minute lunch break. Employees may start between 8:30 AM and 10:30 AM if they complete the same number of hours and are available for the core hours of 11:00 AM to 4:00 PM. Working on a public holiday needs written approval from the department head and earns a compensatory day off.
```

The count is 7: six `##` sections plus one node for the opening block (the title and the
two labelled lines). The parser also added `header_path`, the headings above each node.

## Checkpoint

<details>
<summary>Full <code>loaders.py</code> after this step</summary>

```python
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser


def base_metadata(path):
    return {"file_name": path.name, "file_type": path.suffix.lstrip(".").lower()}


def markdown_nodes(path):
    document = Document(text=path.read_text(encoding="utf-8"), metadata=base_metadata(path))
    return MarkdownNodeParser().get_nodes_from_documents([document])
```

</details>

This file is not finished. Steps 5 to 8 add to it, and Step 8 holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `AttributeError: 'str' object has no attribute 'name'` | A string was passed instead of a `Path` | Call it as `markdown_nodes(Path('docs/employee_handbook.md'))` |
| `ModuleNotFoundError: No module named 'loaders'` | The command ran from a different folder | Run it from the project folder, where `loaders.py` lives |
| The count is 1 | The file has no `##` headings, or it was saved with different line endings | Check `docs/employee_handbook.md` against the Step 3 checkpoint |
| `UnicodeDecodeError` | The file was saved in a non-UTF-8 encoding | Re-save it as UTF-8, or keep `encoding="utf-8"` and fix the file |

Next: **Step 5 — Load Word Through Markdown**.
