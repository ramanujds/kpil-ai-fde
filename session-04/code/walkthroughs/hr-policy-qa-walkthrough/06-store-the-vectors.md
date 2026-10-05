# Step 6 — Store the Vectors

> Back to index · Previous: Embed the Chunks · Next: Retrieve the Top Chunks

## Goal

Finish `ingest.py` by saving the vectors, the chunk texts and their metadata in a Chroma
vector store, so that `ask.py` can search them later without embedding anything again.

## Why this matters

At the moment the 40 vectors live in a Python variable. The moment the script ends, they
are gone, and the next run would pay to embed the same text again. A vector store solves two
problems at once: it keeps the vectors on disk, and it is built to answer one question
quickly, "which stored vectors are closest to this one?".

Three things are stored together for each chunk, and each has a job:

| Stored | Used for |
|---|---|
| The vector | Finding the chunks closest in meaning to a question |
| The chunk text | Handing to the model once the chunk has been found |
| The metadata (source, section) | Telling the user where an answer came from |

Chroma needs an `id` for every chunk too. Here the id is the source and section name,
which is unique. Because the ids are stable, running `ingest.py` again updates the existing
chunks instead of adding duplicates.

## 1. Add the Chroma Import

Add `import chromadb` to the imports, in the group with the other packages:

```python
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
```

## 2. Remove the Looking-Only Lines

Delete the two temporary lines from Step 5:

```python
print(f"Embedded {len(vectors)} chunks. Each vector has {len(vectors[0])} numbers.")
print(vectors[0][:5])
```

## 3. Create the Store and Save the Chunks

Add this at the end of the file:

```python
# Step 4: store the vectors, with the original text and the source of each chunk.
collection = chromadb.PersistentClient(path=".chroma").get_or_create_collection(
    "policies", metadata={"hnsw:space": "cosine"}
)
collection.upsert(
    ids=[f"{m['source']} > {m['section']}" for m in metadatas],
    embeddings=vectors,
    documents=texts,
    metadatas=metadatas,
)

print(f"Stored {collection.count()} chunks. Now run ask.py.")
```

| Part | What it does |
|---|---|
| `PersistentClient(path=".chroma")` | Keeps the store on disk in a `.chroma` folder, so it survives after the script ends |
| `get_or_create_collection("policies", ...)` | A collection is a named set of chunks, like a table. It is created the first time and reused afterwards |
| `"hnsw:space": "cosine"` | Measure closeness by the angle between vectors, the usual choice for text embeddings |
| `upsert(...)` | Insert each chunk, or update it if the id already exists |
| `ids`, `embeddings`, `documents`, `metadatas` | Four lists, all the same length and in the same order. Item 7 of each describes the same chunk |

## Try it

```bash
uv run ingest.py
```

```text
Made 40 chunks from the documents.
Stored 40 chunks. Now run ask.py.
```

Now run it a second time:

```bash
uv run ingest.py
```

```text
Made 40 chunks from the documents.
Stored 40 chunks. Now run ask.py.
```

The count stays at 40. Because of the stable ids, `upsert` replaced the 40 chunks instead
of adding another 40. You will also see a new `.chroma` folder in the project; Git ignores
it.

## Checkpoint

<details>
<summary>Full <code>ingest.py</code></summary>

```python
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()

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

# Step 3: turn every chunk into a vector (a list of numbers that captures its meaning).
response = client.embeddings.create(model="text-embedding-3-small", input=texts)
vectors = [item.embedding for item in response.data]

# Step 4: store the vectors, with the original text and the source of each chunk.
collection = chromadb.PersistentClient(path=".chroma").get_or_create_collection(
    "policies", metadata={"hnsw:space": "cosine"}
)
collection.upsert(
    ids=[f"{m['source']} > {m['section']}" for m in metadatas],
    embeddings=vectors,
    documents=texts,
    metadatas=metadatas,
)

print(f"Stored {collection.count()} chunks. Now run ask.py.")
```

</details>

This matches the reference project's `ingest.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'chromadb'` | The environment was not built, or `python ingest.py` was used instead of `uv run ingest.py` | Run `uv sync`, then `uv run ingest.py` |
| `Collection expecting embedding with dimension of 1536, got ...` | The store was built with one embedding model, and you now embed with another | Delete the `.chroma` folder and run `ingest.py` again with the model you want |
| A section you deleted from a document is still found | `upsert` updates existing ids but never removes old ones | Delete the `.chroma` folder and run `ingest.py` again |
| The count is 80 after a second run | The ids are not stable, for example they include a counter or a timestamp | Build the id from the source and section name, as above |

Next: **Step 7 — Retrieve the Top Chunks**.
