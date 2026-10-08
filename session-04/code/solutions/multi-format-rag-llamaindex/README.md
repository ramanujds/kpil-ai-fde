# Multi-Format RAG with LlamaIndex

A document assistant for company policies that live in different kinds of files: a Markdown handbook, a PDF policy, an Excel workbook, a Word checklist and a CSV of FAQs. You ask a question, the app finds the right parts across all of them, and the model answers from those parts only.

The lesson: **one chunking rule does not fit every format, and one retrieval method does not fit every question.** Each file type is cut in the way that suits it, and retrieval combines meaning search with exact-word search.

The documents in `docs/` are synthetic. "Acme" is a made-up company.

## Prerequisites

1. **uv**, the Python package manager.
2. An OpenAI API key.

## Files

| File | What it does |
|---|---|
| `docs/` | Five sources: `employee_handbook.md`, `travel_policy.pdf`, `expense_limits.xlsx`, `onboarding_checklist.docx`, `hr_faq.csv`. |
| `make_sample_data.py` | Optional. Regenerates the PDF, Excel and Word files. The generated files are already in `docs/`, so you do not need to run it. |
| `loaders.py` | Reads each file type and cuts it into nodes. This is where the chunking strategies live. |
| `ingest.py` | Run once. Calls `loaders.py`, embeds the nodes, stores them in Chroma in `.chroma/`, and saves a copy of the node text in `.store/` for keyword search. |
| `retrieval.py` | Shared setup: models, the vector, keyword and hybrid retrievers, and the file type filter. |
| `ask.py` | Run for every question. A chat engine over the hybrid retriever, with memory, and a source list showing the file and the place inside it. |
| `compare_retrieval.py` | Runs the same questions through vector, keyword and hybrid retrieval and prints the results side by side. |
| `.env.example` | Template for the key. Copy it to `.env` and paste your key. `.env` is ignored by Git. |

## Chunking per File Type

| Format | Natural unit | How it is cut | Metadata kept |
|---|---|---|---|
| Markdown | A section under a heading | `MarkdownNodeParser`, one node per heading | file name, file type |
| Word | A section under a heading | Rebuilt as markdown from the Word heading styles, then the same parser | file name, file type |
| PDF | A page, but pages hold several topics | One document per page, then `SentenceSplitter` with 256 tokens and 40 overlap | file name, page number |
| Excel | A row | One node per row, written as "Sheet: Travel Limits. Grade: L3. Hotel Limit Per Night (INR): 6000. ..." | file name, sheet, row |
| CSV | A row | One node per row, written as "Question: ... Answer: ..." | file name, category, row |

Why these choices:

- A spreadsheet row such as `L3, 6000, 1500` means nothing without its column names. Writing the headers into each node makes the row readable on its own, to the embedding model and to the answering model.
- Cutting a spreadsheet by size would split a row in half. A PDF has no headings to split on, so size is all we have, and the overlap keeps a sentence on a boundary from being lost.
- A Word file read as plain text loses its headings. Converting it to markdown first keeps the section structure.
- Location metadata (page, sheet, row) is kept out of the embedded text. It is there for filtering and for showing sources.

## Retrieval

`ask.py` uses **hybrid retrieval**:

| Retriever | Good at | Weak at |
|---|---|---|
| Vector search | Meaning. "Can I get money back for a course I paid for?" finds the training reimbursement FAQ. | Exact tokens. "L3" and "L4" look almost the same to an embedding model. |
| Keyword search (BM25) | Exact words and codes: "L3", "25,000", "Grade". | Different words for the same idea. |
| Hybrid | Both. The two ranked lists are merged with reciprocal rank fusion. | A little more setup. |

A metadata filter sits on top. Type `/only pdf` to search only the PDF, `/only xlsx` for only the spreadsheet, and `/only all` to go back to everything.

## Run

Copy `.env.example` to `.env` and put your real key in it, then:

```
uv sync
uv run ingest.py
uv run ask.py
```

Run `ingest.py` again only when you change the documents. It rebuilds the collection from scratch each time.

To see the retrievers side by side:

```
uv run compare_retrieval.py
uv run compare_retrieval.py "your own question"
```

## Try It

1. Run `ingest.py` and read the "Nodes per file type" table. Spreadsheet and CSV rows each became a node. The PDF became several nodes per page.
2. Ask "What is the hotel limit for an L3?". The answer comes from one spreadsheet row. Check the source list.
3. Ask "Do I need approval for a trip that costs 30,000 INR?". The answer comes from the PDF.
4. Ask "I am an L3 and my hotel was 7,000 INR a night. What happens?". The model needs the limit from the Excel file and the rule from the PDF. Check that both appear in the sources.
5. Type `/only pdf` and ask question 2 again. The spreadsheet is out of reach, so the model should say it could not find the answer.
6. Run `compare_retrieval.py`. For "hotel limit for L3", compare which rows the vector list and the keyword list return, and what hybrid keeps.
7. In `loaders.py`, change `chunk_size` for the PDF from 256 to 1024, run `ingest.py` again, and see how the PDF nodes and the answers change.

## Notes

- Hybrid scores are rank-fusion scores, around 0.01 to 0.03, so they cannot be compared with the cosine scores of a vector-only app. This app therefore has no similarity cut-off. When nothing relevant exists, the system prompt is what makes the model say it could not find the answer.
- The embedding model in `retrieval.py` is used by both `ingest.py` and `ask.py`, so they always match.
- BM25Retriever has a `filters` option, but in our tests it did not restrict results. `retrieval.py` filters the nodes itself before building the keyword index.
- Scanned PDFs (pictures of pages) have no text to extract and would need OCR. This app does not cover that.
- A spreadsheet with merged cells, several tables on one sheet or formulas will need more careful loading than the simple "one header row, then data rows" layout used here. Formula cells are read as their last saved values.
- The collection is named `multi_format_docs`, so this app does not share a store with the other solutions.
- LlamaIndex's class names and imports change between versions. If an import fails after an upgrade, check the current LlamaIndex documentation.
