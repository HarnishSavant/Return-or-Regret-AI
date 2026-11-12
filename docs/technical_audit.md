# Technical Audit & Architecture Review

## 1. Executive Summary
**Project:** Return or Regret AI — Intelligent Shopping Decision Agent  
**Audit Purpose:** Comprehensive architectural inspection, identification of logical contradictions between multi-source risk indicators, dynamic tool routing evaluation, and removal of internal developer traces from customer-facing interfaces.

---

## 2. Existing Codebase Strengths
1. **Pristine Modular Architecture:** Clean separation of concerns between backend orchestration (`agent/controller.py`), explicit registered tools (`tools/agent_tools.py`), ML pipeline (`ml/train_models.py`), and knowledge base retrieval (`rag/retriever.py`).
2. **True Full-Stack Implementation:** Real FastAPI REST API communicating seamlessly with a React 19 + TypeScript frontend; no decorative mockups.
3. **Rigorous Pre-Purchase Feature Separation:** Zero target leakage in dataset generation and model training. Only pre-purchase signals (category, fit type, price, discount, bracketing, completeness) are utilized.
4. **Strong Aesthetic Baseline:** Premium SaaS styling adhering to Linear/Stripe design language (Slate Navy `#0f172a`, Warm Off-White `#f8fafc`, Coral Orange `#f97316`).

---

## 3. Identified Deficiencies & Resolved Inconsistencies

### A. The Contradictory Risk Signals Dilemma (RESOLVED)
- **Previous Defect:** For the query *"I usually wear size M and my chest measurement is 40 inches. Will P001 fit me?"*, the system simultaneously displayed:
  - Personal Fit Calculator: *High Return Risk* (0.0" chest ease)
  - ML Return Prediction: *11.8% Low Return Probability*
  - Historical Intelligence: *25% Historical Return Rate*
- **Root Cause:** Treating distinct risk metrics as interchangeable. The ML model predicts broad cohort baseline probability based on pre-purchase catalog metadata (category, price, discount), whereas personal fit calculation measures physical anatomical compatibility.
- **Resolution:** Engineered a dedicated **Decision Synthesis Engine** (`backend/agent/decision_engine.py`). It enforces the ground-truth principle: **Physical measurement incompatibility strictly supersedes population-level ML probabilities.** It explicitly explains *why* the ML model shows low general risk while the customer's personal body measurements show an acute ease deficit, and corroborates this with historical returns where 50% of returns cite shoulder/armhole tightness.

### B. Unchecked Alternative Size Recommendations (RESOLVED)
- **Previous Defect:** When Size M was restrictive, the system advised sizing up to Size L without verifying whether Size L dimensions existed or whether Size L actually resolved the restriction.
- **Resolution:** Upgraded `fit_calculator_tool` to perform **Alternative Size Verification**. It retrieves Size L dimensions directly from the catalog (`chart["L"]`), computes alternative ease tolerances, and confirms that Size L provides +3.0" ease before recommending it. If alternative dimensions do not exist, it explicitly alerts the customer.

### C. Static / Indiscriminate Tool Execution (RESOLVED)
- **Previous Defect:** Every inquiry executed up to 6 tools regardless of intent (e.g., asking for fabric material executed the size chart, fit calculator, and ML prediction).
- **Resolution:** Implemented dynamic intent-driven tool selection:
  - `PRODUCT_SPECS_AND_CARE` -> executes `product_information_tool` (+ RAG for fabric care).
  - `SIZE_CHART_INQUIRY` -> executes `size_chart_tool` + `product_information_tool`.
  - `RETURN_POLICY_INQUIRY` -> executes `rag_retrieval_tool`.
  - `RETURN_HISTORY_INQUIRY` -> executes `return_history_analyzer_tool`.
  - `RETURN_RISK_INQUIRY` -> executes `return_risk_prediction_tool`.
  - `FIT_RECOMMENDATION` -> executes multi-tool workflow and runs Decision Synthesis.

### D. Exposed Developer Python Logs in Customer UI (RESOLVED)
- **Previous Defect:** Customer chat displayed raw JSON outputs, code snippets, and Python function names in an accordion.
- **Resolution:** Completely stripped raw Python execution panels from customer view. Replaced with a **Structured Customer Recommendation Card** featuring a prominent verdict badge (`Good Fit`, `Fit Concern`, `High Fit Concern`, `Insufficient Information`), measurement ease comparison table, ML cohort risk card, historical defect notes, and an expandable non-technical explanation.

### E. Intent Standardization & Dimensions Keyword Miss (RESOLVED — Phase 1.2)
- **Previous Defect:** Non-standard intent names (`PRODUCT_SPECS_AND_CARE`, `SIZE_CHART_INQUIRY`, etc.) were used inconsistently. Inline classification in `controller.py` missed queries like *"What are the dimensions of size M for P001?"* due to missing "dimensions" root keyword, causing fallback to general consultation and firing 5 unnecessary tools.
- **Resolution:**
  - Created dedicated `backend/agent/intent_classifier.py` implementing score-based ranking and priority disambiguation.
  - Standardized exactly **9 canonical intents** (`PRODUCT_INFORMATION`, `SIZE_INFORMATION`, `FIT_RECOMMENDATION`, `RETURN_RISK_PREDICTION`, `RETURN_HISTORY_ANALYSIS`, `RETURN_POLICY`, `PURCHASE_DECISION`, `GENERAL_PRODUCT_QUESTION`, `UNKNOWN_INTENT`).
  - Added `ExtractedEntities` and `IntentClassificationResult` schemas with unit and measurement range validation.
  - Fixed dimensions keyword patterns: *"What are the dimensions of size M for P001?"* correctly classifies as `SIZE_INFORMATION` and selects **only** `product_information_tool` and `size_chart_tool`.
  - Added regression test suites: `test_scenarios.py` (20/20 passed) and `test_phase1_agent.py` (32/32 passed, 100%).

---

## 4. Modified & Created Files Summary

| File Path | Action | Description |
| :--- | :--- | :--- |
| `backend/schemas/agent_schemas.py` | **Enhanced** | Canonical `AgentIntent` enum (9 intents), `ExtractedEntities`, `IntentClassificationResult`, and response models. |
| `backend/agent/intent_classifier.py` | **Created** | Dedicated, testable intent classification and entity extraction module. |
| `backend/agent/decision_engine.py` | **Created** | Evidence reconciliation engine balancing physical ease, ML risk, and defect records. |
| `backend/tools/agent_tools.py` | **Enhanced** | Fit-type tolerances, metric unit conversion, verified alternative size inspection. |
| `backend/agent/controller.py` | **Enhanced** | Integrates `IntentClassifier`, enforces strict dynamic tool selection, logs telemetry. |
| `backend/evaluation/test_scenarios.py` | **Enhanced** | 20 automated regression scenarios updated with canonical intents (20/20 passed, 100%). |
| `backend/evaluation/test_phase1_agent.py` | **Created** | 32 comprehensive intent & entity extraction test cases (32/32 passed, 100%). |
| `frontend/public/images/products/*.jpg` | **Created** | All 18 product images downloaded locally to prevent CDN 404/network blocks. |
| `frontend/src/types/index.ts` | **Enhanced** | Matching TypeScript interfaces for structured responses. |
| `frontend/src/components/RecommendationCard.tsx` | **Created** | Customer-facing recommendation UI (verdict badge, ease table, ML card, explanation). |
| `frontend/src/pages/AssistantPage.tsx` | **Enhanced** | Clean chat stream with structured widgets; raw Python logs removed. |

