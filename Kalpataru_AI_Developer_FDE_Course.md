# AI Developer & FDE Training

**Kalpataru Projects | Onsite, Ahmedabad**
Delivered by ADaSci, An AIM Initiative

6 days | 4 hours per day | 3 days per week for 2 weeks | Two batches daily (forenoon and afternoon)

---

## Course at a Glance

```mermaid
flowchart LR
    subgraph W1["WEEK 1"]
        direction LR
        D1["Day 1<br/>AI Developer<br/>Foundations"] --> D2["Day 2<br/>Microsoft Copilot<br/>Hands-on"] --> D3["Day 3<br/>Python +<br/>LLM APIs"]
    end
    subgraph W2["WEEK 2"]
        direction LR
        D4["Day 4<br/>RAG + Vector<br/>Databases"] --> D5["Day 5<br/>AI Agents +<br/>FDE Architecture"] --> D6["Day 6<br/>Industry Use Case<br/>+ Assessment"]
    end
    D3 --> D4

    style D1 fill:#5B4A9E,color:#ffffff
    style D2 fill:#1F5F8B,color:#ffffff
    style D3 fill:#0E9AA7,color:#ffffff
    style D4 fill:#5B4A9E,color:#ffffff
    style D5 fill:#1F5F8B,color:#ffffff
    style D6 fill:#E8752A,color:#ffffff
```

| Day | Module | Hands-on output |
|:---:|---|---|
| 1 | Foundations | Prompt patterns + API/environment setup |
| 2 | Microsoft Copilot | Business workflow exercises |
| 3 | Python + LLM APIs | LLM-powered utility app |
| 4 | RAG + Vector DBs | Document knowledge assistant |
| 5 | AI Agents + FDE | Agentic workflow blueprint |
| 6 | Industry Use Case | Caselet demo |

---

## Who Attends What

```mermaid
flowchart TB
    subgraph DEV["Developers"]
        A1["Application developers and packaged software teams"]
        A2["AI, data and full-stack engineers"]
        A3["SAP consultants"]
        A4["PoC, integration and deployment teams"]
    end
    subgraph BIZ["Business engagement and support teams"]
        B1["Foundation module"]
        B2["Microsoft Copilot module"]
    end
    DEV --> ALL["Days 1 to 6<br/>Full AI Developer and FDE program"]
    BIZ --> PART["Relevant foundation and Copilot modules"]

    style ALL fill:#0E9AA7,color:#ffffff
    style PART fill:#1F5F8B,color:#ffffff
```

- Developers: Python basics, APIs, JSON, SQL and Git recommended
- Business teams: comfortable with Word, Excel, PowerPoint, Outlook and Teams; no coding needed
- The Copilot module is de-coupled from FDE in terms of learning outcomes

---

## How We Learn: LAR

```mermaid
flowchart LR
    L["LEARN<br/>Concepts and<br/>implementation patterns"] --> A["APPLY<br/>Hands-on labs and<br/>use-case practice"] --> R["REFLECT<br/>Assessments and<br/>architecture readout"]

    style L fill:#5B4A9E,color:#ffffff
    style A fill:#1F5F8B,color:#ffffff
    style R fill:#0E9AA7,color:#ffffff
```

## What You Will Gain

- Developers: AI, RAG and agentic solution capability
- Business teams: practical Copilot skills for daily workflows
- Everyone: hands-on, immersive coverage with an exit caselet

---

# Week 1

---

## Day 1: AI Developer Foundations

**Output: Prompt patterns + API/environment setup**

```mermaid
mindmap
  root((Day 1))
    GenAI and LLMs
    Prompt Engineering
    Python for AI
    LLM APIs
    Foundation Map
```

1. GenAI and LLM fundamentals: tokens, context window, temperature, hallucination, closed and open-weight models
2. Prompt engineering: prompt anatomy, few-shot, step-by-step reasoning, structured output, prompt risks
3. Python for AI: Python 3.10+, virtual environments, JSON, API keys and `.env`, error handling
4. LLM APIs overview: anatomy of a call, responses, token usage, rate limits, providers
5. Foundation map: preview of RAG, vector databases and agents

Labs: Prompt Patterns, Environment Setup, First API Calls

---

## Day 2: Microsoft Copilot Hands-on

**Output: Business workflow exercises**

```mermaid
mindmap
  root((Copilot))
    Word
    Excel
    PowerPoint
    Outlook
    Teams
    Reporting
```

| Tool | Focus |
|---|---|
| Word | Draft and refine documents |
| Excel | Analyse tables and explain trends |
| PowerPoint | Create executive summaries |
| Outlook | Draft replies and follow-ups |
| Teams | Meeting summaries and action items |
| Reporting | Management briefs and weekly reports |

- Practical AI skills for daily business operations
- Responsible use with business documents, email and meetings
- Faster, clearer reporting without writing code
- Requires an eligible Microsoft 365 licence and assigned Copilot licence per participant

---

## Day 3: Python + LLM APIs

**Output: LLM-powered utility app**

```mermaid
flowchart LR
    A["API calls"] --> B["Authentication"] --> C["JSON"] --> D["Structured outputs"] --> E["Function calling"] --> F["Integration"]

    style A fill:#5B4A9E,color:#ffffff
    style B fill:#1F5F8B,color:#ffffff
    style C fill:#0E9AA7,color:#ffffff
    style D fill:#5B4A9E,color:#ffffff
    style E fill:#1F5F8B,color:#ffffff
    style F fill:#E8752A,color:#ffffff
```

1. Python for AI in practice
2. API calls and authentication
3. Working with JSON
4. Structured outputs
5. Function calling
6. Integrating LLM calls into an application

---

# Week 2

---

## Day 4: RAG + Vector Databases

**Output: Document knowledge assistant**

```mermaid
flowchart LR
    A["Ingestion"] --> B["Chunking"] --> C["Embeddings"] --> D["Vector store"] --> E["Retrieval"] --> F["Answer with citations"]

    style A fill:#5B4A9E,color:#ffffff
    style B fill:#1F5F8B,color:#ffffff
    style C fill:#0E9AA7,color:#ffffff
    style D fill:#5B4A9E,color:#ffffff
    style E fill:#1F5F8B,color:#ffffff
    style F fill:#E8752A,color:#ffffff
```

1. Why RAG: grounding models in your own documents
2. Ingestion and chunking
3. Embeddings
4. Vector stores: FAISS, Chroma, pgvector or a free equivalent
5. Retrieval
6. Citations

---

## Day 5: AI Agents + FDE Architecture

**Output: Agentic workflow blueprint**

```mermaid
flowchart LR
    A["Tools"] --> B["Agent workflows"] --> C["Guardrails"] --> D["Approvals"] --> E["FDE pillars"]

    style A fill:#5B4A9E,color:#ffffff
    style B fill:#1F5F8B,color:#ffffff
    style C fill:#0E9AA7,color:#ffffff
    style D fill:#E8752A,color:#ffffff
    style E fill:#0F2C4C,color:#ffffff
```

1. Agent fundamentals and workflows
2. Tools
3. Guardrails and approvals
4. Agent frameworks (LangGraph, CrewAI, AutoGen), introduced after agent fundamentals
5. The FDE six-pillar view

### FDE Six-Pillar Capability Model

```mermaid
flowchart TB
    P1["1. Technical Solution<br/>Leadership"]
    P2["2. Enterprise Integration<br/>and APIs"]
    P3["3. Agentic AI, RAG<br/>and Tools"]
    HUB(("FDE<br/>Operating<br/>Motion"))
    P4["4. Production DevOps<br/>and Observability"]
    P5["5. Security, Compliance<br/>and Reliability"]
    P6["6. Customer Caselets<br/>and Storytelling"]

    P1 --- HUB
    P2 --- HUB
    P3 --- HUB
    HUB --- P4
    HUB --- P5
    HUB --- P6

    style HUB fill:#0F2C4C,color:#ffffff
```

---

## Day 6: Industry Use Case + Assessment

**Output: Caselet demo**

```mermaid
flowchart LR
    DI["<b>Discover</b><br/>Business workflow<br/>and requirements"] --> BU["<b>Build</b><br/>Python, APIs, RAG<br/>and agent workflow"]
    BU --> CO["<b>Control</b><br/>Guardrails, approvals<br/>and evaluation"]
    CO --> PR["<b>Present</b><br/>Demo, architecture<br/>and ROI narrative"]

    style DI fill:#5B4A9E,color:#ffffff
    style BU fill:#1F5F8B,color:#ffffff
    style CO fill:#0E9AA7,color:#ffffff
    style PR fill:#E8752A,color:#ffffff
```

Indicative use-case scenarios:

- Project status and management reporting assistant
- Procurement / vendor comparison and exception workflow
- Contract, tender or policy document knowledge assistant
- Site issue / service ticket classification and escalation

Assessment components:

- Hands-on practice checks during labs
- Capstone solution readout with architecture, risks and next steps
- Completion certificate from ADaSci

---

## What Moves Out of Foundation

- Docker, containers and deployment remain in the production / DevOps section
- LangGraph, CrewAI and AutoGen are introduced after agent fundamentals

---

## Tools and Readiness

| Developer toolchain | Classroom readiness |
|---|---|
| Python 3.10+, VS Code / Jupyter, Git | Laptop for each participant |
| LLM APIs: Gemini, OpenAI, Claude or approved enterprise endpoint (free tier only) | Stable internet and projector/display |
| Open-weight models: Llama, Mistral via hosted or local runtime | Package repositories and API endpoints whitelisted |
| Agent framework: LangGraph, CrewAI or AutoGen as selected | API keys issued or training sandbox provisioned |
| Vector DB: FAISS, Chroma, pgvector or free equivalent | Synthetic or sanitized datasets only, or ADaSci-provided dataset |

The final toolchain is validated before kickoff based on customer approvals, endpoint availability and IT whitelisting.

---

## About ADaSci

AIM Media House is one of India's trusted voices in AI, data science, analytics and emerging technologies. ADaSci brings enterprise learning, community engagement, hackathons, events and thought leadership to activate AI adoption at scale.

**Enterprise AI capability building through Learn, Apply, Reflect**

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
