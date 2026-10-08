import sys

from dotenv import load_dotenv

from retrieval import build_retrievers, configure_models, describe, open_index, open_nodes

load_dotenv()
configure_models()

# Questions that mix exact codes and plain meaning. Pass your own as arguments:
#   uv run compare_retrieval.py "your question here"
QUESTIONS = [
    "hotel limit for L3",
    "How many days of sick leave does an L4 get?",
    "Do I need approval for a trip that costs 30,000 INR?",
    "Can I get reimbursed for a course I paid for myself?",
]

questions = sys.argv[1:] or QUESTIONS
vector, keyword, hybrid = build_retrievers(open_index(), open_nodes(), top_k=3)

for question in questions:
    print(f"\nQuestion: {question}")
    for name, retriever in [("vector", vector), ("keyword", keyword), ("hybrid", hybrid)]:
        print(f"  {name}:")
        for result in retriever.retrieve(question):
            print(f"    {result.score:7.3f}  {describe(result.node)}")
