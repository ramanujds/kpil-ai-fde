"""Reads each file type and cuts it into nodes (LlamaIndex's word for chunks).

The point of this file: one chunking rule does not fit every format. Each function below
picks the natural unit of its format.

    .md    one node per heading
    .docx  converted to markdown first, then one node per heading
    .pdf   one document per page, then size-based chunks with overlap
    .xlsx  one node per row, written out as "column: value" text
    .csv   one node per row, written out as a question and answer
"""
import csv
from pathlib import Path

from docx import Document as WordDocument
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.readers.file import PDFReader
from openpyxl import load_workbook

# Metadata that helps filtering and showing sources, but that we do not want mixed into the
# text that gets embedded.
NO_EMBED = ["file_type", "page", "row", "sheet"]


def base_metadata(path):
    return {"file_name": path.name, "file_type": path.suffix.lstrip(".").lower()}


def finish(nodes):
    """Keep location metadata out of the embedded text and out of the prompt text."""
    for node in nodes:
        node.excluded_embed_metadata_keys = NO_EMBED
        node.excluded_llm_metadata_keys = NO_EMBED
    return nodes


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


# File extension -> the function that knows how to read and chunk it.
LOADERS = {
    ".md": markdown_nodes,
    ".docx": docx_nodes,
    ".pdf": pdf_nodes,
    ".xlsx": xlsx_nodes,
    ".csv": csv_nodes,
}


def load_nodes(docs_dir):
    nodes = []
    for path in sorted(Path(docs_dir).iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            print(f"Skipping {path.name}: no loader for {path.suffix}")
            continue
        nodes.extend(finish(loader(path)))
    return nodes
