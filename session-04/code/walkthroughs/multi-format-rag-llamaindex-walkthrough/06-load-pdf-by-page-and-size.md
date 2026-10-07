# Step 6 — Load PDF by Page and Size

> Back to index · Previous: Load Word Through Markdown · Next: Load Excel and CSV by Row

## Goal

Add a PDF loader that keeps each page's number, then cuts the pages into chunks by size,
with overlap.

## Why this matters

A PDF is a picture of pages. Its text has no headings the program can rely on: a heading is
just a line in a bigger font, and the text extractor returns it as one more line. So the
heading rule from Steps 4 and 5 has nothing to cut at, and we fall back to the oldest rule
there is: cut by **size**.

Size cutting has one danger. A cut can land in the middle of an idea, and a fact on the
boundary ends up half in one chunk and half in the next, complete in neither. The remedy is
**overlap**: each chunk begins with the last sentences of the one before. A sentence on the
boundary then appears whole in at least one chunk.

There is also something worth keeping from the PDF that Markdown does not have: the **page
number**. People say "see page 2". So the loader reads one document per page, stores the page
number as metadata, and only then cuts each page by size. The page number follows every
chunk, and later shows up in the source list.

## 1. Add the Imports

Change the node parser import so it also brings `SentenceSplitter`, and add the PDF reader
below it:

```python
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.readers.file import PDFReader
```

## 2. Add the PDF Loader

Add at the end of the file:

```python
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
```

| Line | What it does |
|---|---|
| `PDFReader().load_data(path)` | Returns one LlamaIndex document per page, each with a `page_label` |
| `{**base_metadata(path), "page": int(...)}` | Our usual metadata, plus the page as a number. A number, not text, so it can be sorted and compared |
| `SentenceSplitter(chunk_size=256, chunk_overlap=40)` | Chunks of about 256 tokens that break at sentence ends where they can, with 40 tokens repeated from the previous chunk |
| One splitter call over all pages | Each chunk inherits the metadata of the page it came from |

Why 256 and not a bigger number? A page of this PDF holds roughly 230 to 260 words, about
350 tokens, so a size of 512 or 1024 would give one chunk per page and no cutting to see. 256 makes the
effect of size cutting visible. Exercise 2 lets you try other values.

## Try it

```bash
uv run python -c "
from pathlib import Path
from loaders import pdf_nodes
nodes = pdf_nodes(Path('docs/travel_policy.pdf'))
print(len(nodes))
print([(n.metadata['page'], len(n.text)) for n in nodes])
print(nodes[0].metadata)
print('--- end of node 0:')
print(nodes[0].text[-120:])
print('--- start of node 1:')
print(nodes[1].text[:160])
"
```

```text
6
[(1, 1011), (1, 407), (2, 1111), (2, 432), (3, 1038), (3, 260)]
{'file_name': 'travel_policy.pdf', 'file_type': 'pdf', 'page': 1}
--- end of node 0:
e sharply close to departure.
Trains are the default choice for journeys under 6 hours, for example Ahmedabad to Mumbai.
--- start of node 1:
Trains are the default choice for journeys under 6 hours, for example Ahmedabad to Mumbai. Air
travel is allowed for longer journeys or when a train is not avai
```

Three pages became six nodes, two per page, and every node knows its page. Look at the last
two blocks: the sentence "Trains are the default choice..." ends node 0 **and** begins node
1. That is the overlap.

## Checkpoint

<details>
<summary>Full <code>loaders.py</code> after this step</summary>

```python
from docx import Document as WordDocument
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.readers.file import PDFReader


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
```

</details>

This file is not finished. Steps 7 and 8 add to it.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'llama_index.readers'` | `llama-index-readers-file` is not installed | Check it is in `pyproject.toml` (Step 2) and run `uv sync` |
| `KeyError: 'page_label'` | A different version of the reader names the page field differently | Print `pages[0].metadata` and use the key it shows |
| `ValueError` about metadata being longer than the chunk size | The metadata is bigger than `chunk_size`, which leaves no room for text | Keep metadata small, or raise the chunk size. Our three short fields are fine |
| The count is 3, one per page | `chunk_size` is larger than a page | Use 256, or see Exercise 2 |
| Text is empty or garbled | The PDF is a scan, a picture of text | A PDF without a text layer needs OCR, which this app does not cover |

Next: **Step 7 — Load Excel and CSV by Row**.
