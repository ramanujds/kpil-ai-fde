# Step 5 — Embed the Chunks

> Back to index · Previous: Load and Chunk · Next: Store the Vectors

## Goal

Turn every chunk into an embedding, a list of numbers that captures what the chunk means.

## Why this matters

A computer can easily check whether two texts share words. It cannot check whether they
share a meaning. "Can I roll over my vacation days?" and "Unused paid leave carries forward
to the next leave year" have almost no important word in common, yet they are about the
same thing.

An embedding model solves this. It reads a piece of text and returns a long list of
numbers, arranged so that texts with similar meaning get similar numbers. Once every chunk
has been turned into numbers, "find the chunk that means the same as this question" becomes
"find the stored numbers closest to these numbers", which a computer can do quickly.

You pay for embeddings per token, and free tiers have limits, so the 40 chunks are sent in
one request rather than 40. The cost of embedding is paid once, here. After that, only
each new question has to be embedded.

## 1. Create the Client

Add the imports at the top of `ingest.py`, below the `Path` import, and create the client
before the chunking code:

```python
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Reads OPENAI_API_KEY from the .env file. The OpenAI client picks it up automatically.
load_dotenv()
client = OpenAI()
```

`load_dotenv()` copies the lines of `.env` into the environment. `OpenAI()` then finds
`OPENAI_API_KEY` there on its own, so the key never appears in your code.

## 2. Embed All Chunks in One Call

After the chunking code, replace the line `print(texts[0])` with the embedding step:

```python
# Step 3: turn every chunk into a vector (a list of numbers that captures its meaning).
response = client.embeddings.create(model="text-embedding-3-small", input=texts)
vectors = [item.embedding for item in response.data]
```

Passing a list as `input` embeds every item and returns the results in the same order.
`response.data` holds one entry per chunk, and each entry's `.embedding` is its list of
numbers. The order matches `texts`, so `vectors[7]` belongs to `texts[7]` and `metadatas[7]`.

## 3. Look at the Result

Print how many vectors there are and how long each one is, then print the first few
numbers of one:

```python
print(f"Embedded {len(vectors)} chunks. Each vector has {len(vectors[0])} numbers.")
print(vectors[0][:5])
```

This is again only for looking. You will remove these lines in Step 6.

## Try it

```bash
uv run ingest.py
```

```text
Made 40 chunks from the documents.
Embedded 40 chunks. Each vector has 1536 numbers.
[-0.048858642578125, 0.0654296875, 0.10662841796875, -0.00286102294921875, -0.0008640289306640625]
```

Your first five numbers may differ in the last digits. Nobody can say what the number in
position 3 stands for; the model learned these scales on its own. What matters is that
every chunk, and later every question, gets a list of exactly 1536 numbers, so they can be
compared position by position.

## Checkpoint

<details>
<summary>Full <code>ingest.py</code> after this step</summary>

```python
from pathlib import Path

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

print(f"Embedded {len(vectors)} chunks. Each vector has {len(vectors[0])} numbers.")
print(vectors[0][:5])
```

</details>

This file is not finished. Step 6 adds the last part and holds the final version.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `OpenAIError: Missing credentials. Please pass an api_key ...` | `.env` is missing, misnamed, in the wrong folder, or has no `OPENAI_API_KEY` line | Re-check Step 2, including the `key found` test |
| `AuthenticationError ... Incorrect API key provided` | The key in `.env` is wrong, revoked, or has extra spaces or quotes around it | Copy the key again into `.env`, with no quotes |
| `RateLimitError` or an error about quota | The account has no credit, or a free-tier limit was reached | Wait a minute and retry; check the billing page of your OpenAI account |
| `BadRequestError` about empty input | One chunk text is empty | Re-check the documents for a section with no text |

Next: **Step 6 — Store the Vectors**.
