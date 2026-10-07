# Step 7 — Load Excel and CSV by Row

> Back to index · Previous: Load PDF by Page and Size · Next: Route by File Type

## Goal

Add loaders for the workbook and the FAQ file, turning each row into its own node, written
as text that makes sense without the rest of the table.

## Why this matters

A table has a different shape from prose. Its natural unit is a **row**, so the loaders cut
there. Cutting by size would be a mistake, because a size rule has no idea what a row is and
could split `L3, 6000, 1500` after the first comma.

There is a second, less obvious problem. A row on its own is almost meaningless. The
numbers `L3, 6000, 1500, 1200, Economy` do not say which is the hotel limit and which is the
meal allowance. The column names are in the header row, far away. An embedding model, or the
chat model, sees only the node, so the node must carry its own headers.

So each row is rewritten as text:

> Sheet: Travel Limits. Grade: L3. Hotel Limit Per Night (INR): 6000. Meal Allowance Per Day
> (INR): 1500. ...

Now the node says what each number is, and the words "hotel limit", "per night" and "L3" are
there for a search to find. The same idea, applied to the FAQ file, gives
`Question: ... Answer: ...`, which keeps the question's wording next to its answer.

## 1. Add the Imports

Add `import csv` at the very top of the file, with a blank line after it. Add `TextNode` and
`load_workbook` in these positions among the other imports:

```python
import csv
```

```python
from llama_index.core.schema import TextNode
```

```python
from openpyxl import load_workbook
```

`TextNode` is a node made directly from text. The Markdown and PDF loaders get nodes from a
parser. Here there is nothing to parse, so the loader builds each node itself.

## 2. Add the Excel Loader

Add at the end of the file:

```python
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
```

| Line | What it does |
|---|---|
| `data_only=True` | For a cell with a formula, reads the value Excel last saved and not the formula text |
| `.worksheets` | Loops over every sheet, so both "Travel Limits" and "Leave Entitlement" are read |
| `headers = rows[0]` | The first row of each sheet is taken as the column names |
| `enumerate(rows[1:], start=2)` | Numbers rows the way Excel does. The first data row is row 2, because row 1 is the header |
| `if all(value is None ...)` | Skips blank rows |
| `f"{header}: {value}"` | Writes each cell as `column: value`. This is what makes the row readable on its own |
| `"sheet"` and `"row"` metadata | Where the row came from. They become the source label, such as "sheet Travel Limits, row 4" |

## 3. Add the CSV Loader

Add at the end of the file:

```python
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
```

`csv.DictReader` reads the header line and gives each row as a dictionary, so
`record['question']` works by name. The category goes into metadata and not into the text.

## Try it

```bash
uv run python -c "
from pathlib import Path
from llama_index.core.schema import MetadataMode
from loaders import xlsx_nodes, csv_nodes
x = xlsx_nodes(Path('docs/expense_limits.xlsx'))
print(len(x)); print(x[2].text); print(x[2].metadata)
print('EMBED VIEW:'); print(x[2].get_content(metadata_mode=MetadataMode.EMBED))
c = csv_nodes(Path('docs/hr_faq.csv'))
print(len(c)); print(c[0].text); print(c[0].metadata)
"
```

```text
10
Sheet: Travel Limits. Grade: L3. Hotel Limit Per Night (INR): 6000. Meal Allowance Per Day (INR): 1500. Local Travel Per Day (INR): 1200. Flight Class: Economy.
{'file_name': 'expense_limits.xlsx', 'file_type': 'xlsx', 'sheet': 'Travel Limits', 'row': 4}
EMBED VIEW:
file_name: expense_limits.xlsx
file_type: xlsx
sheet: Travel Limits
row: 4

Sheet: Travel Limits. Grade: L3. Hotel Limit Per Night (INR): 6000. Meal Allowance Per Day (INR): 1500. Local Travel Per Day (INR): 1200. Flight Class: Economy.
12
Question: How do I reset my HR portal password?
Answer: Use the Forgot Password link on the HR portal login page. A reset link is sent to your company email and stays valid for 30 minutes.
{'file_name': 'hr_faq.csv', 'file_type': 'csv', 'category': 'Portal', 'row': 2}
```

Ten spreadsheet nodes (five grades on each of two sheets) and twelve FAQ nodes. The L3 row is
row 4, because row 1 is the header and L1 is row 2.

Now look hard at the EMBED VIEW. Before the row text come four lines of metadata:
`file_name`, `file_type`, `sheet` and `row`. By default, LlamaIndex puts **all** metadata in
front of the text when it creates the embedding. The number `4` in `row: 4` and the word `xlsx`
are noise that gets mixed into the meaning of every row. Step 8 removes it.

## Checkpoint

<details>
<summary>Full <code>loaders.py</code> after this step</summary>

```python
import csv

from docx import Document as WordDocument
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.readers.file import PDFReader
from openpyxl import load_workbook


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
```

</details>

This file is not finished. Step 8 adds the last pieces.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError: 'question'` | The CSV header is not exactly `question,answer,category` | Check the first line of `docs/hr_faq.csv` against Step 3 |
| An FAQ answer is cut short and its category is a sentence | An answer with a comma was not in double quotes, so the row split into extra columns | Quote that answer in the CSV, as the Step 3 checkpoint does |
| Rows show `None` for a value | A cell is empty, or a formula was never calculated and saved | Fill the cell, or open and save the file in Excel once so formula values are stored |
| Only one sheet is read | `load_workbook(path).active` was used, which is the first sheet only | Loop over `.worksheets`, as shown |
| Row numbers are off by one from Excel | The count started at 1 or 0 | `enumerate(rows[1:], start=2)` matches Excel's numbering |

Next: **Step 8 — Route by File Type**.
