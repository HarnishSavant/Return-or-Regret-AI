# RAG Retrieval Engine Validation & Grounding Audit

## 1. Knowledge Base Corpus
The RAG engine indexes 35 semantic chunks extracted from 4 core markdown documents:
1. `backend/knowledge_base/return_policy.md` (30-day window, free size exchanges, no penalty guarantee, footwear & hygiene rules)
2. `backend/knowledge_base/sizing_and_measurement_guide.md` (How to measure, ease tolerance rules across fit types)
3. `backend/knowledge_base/materials_and_fabric_care.md` (Natural fibers, cotton shrinkage prevention, lycra compression, linen rigidity)
4. `backend/knowledge_base/product_catalog_and_fit_notes.md` (Verified fit notes for all 18 styles P001 - P018)

---

## 2. Ingestion & Retrieval Pipeline
- **Chunking Strategy:** Header-aware markdown splitting (`#`, `##`, `###`).
- **Vector Index:** TF-IDF with sublinear term-frequency scaling and cosine similarity scoring.
- **Minimum Similarity Gate:** Similarity scores below 0.05 are filtered out to prevent irrelevant chunk retrieval.

---

## 3. Retrieval Quality & Citation Tracking
Every grounded answer produced by `rag_retrieval_tool` returns:
- `title`: Header of the specific markdown section.
- `document`: File origin (e.g. `return_policy.md`).
- `confidence`: Semantic similarity percentage.
- `snippet`: Verifiable excerpt from the original document.

### Unsupported Query Handling:
When a query asks about unindexed topics (e.g. "Do you sell Rolex watches?" or "What is the capital of France?"), the intent classifier catches it as `UNSUPPORTED_OR_IRRELEVANT` without making false vector matches or fabricating citations.
