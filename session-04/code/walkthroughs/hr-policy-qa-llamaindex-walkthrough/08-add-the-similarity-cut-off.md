# Step 8 — Add the Similarity Cut-off

> Back to index · Previous: Answer with a Chat Engine · Next: Recap and Exercises

## Goal

Finish `ask.py`: drop retrieved nodes that score below a threshold, and show a clear
message when nothing is left.

## Why this matters

Retrieval always returns four nodes, because it returns the k closest, however far away they
are. You saw this in the hand-built app and again in Step 6: the France question came
back with four unrelated sections. In both apps, the system message was the only thing
standing between that and an invented answer.

A **similarity cut-off** adds a second safeguard, earlier in the pipeline. After the
nodes are retrieved and before the prompt is built, a **postprocessor** removes every node
whose score is below the threshold. For an off-topic question, nothing may survive, the
model is given no context, and it should fall back to the "could not find" sentence. The model
is also no longer shown four irrelevant paragraphs that it might be tempted to use.

The threshold is a judgement, not a fact. It depends on your documents and your embedding
model. Set it too low and it filters nothing. Set it too high and it throws away good
nodes, and the app says "could not find" about questions it could have answered. That
second failure is quiet: no error appears, only a worse assistant. For that reason the
code prints an explicit line when no node passes, so you can see it happen.

The starting value used here, 0.3, is a guess to test, not an answer. You have the right
data to test it with: the scores you wrote down at the end of Step 6.

## 1. Add the Postprocessor

Add the import in alphabetical order, under the `llama_index.core` import:

```python
from llama_index.core.postprocessor import SimilarityPostprocessor
```

Change the chat engine, and the second comment line above it:

```python
# Steps 5 and 6 in one object. A chat engine in this mode:
#   - rewrites a follow-up ("And does it carry forward?") into a full question,
#   - retrieves the 4 closest nodes, dropping any below the similarity cut-off,
#   - sends the nodes and the question to the model, and remembers the conversation.
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    similarity_top_k=4,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.3)],
    system_prompt=SYSTEM,
)
```

`node_postprocessors` is a list of steps applied, in order, to the retrieved nodes.
`SimilarityPostprocessor(similarity_cutoff=0.3)` keeps only nodes whose score is 0.3 or
higher. The postprocessor sits between retrieval and the prompt, so it also applies to the
rewritten follow-up questions.

## 2. Handle the Empty Case

In the loop, add a check between the "Retrieved from:" line and the `for` loop:

```python
    if not response.source_nodes:
        print("  - nothing above the similarity cut-off")
```

If the list is empty the `for` loop does nothing, so the message is what tells you why no
sources were shown.

## 3. Choose the Value From Your Own Numbers

Take the page of scores from Step 6 and read it as two groups.

| Group | What to find | Example of what you write |
|---|---|---|
| Questions the documents answer | The lowest top score among them | "My lowest good top score was 0.xx" |
| The France question | The highest score among its four nodes | "My highest France score was 0.xx" |

A good cut-off sits **above** the second number and **below** the first. If your France
scores are all under 0.3 and your good questions are all over it, 0.3 is fine. If one
France node scored 0.35, then 0.3 filters nothing for it, and you should move the value up
until that node drops out while your good questions still pass. If the two groups overlap,
no single number separates them, and you have learned something about your documents or
your questions that a bare cut-off cannot fix.

## Try it

```bash
uv run ask.py
```

First the France question:

```text
You: What is the capital of France?
AI: I could not find that in the policy documents.
Retrieved from:
  - nothing above the similarity cut-off
```

That is the result when every France score is under your cut-off, and the sentence comes
from your `SYSTEM` message. If a node or two still shows, your cut-off is below a France score, and the section above is how to choose again.

Then a pair of questions that the documents answer:

```text
You: I joined 8 months ago. Can I carry forward my unused leave?
AI: (an answer about first-year employees, or the "could not find" sentence)
Retrieved from:
  - 02_leave_policy.md > Carry Forward of Leave (score 0.xx)
  - (any other nodes that passed)
```

As in the hand-built walkthrough, this one can give different answers between runs,
because "8 months" has to be connected to "first year of service". Check "Retrieved from"
first. If Carry Forward of Leave is there, retrieval worked.

Now break it on purpose, to see both failures. Change `similarity_cutoff` to `0.9`, and
ask a question the documents answer:

```text
You: How many days of sick leave do I get?
AI: I could not find that in the policy documents.
Retrieved from:
  - nothing above the similarity cut-off
```

The app answered "could not find" for a question it can answer, with no error. That is
the quiet failure. Change the value to `0.0` and the France question is answered from four
unrelated nodes again. Set it back to the value your numbers support.

## Checkpoint

<details>
<summary>Full <code>ask.py</code></summary>

```python
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# The same embedding model as ingest.py, plus the chat model.
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-4o-mini")

SYSTEM = (
    "You answer questions about company policies. Use ONLY the context provided. "
    "If the answer is not in the context, say 'I could not find that in the policy documents.' "
    "Do not guess."
)

# Open the Chroma collection that ingest.py filled, and wrap it as an index.
collection = chromadb.PersistentClient(path=".chroma").get_collection("policies_llamaindex")
index = VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))

# Steps 5 and 6 in one object. A chat engine in this mode:
#   - rewrites a follow-up ("And does it carry forward?") into a full question,
#   - retrieves the 4 closest nodes, dropping any below the similarity cut-off,
#   - sends the nodes and the question to the model, and remembers the conversation.
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    similarity_top_k=4,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.3)],
    system_prompt=SYSTEM,
)

print("Ask about company policies. Type 'reset' to forget the conversation, 'quit' to exit.\n")

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break
    if question.lower() == "reset":
        chat_engine.reset()
        print("Conversation cleared.\n")
        continue

    response = chat_engine.chat(question)

    print("AI:", response)
    print("Retrieved from:")
    if not response.source_nodes:
        print("  - nothing above the similarity cut-off")
    for node in response.source_nodes:
        heading = node.text.splitlines()[0].lstrip("# ")
        print(f"  - {node.metadata['file_name']} > {heading} (score {node.score:.2f})")
    print()
```

</details>

This matches the reference project's `ask.py` exactly. If you chose a cut-off other than
0.3 from your own numbers, that one value will differ, and that is expected.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| Every question says "nothing above the similarity cut-off" | The cut-off is higher than every score | Lower the value. Set it to `0.0` for a moment and read the scores to see what your range is |
| The France question still shows nodes | The cut-off is below one of the France scores | Raise it, using your Step 6 numbers |
| `ImportError` for `SimilarityPostprocessor` | The import path is wrong | It is `from llama_index.core.postprocessor import SimilarityPostprocessor` |
| `TypeError` mentioning `node_postprocessors` | It was given a single object and not a list | Keep the square brackets: `[SimilarityPostprocessor(...)]` |
| The message prints after the list of sources | The `if not ...` check was placed below the `for` loop | Put it between the `print("Retrieved from:")` line and the `for` loop |

Next: **Step 9 — Recap and Exercises**.
