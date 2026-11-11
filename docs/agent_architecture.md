# AI Agent Architecture & Dynamic Tool Orchestration

## 1. Architectural Overview
The **Return or Regret AI** Agent Controller is a Python-based stateful coordinator that translates free-form customer shopping inquiries into structured, deterministic, and explainable shopping recommendations.

Unlike standard chatbots that hallucinate measurements or blend ungrounded text, the agent controller:
1. Classifies natural language intention into discrete task domains.
2. Extracts and sanitizes parameters (Product IDs, selected size, anatomical measurements).
3. Selects **only the necessary tools** required to fulfill the specific query.
4. Executes registered Python tools against verified catalog data and trained models.
5. Employs the **Decision Synthesis Engine** to reconcile physical ease vs cohort ML probabilities.
6. Returns a structured `AgentResponse` payload adhering to strict Pydantic schemas.

---

## 2. Registered Python Tool Registry

| Tool | File Location | Scope of Responsibility |
| :--- | :--- | :--- |
| `product_information_tool` | `tools/agent_tools.py` | Retrieves verified fabric composition, care guide, silhouette, and known fit quirks. Validates product ID. |
| `size_chart_tool` | `tools/agent_tools.py` | Extracts authentic garment dimensions (inches) across all published sizes. |
| `fit_calculator_tool` | `tools/agent_tools.py` | Computes ease tolerance ($\text{Garment} - \text{Body}$) using fit-type specific thresholds; verifies alternative size dimensions. |
| `return_risk_prediction_tool` | `tools/agent_tools.py` | Executes the serialized Scikit-Learn pipeline using pre-purchase features. |
| `return_history_analyzer_tool` | `tools/agent_tools.py` | Analyzes historical return rates, defect reason breakdown, and customer feedback quotes. |
| `rag_retrieval_tool` | `tools/agent_tools.py` | Performs TF-IDF cosine similarity search across markdown policies, sizing guides, and fabric care docs. |

---

## 3. Dynamic Tool Selection Rules

| Query Type / Intent | Example Query | Tools Executed | Reason for Tool Selection |
| :--- | :--- | :--- | :--- |
| `PRODUCT_SPECS_AND_CARE` | *"What material is P001 made of?"* | `product_information_tool` | Only catalog metadata needed. Fit/ML tools are irrelevant. |
| `SIZE_CHART_INQUIRY` | *"Show me the size chart for P003."* | `product_information_tool`, `size_chart_tool` | Product context + size chart table. |
| `RETURN_POLICY_INQUIRY` | *"What is the return policy for footwear?"* | `rag_retrieval_tool` | Policy document vector search. |
| `RETURN_HISTORY_INQUIRY` | *"Why do customers return P004?"* | `product_information_tool`, `return_history_analyzer_tool` | Product metadata + empirical return records. |
| `RETURN_RISK_INQUIRY` | *"What is the predicted probability of return for P005?"* | `product_information_tool`, `return_risk_prediction_tool`, `return_history_analyzer_tool` | ML model evaluation + historical context. |
| `FIT_RECOMMENDATION` | *"My chest is 40 inches. Will P001 Size M fit?"* | `product_information_tool`, `size_chart_tool`, `fit_calculator_tool`, `return_risk_prediction_tool`, `return_history_analyzer_tool`, `rag_retrieval_tool` | Full multi-pillar synthesis required. |
| `UNSUPPORTED_OR_IRRELEVANT` | *"Do you sell Rolex watches?"* | *None* | Fast rejection without wasting tool compute. |
| `INVALID_PRODUCT_ID` | *"Will size M fit for product P999?"* | `product_information_tool` | Validates ID, terminates with clarification prompt. |

---

## 4. Structured Response Contract (`AgentResponse`)

```json
{
  "intent": "FIT_RECOMMENDATION",
  "product_id": "P001",
  "product_name": "Heritage Oxford Slim Shirt",
  "selected_size": "M",
  "summary_message": "Personalised body ease calculation reveals active fit restriction in Size M...",
  "verdict": "High Fit Concern",
  "fit_assessment": {
    "verdict": "High Fit Concern",
    "confidence": 0.92,
    "fit_type": "Slim Fit",
    "tight_areas": ["Chest is severely constricted (+0.0\" ease vs recommended minimum 1.5\" for Slim Fit)"],
    "measurement_comparison": [
      {
        "dimension": "Chest",
        "body_measurement": 40.0,
        "garment_measurement": 40.0,
        "ease": 0.0,
        "interpretation": "Severely constricted (only 0.0\" ease; button pull/chafing)",
        "status": "tight"
      }
    ],
    "alternative_size_check": {
      "alternative_size": "L",
      "is_available_in_chart": true,
      "assessment_notes": "Size L measurements verified in catalog (Chest: 43.0\" (gives +3.0\" ease))..."
    }
  },
  "ml_prediction": {
    "predicted_return_probability": 0.118,
    "predicted_return_percentage": 11.8,
    "risk_tier": "Low",
    "model_name": "Logistic Regression (Balanced)"
  },
  "historical_analysis": {
    "total_orders_analyzed": 40,
    "overall_return_rate": 25.0,
    "top_return_reasons": [{"reason": "Shoulder / Armhole Tightness", "percentage": 50.0}]
  },
  "decision_synthesis": {
    "reconciled_verdict": "High Fit Concern",
    "reconciliation_explanation": "Physical ease deficit takes precedence over low ML probability...",
    "actionable_advice": "We strongly recommend checking Size L instead of Size M..."
  },
  "final_recommendation": "We strongly recommend checking Size L instead of Size M...",
  "evidence_sources": [...],
  "customer_explanation": {...},
  "tools_executed": ["product_information_tool", "size_chart_tool", "fit_calculator_tool", "return_risk_prediction_tool", "return_history_analyzer_tool", "rag_retrieval_tool"],
  "execution_metadata": {
    "latency_ms": 28.3,
    "execution_mode": "Deterministic Academic Engine"
  }
}
```
