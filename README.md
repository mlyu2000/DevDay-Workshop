# Building Secure Enterprise AI Agents with RAG, RBAC, and Workflow Automation

This repository contains the workshop notebooks and supporting materials for a technical developer workshop on building **enterprise AI agent solutions** using:

- **LLM application pipelines**
- **Retrieval-Augmented Generation (RAG)**
- **retrieval quality analysis**
- **RBAC-enforced document access control**
- **workflow automation patterns**
- **production-oriented observability**

The workshop is designed for developers who want to move beyond prompt demos and build systems that are:

- grounded in enterprise data,
- controlled by policy,
- observable in production,
- and capable of safe automation.

---

# Repository Purpose

This repo is intended to be reused by:

- workshop presenters
- technical facilitators
- internal enablement teams
- solution architects
- developers running hands-on sessions

It provides a notebook-based learning path that progresses from a basic LLM pipeline to a secure AI agent architecture.

---

# Workshop Learning Path

The workshop follows this sequence:

1. **Basic LLM pipeline**
2. **Enterprise RAG over private documents**
3. **Retrieval quality diagnostics with query logs**
4. **RBAC and document-level access control**
5. **Workflow automation and secure agent orchestration**

Each notebook builds on concepts introduced in the previous one.

---

# Repository Structure

Example structure:

```text
.
├── 01_lab1a_llm_basics.ipynb
├── 02_lab2a_build_document_agent.ipynb
├── 03_lab3a_analyze_query_logs.ipynb
├── 04_lab4a_rbac_enforced_rag.ipynb
├── 01_solution.ipynb
├── 02_solution.ipynb
├── 03_solution.ipynb
├── 04_solution.ipynb
├── data/
│   ├── workshop/
│   │   ├── docs/
│   │   ├── query_log.csv
│   │   ├── rbac_docs/
│   │   └── tokens/
├── scripts/
│   ├── generate_rbac_docs.py
│   └── ...
└── README.md
```

Actual file names may vary depending on the final repo layout.

---

# Notebook Overview

## Notebook 1 — LLM Basics
Introduces the foundation of an AI application:

- prompt templates
- model invocation
- output parsing
- sync / async / streaming execution
- observability with Langfuse

### Outcome
Participants build a reusable and traceable LLM chain.

---

## Notebook 2 — Build a Document Agent
Introduces RAG over enterprise documents:

- document loading
- chunking
- embeddings
- Qdrant indexing
- similarity retrieval
- grounded prompt construction

### Outcome
Participants build a document-aware assistant that answers from retrieved evidence.

---

## Notebook 3 — Analyze Query Log Dataset
Introduces retrieval diagnostics:

- score distribution analysis
- semantic query embeddings
- clustering with K-means
- visualization with UMAP
- identifying low-performing query clusters
- diagnosing content gaps

### Outcome
Participants learn how to analyze RAG quality using real query logs.

---

## Notebook 4 — Implement RBAC-Enforced RAG
Introduces secure retrieval and policy enforcement:

- ingesting documents with RBAC metadata
- defining role permission profiles
- decoding JWTs
- building Qdrant payload filters
- enforcing role-based retrieval boundaries
- validating audit logs

### Outcome
Participants build a secure RAG pipeline that enforces document-level access control.

---

# Intended Audience

This repository is built for **technical developers** with basic familiarity in:

- Python
- APIs
- JSON
- notebooks
- authentication concepts

Helpful but not required:

- LangChain
- vector databases
- JWTs
- observability tooling

---

# Presenter Guidance

If you are using this repository to run a workshop, read this section carefully.

## Before the workshop
Presenters should verify:

- notebook paths are correct
- endpoint URLs are valid
- API keys and tokens are current
- Qdrant is reachable
- Langfuse is reachable
- local/shared dataset paths exist
- all notebooks run from top to bottom in a clean kernel
- solution notebooks are available as fallback

## During the workshop
Recommended presentation flow:

1. Explain architecture before code
2. Run the configuration cells first
3. Emphasize the difference between:
   - model logic
   - retrieval logic
   - policy logic
4. Pause after each notebook to summarize:
   - what was built
   - what trust boundary was introduced
   - what production concern was added

## If participants get stuck
Suggested fallback strategy:

- use pre-run solution notebooks
- show expected output instead of troubleshooting deeply
- keep the conceptual flow moving
- return to environment/debug issues after the session if needed

---

# Security Notes

## Important
Some notebooks may contain inline workshop credentials or tokens for convenience during a controlled training session.

These should **not** be treated as production-safe patterns.

### Presenters should:
- rotate any temporary workshop credentials regularly
- avoid publishing real internal secrets
- remove or replace inline credentials when adapting this repo for broader use
- use environment variables or secret management for any long-term deployment

## Production guidance
In real systems:

- JWTs must be **signature-verified**
- RBAC must be enforced in the **application layer**
- vector store filters must be generated from trusted identity claims
- users must never be allowed to submit raw access filters directly
- audit logging should capture allow and deny decisions

---

# RBAC Design Principle

One of the core lessons of this workshop is:

> **Qdrant is not the RBAC engine.**

Qdrant only executes the payload filter it receives.

Security depends on the application layer correctly doing all of the following:

1. validate user identity
2. decode trusted claims
3. resolve permissions
4. generate an allowed filter
5. execute retrieval using that filter
6. log the result

If the application gets that wrong, the vector store will faithfully return the wrong data.

---

# Workflow and Agent Design Principle

Another core lesson of this repository is:

> **An enterprise AI agent is not just a prompt wrapped around an LLM.**

A production-capable agent requires:

- data retrieval
- policy enforcement
- workflow routing
- tool orchestration
- logging and traceability
- safe refusal behavior

This repo teaches those pieces incrementally.

---

# Environment Expectations

The notebooks assume access to a workshop environment that may include:

- HPE Private Cloud AI hosted model endpoints
- OpenAI-compatible LLM APIs
- OpenAI-compatible embedding APIs
- Qdrant
- Langfuse
- shared workshop data directories

Because these resources may differ by event or presenter, expect to update:

- endpoint URLs
- API keys
- hostnames
- filesystem paths

before running the workshop.

---

# Recommended Python Packages

Exact requirements depend on notebook versions, but commonly used packages include:

- `langchain`
- `langchain-openai`
- `langchain-qdrant`
- `langchain-community`
- `langchain-text-splitters`
- `openai`
- `qdrant-client`
- `langfuse`
- `httpx`
- `pandas`
- `numpy`
- `matplotlib`
- `umap-learn`
- `scikit-learn`

If you maintain this repo long term, it is strongly recommended to add a pinned `requirements.txt` or `environment.yml`.

---

# Suggested Additions for Maintainers

To improve reusability across presenters, consider adding:

- `requirements.txt`
- `environment.yml`
- `slides/` directory
- sample architecture diagrams
- pre-generated workshop datasets
- presenter notes
- troubleshooting guide
- setup validation script

---

# Troubleshooting Tips

## Common issues

### 1. Qdrant connection fails
Check:
- hostname
- port
- HTTPS setting
- firewall / tunnel availability
- collection name

### 2. Embedding dimension mismatch
Check:
- configured `EMBED_DIM`
- actual deployed embedding model dimension
- collection schema

### 3. Langfuse auth check fails
Check:
- host URL
- public/secret key pair
- service reachability

### 4. JWT decode or RBAC behavior seems wrong
Check:
- token file contents
- role claim names
- permission matrix
- payload field names in Qdrant

### 5. Retrieval returns empty results unexpectedly
Check:
- ingestion count
- metadata field names
- filter structure
- whether the role should actually have access

---

# Teaching Tips

Useful messages to reinforce during the workshop:

- **Notebook 1:** “A chain is the smallest useful LLM application unit.”
- **Notebook 2:** “RAG separates memory from evidence.”
- **Notebook 3:** “You diagnose retrieval by looking at populations, not anecdotes.”
- **Notebook 4:** “Security lives in the app layer, not in the vector DB.”

---

# License / Usage

Add your organization’s preferred license or internal usage note here.

Example placeholder:

```text
© Your Organization. Internal workshop use unless otherwise specified.
```

or

```text
Licensed under the MIT License.
```

---

# Contact / Ownership

Add workshop owner or maintainer details here.

Example:

- Workshop maintainer: `team@example.com`
- Platform contact: `platform@example.com`

---

# Final Takeaway

If participants complete the notebook sequence successfully, they should understand how to build an AI application that is:

- grounded in enterprise documents,
- measured through log-based diagnostics,
- protected by RBAC,
- and extensible toward workflow automation and agent orchestration.

That is the real through-line of this repository.

## In one sentence

**This repo teaches how to go from prompt-based prototypes to secure enterprise AI agent systems.**
```

## Recommended next repo additions
For long-term presenter reuse, I strongly recommend adding these files next:

- `requirements.txt`
- `PRESENTER_GUIDE.md`
- `TROUBLESHOOTING.md`
- `WORKSHOP_AGENDA.md`
- `slides/` or `deck/`
