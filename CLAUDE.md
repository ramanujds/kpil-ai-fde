# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repo is

Training material for the **AI Developer & FDE Training** program delivered to Kalpataru
Projects (Ahmedabad) by ADaSci. Six days, 4 hours/day, two batches (forenoon/afternoon).
Audience is a mix of developers (Python/APIs/Git assumed) and business users (no coding).

- [Kalpataru_AI_Developer_FDE_Course.md](Kalpataru_AI_Developer_FDE_Course.md) — the full
  course overview: schedule, audience map, toolchain, FDE six-pillar model.
- `session-01` … `session-06` — one folder per training day. The established layout, per
  folder:
  - `schedule.md` — agenda, timing, topic lists, labs, learning objectives, ground rules
    (originally named `DayN_*_Schedule.md`; `session-01` is renamed, others still pending).
  - `intro.md` — a short orientation page: why the day matters, how it connects to the rest
    of the program, today's journey at a glance, before-you-start checklist.
  - `notes/` — one markdown file per topic block: storytelling, plain examples and Mermaid
    diagrams. **No code in notes, and no `code/` folders unless the user asks.**

This is not an application codebase — there is no build, test, or package config here. It is
a content repository: markdown + Mermaid diagrams, plus (going forward) Python teaching
examples.

### Day-to-folder map

| Day | Folder | Topic | Course output |
|---|---|---|---|
| 1 | `session-01` | AI Developer Foundations | Prompt patterns + API/environment setup |
| 2 | `session-02` | Microsoft Copilot Hands-on | Business workflow exercises |
| 3 | `session-03` | Python + LLM APIs | LLM-powered utility app |
| 4 | `session-04` | RAG + Vector Databases | Document knowledge assistant |
| 5 | `session-05` | AI Agents + FDE Architecture | Agentic workflow blueprint |
| 6 | `session-06` | Industry Use Case + Assessment | Caselet demo |

## The gap this repo is being filled in for

Every `DayN_*_Schedule.md` file carries a scope note near the top, e.g.:

> Scope note: this document covers structure, timing, topics and outputs only. Code, worked
> examples, datasets and demo content will be developed separately.

The schedule files are the skeleton (what's taught, when, in what order). The task going
forward is to build the **flesh**: per-topic Python content — explanations, runnable code,
workflow diagrams, walkthroughs and use cases — that trainers and trainees use during each
block and lab named in the schedules.

When asked to "write the content for Day X / Block Y / a lab," treat the relevant schedule
file as the source of truth for scope, topic list, ordering and timing — don't invent topics
it doesn't list, and keep new content inside the time budget implied by the block's duration.

## Where new topic content goes

Each session folder follows this layout (established in `session-01`; roll it out to the
other sessions as their content gets written):

```
session-01/
  schedule.md          agenda, timing, topics, labs, ground rules (source of truth for scope)
  intro.md             orientation: why the day matters, journey at a glance, before-you-start
  notes/
    01-how-are-AI-ML-DL-GenAI-LLM-prompts-connected.md
    02-....md
```

- **Notes** are numbered to match block order in `schedule.md`. They never contain code
  blocks. Explain ideas with stories, relatable everyday examples (phone autocomplete, spam
  email, site reports), tables and Mermaid diagrams. Notes are slide-style: one idea per
  block between `---` lines.
- **Keep notes concise.** Trim optional/repeating slides (myths, quick-check questions, extra
  recap slides) rather than including them by default — pad only if the user asks for more
  depth.
- **Do not add coding examples unless the user asks.** By default, teach with simple examples
  the reader can try without code: a local model (Ollama chat), or a website that lets them
  visualise the idea (tokenizer sites, Embedding Projector, Transformer Explainer). Put these
  in an "Explore It Yourself" slide.
- Only create files/folders when actually writing that content — don't scaffold empty ones.
- If the user does ask for code later, put it in `session-XX/code/<topic>/` and link to it from the note.

## Content format for a topic file

Each topic markdown file should read as a self-contained teaching unit and generally include,
in this order:

1. **Title + context** — one line linking it back to `DayN` / block name / lab name from the
   schedule.
2. **Concept overview** — short, simple, story-led prose explaining the idea, written for the mixed audience
   (assume Python but not ML background unless the day's schedule says otherwise).
3. **A Mermaid diagram** — a `flowchart` for a process/pipeline, `sequenceDiagram` for a
   request/response or multi-turn interaction, or `mindmap` for a concept map. Match the
   existing visual language (see Mermaid style below).
4. **Examples** — plain-language, relatable examples in the note itself (no code blocks). The
   matching runnable Python goes in `code/` and is linked from the note. Code uses only the
   toolchain named in the course doc (see Toolchain below).
5. **Walkthrough** — step through what the example does and why, tied to the concept above.
6. **Use case / when to reach for this** — a short, realistic scenario showing why this
   matters in practice. Keep it generic by default; only make it Kalpataru-specific
   (project reporting, procurement, contracts/tenders, site/service tickets — see Day 6's
   indicative use cases) when the user explicitly asks for a Kalpataru-relevant example.
7. **Lab tie-in**, if the schedule names a lab for this block — what the trainee should be able
   to do hands-on by the end.

Keep code examples honest about failure modes (rate limits, malformed JSON, auth errors) where
the topic is API-related — several blocks (Day 3 structured outputs, function calling) exist
specifically to teach handling those.

## Mermaid style

Reuse the palette and diagram types already established across the schedule files so new
content looks like it belongs to the same deck:

| Color | Hex | Used for |
|---|---|---|
| Purple | `#5B4A9E` | Stage 1 / primary |
| Blue | `#1F5F8B` | Stage 2 |
| Teal | `#0E9AA7` | Stage 3 |
| Orange | `#E8752A` | Highlight / critical / final build step |
| Navy | `#0F2C4C` | Hub node / final output |

All text on colored fills uses `color:#ffffff`. Typical patterns already in use:

```mermaid
flowchart LR
    A["Step one"] --> B["Step two"] --> C["Step three"]

    style A fill:#5B4A9E,color:#ffffff
    style B fill:#1F5F8B,color:#ffffff
    style C fill:#0E9AA7,color:#ffffff
```

- `mindmap` for "topics at a glance" summaries (one per day, optionally one per topic file).
- `gantt` for agendas/timing only — don't reuse it for anything else.
- `flowchart TB` with a hub node (see the FDE six-pillar diagram in the course overview) for
  capability/architecture models.
- Keep node labels short with `<br/>` line breaks rather than long single-line text.

## Toolchain (stay within this; it's what's whitelisted for the classroom)

- Python 3.10+, VS Code or Jupyter, Git
- LLM APIs: Gemini, OpenAI, Claude, or an approved enterprise endpoint — **free tier only**
- Open-weight models via hosted or local runtime: Llama, Mistral
- Vector DB (Day 4): FAISS, Chroma, pgvector, or a free equivalent
- Agent frameworks (Day 5, after fundamentals): LangGraph, CrewAI, or AutoGen
- Docker/containers/deployment are explicitly out of scope for this foundation program

## Ground rules that apply to every example you write

- **No markdown links (`[text](path)`) to other files or folders, anywhere in this repo.**
  This applies even within one generated set of files (a walkthrough's own index-to-step
  links, previous/next breadcrumbs, "matches ../file.py exactly" notes) — files and folders
  in this repo get moved and renamed often, and every link is a latent inconsistency when
  that happens. If content spans multiple files, order or reference them by name in prose
  ("see Step 2"), not by hyperlink. This overrides the default multi-file, cross-linked
  output shape of the app-walkthrough skill — use it for structure and content, not for its
  linking convention.
- No real API keys or secrets in any file — use `.env` + `.env.example` patterns, never commit
  actual keys.
- Only synthetic or sanitized data in examples and datasets — never real Kalpataru project,
  vendor, contract, or personnel data.
- Assume free-tier API limits; don't write examples that assume paid-tier throughput or quota.
- Match each day's "Not Covered Today" boundaries — e.g. don't pull agent frameworks into Day 3
  content, don't pull deployment/Docker into the foundation days.

## Editorial conventions carried over from existing files

- Files end with: `*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*`
- Headings use Title Case; body prose is plain and instructional, not marketing copy.
- Tables are used for schedules, deliverables, and comparisons — prefer a table over prose
  when listing more than 3 parallel items.
- No emojis.
