# Step 5 — Load Word Through Markdown

> Back to index · Previous: Load Markdown by Heading · Next: Load PDF by Page and Size

## Goal

Add a Word loader that rebuilds each heading and bullet as markdown, so the same parser can
cut the file at its headings.

## Why this matters

A Word file looks like it has headings, but to a program it does not. A heading in Word is a
paragraph with a **style** called "Heading 2". The words themselves carry no `#` and no
marker. Read the file as plain text and the headings melt into the body.

That matters because `MarkdownNodeParser` looks for `#` characters. With none to find, it
would return the whole file as one node, and a question about "First Week" would pull in the
whole checklist.

The fix is small and general: read the file with `python-docx`, which does expose each
paragraph's style, and write the text back out as markdown. A paragraph styled "Heading 2"
becomes `## ...`, a bullet becomes `- ...`, and everything else stays as it is. Then the
Markdown parser from Step 4 does the cutting. One cutting rule serves two formats.

## 1. See the Problem First

Print the Word file as plain text:

```bash
uv run python -c "
from docx import Document
text = '\n'.join(p.text for p in Document('docs/onboarding_checklist.docx').paragraphs if p.text.strip())
print(text[:330])
"
```

```text
New Joiner Onboarding Checklist
Department: HR. This checklist is shared with every new joiner and their manager.
Before Day One
HR sends the offer documents and a list of papers to bring: ID proof, address proof, and the relieving letter from the previous employer.
IT prepares a laptop and a company email account. The laptop is
```

"Before Day One" is a heading, but nothing in the text says so.

## 2. Add the Word Loader

Add the import at the top, above the `llama_index` imports. It is renamed because
LlamaIndex also has a class called `Document`:

```python
from docx import Document as WordDocument
```

Then add the function at the end of the file:

```python
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
```

| Line | What it does |
|---|---|
| `paragraph.style.name` | The style Word gave the paragraph: "Heading 1", "Heading 2", "List Bullet", "Normal" |
| `int(style.split()[-1])` | The heading level from the style name, so "Heading 2" becomes two `#` marks |
| `if not text: continue` | Skips empty paragraphs, which would otherwise become blank lines |
| `"\n\n".join(lines)` | Markdown needs a blank line between blocks to read them as separate paragraphs |
| The last two lines | The same as the Markdown loader. Only the first half differs |

## Try it

```bash
uv run python -c "
from pathlib import Path
from loaders import docx_nodes
nodes = docx_nodes(Path('docs/onboarding_checklist.docx'))
print(len(nodes))
print([n.text.splitlines()[0] for n in nodes])
print(nodes[1].text)
"
```

```text
6
['# New Joiner Onboarding Checklist', '## Before Day One', '## Day One', '## First Week', '## First Month', '## Who to Contact']
## Before Day One

- HR sends the offer documents and a list of papers to bring: ID proof, address proof, and the relieving letter from the previous employer.

- IT prepares a laptop and a company email account. The laptop is collected from the IT desk on the first morning.

- The manager nominates a buddy from the same team.
```

Six nodes: the title block and five sections, each starting with its heading.

## Checkpoint

<details>
<summary>Full <code>loaders.py</code> after this step</summary>

```python
from docx import Document as WordDocument
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser


def base_metadata(path):
    return {"file_name": path.name, "file_type": path.suffix.lstrip(".").lower()}


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
```

</details>

This file is not finished. Steps 6 to 8 add to it.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'docx'` | The package is installed as `python-docx` but imported as `docx`, and `uv sync` was skipped | Run `uv sync`, and start Python with `uv run` |
| Only 1 node comes back | The heading styles were not recognised, for example the file was made in a tool that uses its own style names | Print `paragraph.style.name` for a few paragraphs and adjust the `startswith("Heading")` test |
| `NameError: name 'Document' is not defined` or the wrong `Document` is used | The Word import was not renamed, so it replaced the LlamaIndex `Document` | Import it as `from docx import Document as WordDocument` and call `WordDocument(path)` |
| Bullets run together in one line | The nodes were joined with a single newline | Join with `"\n\n"`, as shown |

Next: **Step 6 — Load PDF by Page and Size**.
