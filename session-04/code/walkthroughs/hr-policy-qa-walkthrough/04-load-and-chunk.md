# Step 4 — Load and Chunk

> Back to index · Previous: The Documents · Next: Embed the Chunks

## Goal

Start `ingest.py`: read every document and cut it into chunks, one per section, each with
its source and section name attached.

## Why this matters

The model can only be given a few pieces of text per question, so the documents have to be
cut into pieces small enough to pick from. Think of index cards: if each card holds one
section of a policy, finding the right card is easy. If each card holds a whole 20-page
document, the right card is found but the answer is buried in it. If each card holds half a
sentence, it means nothing on its own.

A section is a natural size: one idea, written to stand alone. Two details make each chunk
more useful. The title and heading are written into the chunk text, so a card that says
"The limit is 6 days" is instead "Leave Policy > Carry Forward of Leave", then the text.
And the source and section are kept separately as metadata, so the app can say where an
answer came from.

## 1. Find the Files

Create `ingest.py` and start with the loop over the files:

```python
from pathlib import Path

for path in sorted(Path("docs").glob("*.md")):
    print(path.name)
```

`Path("docs").glob("*.md")` returns every `.md` file in `docs`. `sorted` puts them in the
same order every time, which keeps the chunks in a predictable order.

## 2. Split the Title from the Sections

Every section starts with a `##` at the start of a line, so splitting the file on
`"\n## "` gives one piece for the header and one piece for each section:

```python
for path in sorted(Path("docs").glob("*.md")):
    header, *sections = path.read_text().split("\n## ")
    title = header.splitlines()[0].lstrip("# ")
```

`header, *sections = ...` puts the first piece in `header` and all the rest in the list
`sections`. The first line of the header is `# Leave Policy`; `lstrip("# ")` removes the
leading `#` and space, leaving `Leave Policy`.

## 3. Build One Chunk per Section

Each section piece reads `Carry Forward of Leave`, a line break, and then the text. Split
once on the first line break to separate the heading from the body:

```python
texts, metadatas = [], []
for path in sorted(Path("docs").glob("*.md")):
    header, *sections = path.read_text().split("\n## ")
    title = header.splitlines()[0].lstrip("# ")
    for section in sections:
        heading, body = section.split("\n", 1)
        # The title and heading go inside the chunk, so it makes sense on its own.
        texts.append(f"{title} > {heading}\n{body.strip()}")
        metadatas.append({"source": title, "section": heading})
```

Two lists are filled side by side: `texts` holds the chunk text and `metadatas` holds the
label for the chunk in the same position. Chunk number 7 in `texts` is described by item
number 7 in `metadatas`. Later steps rely on that.

## 4. Report What You Made

At the end of the file, print the count, and print the first chunk so you can read it:

```python
print(f"Made {len(texts)} chunks from the documents.")
print(texts[0])
```

The second line is only for looking at the result. You will remove it in Step 5.

## Try it

```bash
uv run ingest.py
```

```text
Made 40 chunks from the documents.
HR Handbook > Working Hours
The standard working week is Monday to Friday. Core hours are 10:30 am to 4:30 pm, and every employee is expected to be available during them. The remaining hours can be arranged with the reporting manager. Total working time is 8 hours a day, including a 45-minute lunch break.
```

Change `texts[0]` to `texts[8]` and run it again to read a chunk from the leave policy.
Ask yourself whether someone who had only that card could answer a question from it.

## Checkpoint

<details>
<summary>Full <code>ingest.py</code> after this step</summary>

```python
from pathlib import Path

# Step 1 and 2: load every document and cut it into chunks, one chunk per "## Section".
texts, metadatas = [], []
for path in sorted(Path("docs").glob("*.md")):
    header, *sections = path.read_text().split("\n## ")
    title = header.splitlines()[0].lstrip("# ")
    for section in sections:
        heading, body = section.split("\n", 1)
        # The title and heading go inside the chunk, so it makes sense on its own.
        texts.append(f"{title} > {heading}\n{body.strip()}")
        metadatas.append({"source": title, "section": heading})

print(f"Made {len(texts)} chunks from the documents.")
print(texts[0])
```

</details>

This file is not finished. Steps 5 and 6 add to it, and Step 6 holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `Made 0 chunks`, then `IndexError: list index out of range` | `docs` was not found, usually because you ran the command from a different folder | Run `uv run ingest.py` from the folder that contains `docs` and `ingest.py` |
| `ValueError: not enough values to unpack` | A section has a heading but no text under it | Add at least one line of text below the heading |
| The count is lower than 40 | A file is missing, or a heading uses the wrong number of `#` | Re-check Step 3 |
| The chunk text starts with `# ` | `lstrip("# ")` was left out | Restore it, so the title has no leading `#` |

Next: **Step 5 — Embed the Chunks**.
