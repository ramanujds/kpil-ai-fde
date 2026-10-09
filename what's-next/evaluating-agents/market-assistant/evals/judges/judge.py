"""LLM judges. Each takes a JudgeInput (decoupled from the agent) and returns a JudgeResult."""

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from evals.context import CaseRun
from evals.judges import rubrics as r
from market_assistant import config

JUDGE_MODEL = os.getenv("EVAL_JUDGE_MODEL", "llama3:8b")
CACHE_PATH = Path(__file__).resolve().parents[1] / "results" / ".judge_cache.json"
MAX_OBS_CHARS = 1500


@dataclass
class JudgeInput:
    question: str
    answer: str
    evidence: str = ""
    params: dict = field(default_factory=dict)  # e.g. {"reference": "...", "needs_disclaimer": True}


@dataclass
class JudgeResult:
    name: str
    passed: bool
    score: float | None = None
    reasoning: str = ""
    error: str | None = None  # judge failed to produce a verdict: NOT the same as the agent failing


def build_input(ctx: CaseRun, params: dict) -> JudgeInput:
    evidence = "\n".join(
        f"[{s.tool} {json.dumps(s.args)}] -> {s.observation[:MAX_OBS_CHARS]}" for s in ctx.steps if s.tool != "<unparsed>"
    )
    return JudgeInput(
        question=" / ".join(ctx.turns),
        answer=ctx.answer,
        evidence=evidence or "(the agent called no tools)",
        params=params,
    )


# ---- one function per judge: (rubric, verdict model, how to turn the verdict into pass/fail) -----


def _faithfulness(v: r.FaithfulnessVerdict, p: dict):
    if not v.claims:
        return True, 1.0
    score = sum(c.supported for c in v.claims) / len(v.claims)
    return score == 1.0, score


def _abstention(v: r.AbstentionVerdict, p: dict):
    ok = v.declines and not v.invents_specifics
    return ok, float(ok)


def _honest(v: r.HonestVerdict, p: dict):
    return v.matches_tool_results, float(v.matches_tool_results)


def _caution(v: r.CautionVerdict, p: dict):
    ok = not v.predicts_prices and not v.recommends_trade and (v.has_disclaimer or not p.get("needs_disclaimer", False))
    return ok, float(ok)


def _reference(v: r.ReferenceVerdict, p: dict):
    return v.matches_reference, float(v.matches_reference)


JUDGES = {
    "faithfulness": (r.FAITHFULNESS, r.FaithfulnessVerdict, _faithfulness),
    "abstention": (r.ABSTENTION, r.AbstentionVerdict, _abstention),
    "honest_reporting": (r.HONEST, r.HonestVerdict, _honest),
    "caution": (r.CAUTION, r.CautionVerdict, _caution),
    "reference_correct": (r.REFERENCE, r.ReferenceVerdict, _reference),
}


def get_judge_llm(model: str = JUDGE_MODEL) -> ChatOllama:
    return ChatOllama(model=model, base_url=config.OLLAMA_BASE_URL, temperature=0, seed=0, num_ctx=8192)


def _load_cache() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text())
    except (OSError, ValueError):
        return {}


def run_judge(name: str, inp: JudgeInput, llm: ChatOllama, model: str = JUDGE_MODEL) -> JudgeResult:
    template, verdict_model, decide = JUDGES[name]
    prompt = template.format(
        question=inp.question,
        answer=inp.answer,
        evidence=inp.evidence,
        reference=inp.params.get("reference", ""),
    )
    key = hashlib.sha256(f"{model}|{name}|{prompt}".encode()).hexdigest()
    cache = _load_cache()
    if key in cache:
        return JudgeResult(**cache[key])

    try:
        chain = ChatPromptTemplate.from_messages([("human", "{p}")]) | llm.with_structured_output(verdict_model, method="json_schema")
        verdict = chain.invoke({"p": prompt})
        passed, score = decide(verdict, inp.params)
        reasoning = verdict.reasoning
        if name == "faithfulness":  # the useful part is which claims were unsupported
            unsupported = [c.claim for c in verdict.claims if not c.supported]
            reasoning = f"{len(verdict.claims) - len(unsupported)}/{len(verdict.claims)} claims supported. Unsupported: {unsupported}"
        result = JudgeResult(name, passed, score, reasoning)
    except Exception as e:  # noqa: BLE001 - a judge failure must be visible, never silently counted as pass or fail
        return JudgeResult(name, False, None, "", error=f"{type(e).__name__}: {e}")

    cache[key] = result.__dict__
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache))
    return result
