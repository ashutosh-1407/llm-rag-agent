# LLM-Powered Document Assistant (RAG + Tool Calling + Evaluation)

## Overview

This project is a production-style LLM document assistant built without LangChain.

It answers user questions over document content using:

* Retrieval-Augmented Generation (RAG)
* OpenAI function/tool calling
* lightweight session memory
* structured logging and service metrics
* offline evaluation pipeline

The goal is to combine strong retrieval accuracy with modular backend design suitable for production environments.

---

## Problem Statement

Large language models can generate fluent answers, but they:

* hallucinate when facts are missing
* do not know private document content
* cannot reliably execute actions without explicit tool interfaces

This system addresses that by combining:

* semantic retrieval for grounding
* tool calling for explicit actions
* an agent layer for routing decisions

---

## Architecture

```text
User Query
   ↓
FastAPI API Layer
   ↓
Agent (Decision Layer)
 ┌───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓
RAG Retrieval    Tools           Direct LLM
 ↓               ↓               ↓
Context        Function Call    Response
 └───────────────┴───────────────┘
         ↓
Final Answer
```

---

## Core Components

### Retrieval Layer

* document ingestion from PDF
* chunking with overlap
* embeddings
* FAISS similarity search
* top-k retrieval

### Agent Layer

The agent decides whether to:

* answer directly
* use retrieved context
* call a tool

### Tools

Implemented tools include:

* summarize_doc
* get_support_info

### Memory

Conversation history is stored per session (in-memory) and injected into prompts.

### Observability

The service includes:

* structured request logging
* latency measurement
* route tracking
* health endpoint
* metrics endpoint

---

## Project Structure

```text
llm-rag-agent/
├── backend/
│   ├── data/
│   ├── evaluation/
│   │   ├── dataset.json
│   │   └── evaluator.py
│   ├── scripts/
│   │   └── run_eval.py
│   ├── src/
│   │   ├── agent/
│   │   │   └── agent.py
│   │   ├── llm/
│   │   │   └── generator.py
│   │   ├── memory/
│   │   │   └── memory_store.py
│   │   ├── observability/
│   │   │   ├── logger.py
│   │   │   ├── metrics_db.py
│   │   │   └── metrics_service.py
│   │   ├── rag/
│   │   │   ├── chunker.py
│   │   │   ├── embedder.py
│   │   │   ├── loader.py
│   │   │   ├── retriever.py
│   │   │   └── retriever_store.py
│   │   ├── tools/
│   │   │   ├── registry.py
│   │   │   └── tools.py
│   │   ├── utils/
│   │   │   ├── constants.py
│   │   │   └── helper.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── ui/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── streamlit_app.py
├── docker-compose.yaml
├── README.md
└── render.yaml
```

---

## Evaluation Results

Evaluation was performed on a 15-question benchmark covering:

* direct retrieval
* paraphrased retrieval
* multi-part reasoning
* exception handling

### Results

* Retrieval Hit@5: 93.33%
* Exact Match: 20.00%
* Avg Keyword Coverage: 93.33%

### Interpretation

Retrieval quality is strong, with correct supporting chunks retrieved in most cases.

Exact match remains low because the model frequently paraphrases semantically correct answers.

Keyword coverage confirms answer quality remains high.

---

## Example Queries

### Retrieval Example

Q: Can I return electronics?

A: Electronics such as laptops and phones are non-refundable.

### Tool Example

Q: Summarize the document

A: The document covers refunds, shipping, support, discounts, and account policies.

### Multi-part Example

Q: I need support and also want to know when they reply.

A: Customers can contact support via email or phone, and support aims to respond within 24 hours.

---

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run server:

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Docker:

Make sure to create a .env in the root folder
```text
docker build -t llm-rag-agent .
docker run --env-file .env -p 10000:10000 llm-rag-agent
```

---

## Tradeoffs

### Current choices

* in-memory session store for simplicity
* lightweight reranking heuristic
* local FAISS retrieval

### Future improvements

* Redis-backed memory
* stronger reranker
* Docker slimming for cloud deployment
* Prometheus/Grafana monitoring

---

## Key Learnings

This project demonstrates how to design an LLM system beyond a simple chatbot by separating:

* decision logic
* retrieval
* tool execution
* observability
* evaluation

---

## Tech Stack

* Python
* FastAPI
* OpenAI API
* FAISS
* NumPy

---
