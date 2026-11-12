# AI Agent Architecture & Dynamic Tool Orchestration (Phase 1.2)

## 1. Architectural Overview
The **Return or Regret AI** Agent Controller is a Python-based stateful coordinator that translates free-form customer shopping inquiries into structured, deterministic, and explainable shopping recommendations.

The architecture decouples intent classification and entity extraction into a dedicated module (`backend/agent/intent_classifier.py`), enforces **nine standardized canonical intents**, performs dynamic tool selection to eliminate unnecessary compute, and synthesizes multi-pillar evidence through the **Decision Synthesis Engine**.

---

## 2. Standardized Canonical Intent Taxonomy

Phase 1.2 establishes exactly 9 canonical intents via the `AgentIntent` enum in `schemas/agent_schemas.py`:

| Canonical Intent | Description | Standard Tools Selected |
| :--- | :--- | :--- |
| `PRODUCT_INFORMATION` | Fabric composition, care instructions, price, silhouette | `product_information_tool` (+ `rag_retrieval_tool` for wash/shrinkage) |
| `SIZE_INFORMATION` | Garment dimensions, sizing charts, measurements | `product_information_tool`, `size_chart_tool` |
| `FIT_RECOMMENDATION` | Personal fit evaluation based on body ease | `product_information_tool`, `size_chart_tool`, `fit_calculator_tool` (if measurements present) |
| `RETURN_RISK_PREDICTION` | ML cohort return probability & risk tier | `product_information_tool`, `return_risk_prediction_tool`, `return_history_analyzer_tool` |
| `RETURN_HISTORY_ANALYSIS` | Historical return rates, defect clusters, quotes | `product_information_tool`, `return_history_analyzer_tool` |
| `RETURN_POLICY` | Return window, exchange terms, refunds | `rag_retrieval_tool` |
| `PURCHASE_DECISION` | End-to-end purchasing recommendation | `product_information_tool`, `size_chart_tool`, `fit_calculator_tool` (if meas), `return_risk_prediction_tool`, `return_history_analyzer_tool`, `rag_retrieval_tool` |
| `GENERAL_PRODUCT_QUESTION` | Overview, features, brand consultation | `product_information_tool`, `rag_retrieval_tool` |
| `UNKNOWN_INTENT` | Out-of-domain queries or unlisted product IDs | *Zero tools* (or `product_information_tool` for ID validation) |

---

## 3. Dedicated Intent Classifier Module (`backend/agent/intent_classifier.py`)

The classifier operates independently and deterministically without hard-coding answers:
1. **Keyword Cluster Scoring:** Weighted regex pattern scoring across all 9 intent clusters.
2. **Disambiguation Rules:** Priority hierarchy resolving overlaps (e.g., body measurements + fit question routes to `FIT_RECOMMENDATION`; "should I buy" routes to `PURCHASE_DECISION`; explicit "dimensions of size M" routes to `SIZE_INFORMATION`).
3. **Structured Entity Extraction:**
   - `product_id`: Extracted via regex `(P\d{3,4})`, context, or catalog keyword matching; validated against catalog.
   - `requested_size`: Letter (`XS`-`XXL`) or numeric waist (`28`-`42`), with safeguards preventing non-sizes (e.g., "chart", "guide", "dimensions") from being misidentified.
   - `measurements`: Extracted for chest, waist, shoulder, hip, inseam, with auto-conversion from cm to inches ($> 60\text{ cm} \rightarrow \div 2.54$) and plausibility filtering.
   - `missing_required_information`: Flags missing chest/waist/shoulder requirements dynamically.

---

## 4. Registered Python Tool Registry

| Tool | File Location | Scope of Responsibility |
| :--- | :--- | :--- |
| `product_information_tool` | `tools/agent_tools.py` | Retrieves verified fabric composition, care guide, silhouette, and known fit quirks. Validates product ID. |
| `size_chart_tool` | `tools/agent_tools.py` | Extracts authentic garment dimensions (inches) across all published sizes. |
| `fit_calculator_tool` | `tools/agent_tools.py` | Computes ease tolerance ($\text{Garment} - \text{Body}$) using fit-type specific thresholds; verifies alternative size dimensions in catalog. |
| `return_risk_prediction_tool` | `tools/agent_tools.py` | Executes the serialized Scikit-Learn pipeline using pre-purchase features. |
| `return_history_analyzer_tool` | `tools/agent_tools.py` | Analyzes historical return rates, defect reason breakdown, and customer feedback quotes. |
| `rag_retrieval_tool` | `tools/agent_tools.py` | Performs TF-IDF cosine similarity search across markdown policies, sizing guides, and fabric care docs. |

---

## 5. Structured Response Schema (`AgentResponse`)

```json
{
  "intent": "SIZE_INFORMATION",
  "product_id": "P001",
  "product_name": "Heritage Oxford Slim Shirt",
  "selected_size": "M",
  "summary_message": "Size chart retrieved for Heritage Oxford Slim Shirt (Slim Fit).",
  "verdict": null,
  "fit_assessment": null,
  "measurement_comparison": null,
  "ml_prediction": null,
  "historical_analysis": null,
  "decision_synthesis": null,
  "final_recommendation": "Review the dimensions for Size M in the table above...",
  "evidence_sources": [],
  "missing_information": [],
  "customer_explanation": {
    "methodology_summary": "This evaluation is based on verified catalog specifications...",
    "data_sources_used": ["Official Garment Size Chart"],
    "limitations_notice": "Garment measurements reflect manufacturer specifications with standard ±0.5 inch tailoring tolerance."
  },
  "tools_executed": ["product_information_tool", "size_chart_tool"],
  "execution_metadata": {
    "latency_ms": 12.0,
    "execution_mode": "Deterministic Academic Engine"
  }
}
```

---

## 6. Evaluation Verification

The architecture is continuously validated by two automated test suites:
1. `backend/evaluation/test_scenarios.py`: **20/20 Passed (100.0%)**
2. `backend/evaluation/test_phase1_agent.py`: **32/32 Passed (100.0%)**
