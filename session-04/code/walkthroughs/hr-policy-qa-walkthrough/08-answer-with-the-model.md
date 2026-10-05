# Step 8 — Answer with the Model

> Back to index · Previous: Retrieve the Top Chunks · Next: Recap and Exercises

## Goal

Finish `ask.py`: put the retrieved chunks and the question into one prompt, let `gpt-4o-mini`
write the answer from them, and refuse politely when the answer is not there.

## Why this matters

Until now the model has not been involved, and the app has only found text. This step adds
the last piece, and with it the one risk RAG is meant to remove: a model that answers from
memory instead of from your documents.

Two decisions in the prompt do the work.

The first is the **system message**. It tells the model to use only the context, and gives
it an exact sentence to use when the answer is missing. Without a clear way out, a model
tends to try to be helpful, and a helpful guess about a leave policy is a wrong answer
wearing a confident voice.

The second is the **shape of the user message**: the context first, then the question. The
model sees the chunks as the material it has been given, and the question as the thing to
answer from them.

Retrieval always returns four chunks, even for the France question in Step 7. The prompt
is therefore the only safeguard against an off-topic answer. That makes the "Retrieved
from" list under each answer important: it shows what the model was given, which is how
you tell a retrieval problem from a model problem.

## 1. Add the System Message

Below the line that opens the collection, add:

```python
SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)
```

## 2. Build the Prompt and Call the Model

Inside the loop, replace the line `print(chunks[0])` with:

```python
    # Step 6: send the chunks and the question to the model in one prompt.
    context = "\n\n".join(chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )

    print("AI:", response.choices[0].message.content)
```

| Part | What it does |
|---|---|
| `"\n\n".join(chunks)` | Joins the four chunk texts, with a blank line between them, into one block of context |
| `{"role": "system", ...}` | The standing rules for the model |
| `f"Context:\n{context}\n\nQuestion: {question}"` | The retrieved text, then the question |
| `response.choices[0].message.content` | The answer text, read as in `simple-chat` |

Reusing `response` for the chat reply is safe: the embedding response was already used to
build `result`, so the name can be taken over.

The "Retrieved from" printing stays exactly as it was, now below the answer.

## Try it

```bash
uv run ask.py
```

```text
You: Can a first-year employee carry forward unused leave?
AI: No, a first-year employee cannot carry forward any leave.
Retrieved from:
  - Leave Policy > Carry Forward of Leave
  - Leave Policy > Leave Without Pay
  - Leave Policy > Paid Leave Entitlement
  - Leave Policy > Casual Leave

You: My laptop was stolen last night. What should I do?
AI: You must report the stolen laptop to IT and your reporting manager within 24 hours. Additionally, you should file a police complaint and provide a copy of that complaint to IT.
Retrieved from:
  - Laptop and Equipment Policy > Loss, Theft and Damage
  - Laptop and Equipment Policy > Returning Equipment
  - IT Security Policy > Reporting a Security Incident
  - Laptop and Equipment Policy > Acceptable Use

You: What is the capital of France?
AI: I could not find that in the policy documents.
Retrieved from:
  - Laptop and Equipment Policy > Accessories
  - IT Security Policy > Passwords
  - Expense Reimbursement Policy > Travel Limits
  - Expense Reimbursement Policy > Meal Allowance

You: quit
```

The wording of the answers will differ a little from run to run. Look at the third answer:
the model was handed four unrelated chunks, and the system message is what made it say so
instead of improvising.

## Seeing a Weak Spot

Ask this question three or four times:

```text
You: I joined 8 months ago. Can I carry forward my unused leave?
```

The "Retrieved from" list starts with Leave Policy > Carry Forward of Leave every time, so
retrieval is working. But the answer changes between runs: sometimes "No, you cannot carry
forward any leave since you are in your first year of service", and sometimes "I could not
find that in the policy documents." The document says "first year of service", the
question says "8 months", and the model has to connect the two. Sometimes it does and
sometimes it plays safe.

This is the habit to build. Check "Retrieved from" first: if the right section is there,
the problem is on the model side, and a clearer question or a more specific instruction
usually helps.

## Checkpoint

<details>
<summary>Full <code>ask.py</code></summary>

```python
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

print("Ask about company policies. Type 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    # Step 5: turn the question into a vector (same model as ingest.py), then
    # fetch the 4 stored chunks whose vectors are closest to it.
    response = client.embeddings.create(model="text-embedding-3-small", input=question)
    result = collection.query(query_embeddings=[response.data[0].embedding], n_results=4)
    chunks = result["documents"][0]

    # Step 6: send the chunks and the question to the model in one prompt.
    context = "\n\n".join(chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )

    print("AI:", response.choices[0].message.content)
    print("Retrieved from:")
    for meta in result["metadatas"][0]:
        print(f"  - {meta['source']} > {meta['section']}")
    print()
```

</details>

This matches the reference project's `ask.py` exactly.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `NameError: name 'chunks' is not defined` | The retrieval lines from Step 7 were removed along with `print(chunks[0])` | Only replace the single `print(chunks[0])` line. The three retrieval lines stay |
| Every answer is "I could not find that in the policy documents." | The context is empty or wrong, for example `chunks` is an empty list, or `ingest.py` stored nothing | Print `context` before the model call and check that it holds policy text |
| The model answers questions that are not in the documents | The system message was changed, or `Use ONLY the context provided.` was dropped | Restore the system message and ask the off-topic question again |
| `AuthenticationError` or `RateLimitError` appears mid-session | Key problem or quota, as in Step 5 | Check `.env` and your account; wait a minute and retry |

Next: **Step 9 — Recap and Exercises**.
