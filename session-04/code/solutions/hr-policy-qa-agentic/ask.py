import json
from datetime import date
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()
client = OpenAI()

MAX_STEPS = 5  # the most tool rounds the agent gets for one question

collection = chromadb.PersistentClient(path=".chroma").get_collection("policies")
employees = json.loads(Path("employees.json").read_text())

# The document names in the store, so the agent can search one document at a time.
documents = sorted({m["source"] for m in collection.get(include=["metadatas"])["metadatas"]})

SYSTEM = (
    "You answer questions about company policies. You have two tools: search_policies "
    "and get_my_profile.\n"
    "- Never state a policy fact from memory. Use ONLY text returned by search_policies.\n"
    "- If a question has several parts, or spans several documents, search for each part "
    "separately.\n"
    "- If the results look weak or off-topic, rewrite the query or try another document "
    "before giving up.\n"
    "- If the answer depends on the user's own situation (probation, first year, level, "
    "notice period, leave earned so far), call get_my_profile FIRST. Then search for the "
    "rule that applies to that situation. Never ask the user for facts the profile has.\n"
    "- For greetings and small talk, answer directly without any tool.\n"
    "- Cite every fact as [Document > Section]. If the answer is not in the documents, "
    "say 'I could not find that in the policy documents.' Do not guess."
)

# Sources of every chunk the agent reads while answering one question.
retrieved = []


# ---------------------------------------------------------------------------
# The tools: ordinary Python functions the model is allowed to ask for.
# ---------------------------------------------------------------------------


def search_policies(query, document=None):
    embedding = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
    result = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        where={"source": document} if document else None,
    )
    found = []
    for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        retrieved.append(f"{meta['source']} > {meta['section']}")
        # Cosine distance becomes a 0-to-1 relevance score the model can judge.
        found.append({"source": meta["source"], "section": meta["section"], "relevance": round(1 - distance, 2), "text": text})
    return json.dumps(found)


def get_my_profile():
    # Only the signed-in user's own record is ever returned. The model cannot ask for anyone else's.
    joined = date.fromisoformat(me["joined"])
    today = date.today()
    months = (today.year - joined.year) * 12 + today.month - joined.month - (today.day < joined.day)
    return json.dumps({**me, "months_of_service": months, "today": today.isoformat()})


TOOL_FUNCTIONS = {"search_policies": search_policies, "get_my_profile": get_my_profile}

# What the model sees: a name, a description and the arguments for each tool.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_policies",
            "description": (
                "Search the company policy documents and return the 3 most relevant sections. "
                "Each result has a relevance score from 0 to 1; below about 0.3 usually means "
                "the text is not about the question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "A complete, standalone search query."},
                    "document": {
                        "type": "string",
                        "enum": documents,
                        "description": "Optional. Search only this document.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_profile",
            "description": "Get the signed-in employee's name, role, level, department, joining date and months of service.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def run_tool(call):
    """Run one tool the model asked for. A mistake goes back to the model as text instead of crashing."""
    name = call.function.name
    try:
        args = json.loads(call.function.arguments or "{}")
        shown = ", ".join(f"{key}={value!r}" for key, value in args.items())
        print(f"  -> {name}({shown})")
        return TOOL_FUNCTIONS[name](**args)
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"  -> {name} failed: {error!r}")
        return json.dumps({"error": f"Could not run {name}: {error!r}"})


# ---------------------------------------------------------------------------
# The agent loop: ask the model, run the tools it requests, repeat until it answers.
# ---------------------------------------------------------------------------
def run_agent(messages):
    for _ in range(MAX_STEPS):
        reply = client.chat.completions.create(model="gpt-4o", messages=messages, tools=TOOLS).choices[0].message
        messages.append(reply)

        if not reply.tool_calls:  # no tool requested: this is the final answer
            return reply.content

        for call in reply.tool_calls:
            messages.append({"role": "tool", "tool_call_id": call.id, "content": run_tool(call)})

    # Step cap reached: stop the searching and make the model answer with what it has.
    print(f"  (step limit of {MAX_STEPS} reached)")
    messages.append({"role": "user", "content": "Stop searching. Answer now from what you have found, or say you could not find it."})
    reply = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS, tool_choice="none").choices[0].message
    messages.append(reply)
    return reply.content


employee_id = input("Your employee ID (for example E101): ").strip().upper()
if employee_id not in employees:
    raise SystemExit(f"Unknown employee ID. Try one of: {', '.join(employees)}")
me = employees[employee_id]

print(f"\nHello {me['name']}. Ask about company policies. Type 'quit' to exit.\n")

# The history is kept between questions, so a follow-up like "and does it carry forward?" still makes sense.
messages = [{"role": "system", "content": SYSTEM}]

while True:
    question = input("You: ")

    if question.lower() in ("quit", "exit"):
        break

    checkpoint = len(messages)
    retrieved.clear()
    messages.append({"role": "user", "content": question})

    try:
        answer = run_agent(messages)
    except OpenAIError as error:  # rate limit, bad key, network
        del messages[checkpoint:]  # drop the half-finished turn so the next question starts clean
        print(f"The model call failed: {error}\n")
        continue

    print("AI:", answer)
    if retrieved:
        print("Retrieved from:")
        for source in dict.fromkeys(retrieved):  # unique, in the order they were read
            print(f"  - {source}")
    print()
