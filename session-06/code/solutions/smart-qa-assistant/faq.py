"""Frequently asked questions: approved answers returned without calling the chat model.

A new question is compared with the FAQ questions by meaning. Only a very close match
counts; anything else goes to the agent.
"""

import json
from pathlib import Path

import numpy as np

import config

_entries = json.loads(Path("faq.json").read_text())
_vectors = None


def _embed(texts: list[str]) -> np.ndarray:
    vectors = np.array(config.Settings.embed_model.get_text_embedding_batch(texts))
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)  # unit length


def lookup(question: str) -> dict | None:
    """Return the FAQ entry that matches the question, or None."""
    global _vectors
    if _vectors is None:  # embed the FAQ questions once, on first use
        _vectors = _embed([entry["question"] for entry in _entries])
    scores = _vectors @ _embed([question])[0]
    best = int(scores.argmax())
    if scores[best] >= config.FAQ_MIN_SCORE:
        return {**_entries[best], "score": float(scores[best])}
    return None
