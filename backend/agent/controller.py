"""
AI Agent Controller — Phase 1.2
================================
Orchestrates intent classification → dynamic tool selection →
structured response synthesis → telemetry logging.

Uses the dedicated IntentClassifier module and standardized AgentIntent enum.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from tools.agent_tools import (
    AVAILABLE_TOOLS,
    product_information_tool,
    size_chart_tool,
    fit_calculator_tool,
    return_risk_prediction_tool,
    return_history_analyzer_tool,
    rag_retrieval_tool,
    PRODUCTS_CACHE,
)
from schemas.agent_schemas import (
    AgentIntent,
    AgentResponse,
    FitVerdict,
    FitAssessment,
    MeasurementComparisonItem,
    AlternativeSizeEvaluation,
    MLPredictionOutput,
    HistoricalIntelligence,
    DecisionSynthesis,
    EvidenceSource,
    CustomerExplanation,
)
from agent.intent_classifier import IntentClassifier
from agent.decision_engine import DecisionSynthesisEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MONITORING_LOG_PATH = os.path.join(DATA_DIR, "monitoring_logs.json")


def append_monitoring_log(log_entry: Dict[str, Any]):
    logs = []
    if os.path.exists(MONITORING_LOG_PATH):
        try:
            with open(MONITORING_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.insert(0, log_entry)
    logs = logs[:500]
    with open(MONITORING_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


class AIAgentController:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.intent_classifier = IntentClassifier(PRODUCTS_CACHE)

    def process_query(
        self,
        query: str,
        context_product_id: Optional[str] = None,
        context_measurements: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        # ── 1. INTENT CLASSIFICATION & ENTITY EXTRACTION ──
        classification = self.intent_classifier.classify(
            query=query,
            context_product_id=context_product_id,
            context_measurements=context_measurements,
        )
        intent = classification.intent
        entities = classification.extracted_entities

        pid = entities.product_id
        is_invalid_pid = entities.is_invalid_product_id
        size = entities.requested_size or "M"

        # Build customer_measurements dict for downstream tools
        cust_meas: Dict[str, float] = {}
        if entities.chest_measurement is not None:
            cust_meas["chest"] = entities.chest_measurement
        if entities.waist_measurement is not None:
            cust_meas["waist"] = entities.waist_measurement
        if entities.shoulder_measurement is not None:
            cust_meas["shoulder"] = entities.shoulder_measurement
        if entities.hip_measurement is not None:
            cust_meas["hip"] = entities.hip_measurement
        if entities.inseam_measurement is not None:
            cust_meas["inseam"] = entities.inseam_measurement

        # ── INVALID PRODUCT ID ──
        if is_invalid_pid:
            latency_ms = round((time.time() - start_time) * 1000, 1)
            resp = AgentResponse(
                intent=AgentIntent.UNKNOWN_INTENT.value,
                product_id=pid,
                summary_message=f"Product ID '{pid}' is not found in our verified catalog.",
                final_recommendation=(
                    f"We could not locate product '{pid}'. "
                    f"Available catalog IDs are: {', '.join(sorted(PRODUCTS_CACHE.keys())[:6])}..."
                ),
                missing_information=[f"Valid product identifier (searched: {pid})"],
                customer_explanation=CustomerExplanation(
                    methodology_summary="Product ID lookup failed against catalog registry.",
                    data_sources_used=["Catalog Database"],
                    limitations_notice="Cannot evaluate unlisted product codes.",
                ),
                tools_executed=["product_information_tool"],
                execution_metadata={"latency_ms": latency_ms, "execution_mode": "Deterministic Validation"},
            )
            return resp.model_dump()

        # ── UNKNOWN INTENT ──
        if intent == AgentIntent.UNKNOWN_INTENT:
            latency_ms = round((time.time() - start_time) * 1000, 1)
            resp = AgentResponse(
                intent=AgentIntent.UNKNOWN_INTENT.value,
                summary_message=(
                    "I am Return or Regret AI, an assistant dedicated exclusively to "
                    "apparel fit analysis, return risk prediction, and shopping decision guidance."
                ),
                final_recommendation=(
                    "Please ask about apparel sizing, garment dimensions, fabric care, "
                    "or return policies for items in our catalog."
                ),
                missing_information=["In-domain e-commerce question"],
                customer_explanation=CustomerExplanation(
                    methodology_summary="Intent classification identified out-of-domain query.",
                    data_sources_used=["Intent Filter"],
                    limitations_notice="Agent only handles shopping decision, sizing, and product intelligence.",
                ),
                tools_executed=[],
                execution_metadata={"latency_ms": latency_ms, "execution_mode": "Intent Filter"},
            )
            return resp.model_dump()

        # Default to P001 if no product specified for product-related intents
        if not pid and intent != AgentIntent.RETURN_POLICY:
            pid = "P001"

        # ── 2. DYNAMIC INTENT-DRIVEN TOOL SELECTION ──
        executed_tools: List[str] = []
        tool_results: Dict[str, Any] = {}

        if intent == AgentIntent.PRODUCT_INFORMATION:
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            # Add RAG only for care/wash queries
            q_lower = query.lower()
            if any(w in q_lower for w in ("wash", "care", "shrink", "iron", "dry clean")):
                executed_tools.append("rag_retrieval_tool")
                tool_results["rag_retrieval_tool"] = rag_retrieval_tool(
                    query="fabric care wash temperature shrinkage"
                )

        elif intent == AgentIntent.SIZE_INFORMATION:
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("size_chart_tool")
            tool_results["size_chart_tool"] = size_chart_tool(product_id=pid, size=size)

        elif intent == AgentIntent.RETURN_POLICY:
            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(
                query="return window exchange refund policy bracketing"
            )

        elif intent == AgentIntent.RETURN_HISTORY_ANALYSIS:
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

        elif intent == AgentIntent.RETURN_RISK_PREDICTION:
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("return_risk_prediction_tool")
            tool_results["return_risk_prediction_tool"] = return_risk_prediction_tool(
                product_id=pid, selected_size=size
            )
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

        elif intent == AgentIntent.FIT_RECOMMENDATION:
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("size_chart_tool")
            tool_results["size_chart_tool"] = size_chart_tool(product_id=pid, size=size)
            if cust_meas:
                executed_tools.append("fit_calculator_tool")
                tool_results["fit_calculator_tool"] = fit_calculator_tool(
                    product_id=pid, selected_size=size, customer_measurements=cust_meas
                )

        elif intent == AgentIntent.PURCHASE_DECISION:
            # Full multi-tool workflow for comprehensive purchase advice
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("size_chart_tool")
            tool_results["size_chart_tool"] = size_chart_tool(product_id=pid, size=size)
            if cust_meas:
                executed_tools.append("fit_calculator_tool")
                tool_results["fit_calculator_tool"] = fit_calculator_tool(
                    product_id=pid, selected_size=size, customer_measurements=cust_meas
                )
            executed_tools.append("return_risk_prediction_tool")
            tool_results["return_risk_prediction_tool"] = return_risk_prediction_tool(
                product_id=pid, selected_size=size
            )
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)
            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(
                query=f"{pid} fit sizing tolerance quirks"
            )

        elif intent == AgentIntent.GENERAL_PRODUCT_QUESTION:
            # Only product info + RAG for general queries
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(
                query=f"{pid} product features specifications"
            )

        # ── 3. STRUCTURED RESPONSE SYNTHESIS ──
        structured_response = self._synthesize_structured_response(
            query=query,
            intent=intent,
            pid=pid,
            size=size,
            cust_meas=cust_meas,
            executed_tools=executed_tools,
            tool_results=tool_results,
            start_time=start_time,
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        # ── 4. TELEMETRY LOG ──
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "detected_intent": intent.value,
            "product_id": pid,
            "selected_size": size,
            "customer_measurements": cust_meas,
            "tools_called": executed_tools,
            "execution_time_ms": elapsed_ms,
            "execution_mode": structured_response.execution_metadata.get(
                "execution_mode", "Deterministic Academic Engine"
            ),
            "verdict": structured_response.verdict.value if structured_response.verdict else "N/A",
            "prediction_risk": (
                structured_response.ml_prediction.risk_tier if structured_response.ml_prediction else "N/A"
            ),
            "predicted_probability": (
                structured_response.ml_prediction.predicted_return_percentage
                if structured_response.ml_prediction
                else "N/A"
            ),
        }
        append_monitoring_log(log_entry)

        return structured_response.model_dump()

    # ──────────────────────────────────────────────────────
    # Response Synthesis
    # ──────────────────────────────────────────────────────
    def _synthesize_structured_response(
        self,
        query: str,
        intent: AgentIntent,
        pid: str,
        size: str,
        cust_meas: Dict[str, float],
        executed_tools: List[str],
        tool_results: Dict[str, Any],
        start_time: float,
    ) -> AgentResponse:
        prod = tool_results.get("product_information_tool", {})
        fit_calc = tool_results.get("fit_calculator_tool")
        risk_pred = tool_results.get("return_risk_prediction_tool")
        hist_analysis = tool_results.get("return_history_analyzer_tool")
        rag = tool_results.get("rag_retrieval_tool")
        size_chart = tool_results.get("size_chart_tool")

        p_name = prod.get("name", pid)
        mode = "Live LLM (Gemini 1.5 Flash)" if self.gemini_api_key else "Deterministic Academic Engine"

        # Evidence Sources
        sources: List[EvidenceSource] = []
        if rag and "citations" in rag:
            for c in rag["citations"][:3]:
                sources.append(
                    EvidenceSource(
                        title=c["title"],
                        document=c["document"],
                        confidence=c["confidence"],
                        snippet=c.get("snippet"),
                    )
                )

        # Missing information
        missing_info: List[str] = []
        if intent in (AgentIntent.FIT_RECOMMENDATION, AgentIntent.PURCHASE_DECISION):
            if "chest" not in cust_meas and "bust" not in cust_meas:
                missing_info.append("Chest / Bust measurement")
            if "waist" not in cust_meas:
                missing_info.append("Waist measurement")
            if prod.get("fit_type") == "Slim Fit" and "shoulder" not in cust_meas:
                missing_info.append("Shoulder width measurement (recommended for Slim Fit styles)")

        # Build Fit Assessment
        fit_assessment_obj = None
        measurement_comparison_items = None
        if fit_calc and fit_calc.get("status") == "success":
            comp_list = [
                MeasurementComparisonItem(
                    dimension=item["dimension"],
                    body_measurement=item["body_measurement"],
                    garment_measurement=item["garment_measurement"],
                    ease=item["ease"],
                    unit=item.get("unit", "inches"),
                    interpretation=item["interpretation"],
                    status=item["status"],
                )
                for item in fit_calc.get("measurement_comparison", [])
            ]
            measurement_comparison_items = comp_list

            alt_check_obj = None
            if fit_calc.get("alternative_size_check"):
                alt_raw = fit_calc["alternative_size_check"]
                alt_check_obj = AlternativeSizeEvaluation(
                    alternative_size=alt_raw["alternative_size"],
                    is_available_in_chart=alt_raw["is_available_in_chart"],
                    dimensions=alt_raw.get("dimensions"),
                    ease_analysis=alt_raw.get("ease_analysis"),
                    assessment_notes=alt_raw["assessment_notes"],
                )

            fit_assessment_obj = FitAssessment(
                verdict=FitVerdict(fit_calc.get("verdict", FitVerdict.GOOD_FIT.value)),
                confidence=fit_calc.get("confidence", 0.90),
                fit_type=fit_calc.get("fit_type", "Regular Fit"),
                tight_areas=fit_calc.get("tight_areas", []),
                loose_areas=fit_calc.get("loose_areas", []),
                measurement_comparison=comp_list,
                alternative_size_check=alt_check_obj,
                summary=fit_calc.get("summary", ""),
            )

        # Build ML Prediction
        ml_prediction_obj = None
        if risk_pred and risk_pred.get("status") == "success":
            ml_prediction_obj = MLPredictionOutput(
                predicted_return_probability=risk_pred.get("predicted_return_probability", 0.20),
                predicted_return_percentage=risk_pred.get("predicted_return_percentage", 20.0),
                risk_tier=risk_pred.get("risk_tier", "Low"),
                model_name=risk_pred.get("model_name", "Logistic Regression (Balanced)"),
                key_contributing_signals=risk_pred.get("key_contributing_signals", []),
                limitations=risk_pred.get("limitations", "Cohort pre-purchase baseline."),
            )

        # Build Historical Intelligence
        historical_analysis_obj = None
        if hist_analysis and hist_analysis.get("status") == "success":
            historical_analysis_obj = HistoricalIntelligence(
                total_orders_analyzed=hist_analysis.get("total_orders_analyzed", 0),
                overall_return_rate=hist_analysis.get("overall_return_rate", 0.0),
                category_baseline_rate=hist_analysis.get("category_baseline_rate", 20.0),
                risk_category=hist_analysis.get("risk_category", "Medium Risk"),
                top_return_reasons=hist_analysis.get("top_return_reasons", []),
                known_design_issues=hist_analysis.get("known_design_issues", "None reported"),
                representative_feedback=hist_analysis.get("representative_customer_feedback", []),
            )

        # Decision Synthesis
        decision_synthesis_obj = None
        verdict = None
        if fit_calc or risk_pred or hist_analysis:
            decision_synthesis_obj = DecisionSynthesisEngine.synthesize(
                prod_info=prod,
                fit_calc=fit_calc,
                risk_pred=risk_pred,
                hist_analysis=hist_analysis,
                selected_size=size,
                customer_measurements=cust_meas,
            )
            verdict = decision_synthesis_obj.reconciled_verdict

        # ── Final Recommendation & Summary Message ──
        if intent == AgentIntent.RETURN_POLICY:
            summary_message = "Our return policy offers a 30-day return window with free size exchanges."
            final_recommendation = (
                "Returns and exchanges are accepted within 30 days of delivery in unworn condition. "
                "Size exchanges are 100% free with prepaid return shipping labels. "
                "Our core policy: 'Fix the product page, not the customer' — "
                "you will never be penalized for legitimate sizing uncertainty."
            )
        elif intent == AgentIntent.PRODUCT_INFORMATION:
            mat = prod.get("material", "Cotton blend")
            care = prod.get("care_instructions", "Machine wash cold")
            summary_message = f"{p_name} is crafted from {mat} (${prod.get('price', 0):.2f})."
            final_recommendation = (
                f"Fabric composition: {mat}. Care guide: {care}. "
                f"Air dry to prevent thermal shrinkage."
            )
        elif intent == AgentIntent.SIZE_INFORMATION:
            summary_message = f"Size chart retrieved for {p_name} ({prod.get('fit_type', 'Regular Fit')})."
            final_recommendation = (
                f"Review the dimensions for Size {size} in the table above. "
                f"To test personal ease and comfort, enter your chest and waist measurements "
                f"in the customer measurements panel."
            )
        elif intent == AgentIntent.RETURN_HISTORY_ANALYSIS:
            rate = hist_analysis.get("overall_return_rate", 20.0) if hist_analysis else 20.0
            orders = hist_analysis.get("total_orders_analyzed", 0) if hist_analysis else 0
            summary_message = (
                f"Historical return rate for {p_name} is {rate}% across {orders} analyzed orders."
            )
            top_r = (
                hist_analysis.get("top_return_reasons", [{}])[0].get("reason", "Sizing issues")
                if hist_analysis
                else "Fit"
            )
            final_recommendation = (
                f"Primary customer return driver is '{top_r}'. "
                f"Check your personal measurements against our chart to prevent fit-related returns."
            )
        elif intent == AgentIntent.RETURN_RISK_PREDICTION:
            prob = risk_pred.get("predicted_return_percentage", 20.0) if risk_pred else 20.0
            tier = risk_pred.get("risk_tier", "Low") if risk_pred else "Low"
            summary_message = f"Predicted return probability for Size {size} is {prob}% ({tier} Risk)."
            model = risk_pred.get("model_name", "Scikit-learn ML") if risk_pred else "ML"
            final_recommendation = (
                f"Model evaluation: {model}. "
                f"This reflects cohort characteristics. "
                f"To ensure personal fit, verify your body ease against the size chart."
            )
        elif decision_synthesis_obj:
            summary_message = decision_synthesis_obj.reconciliation_explanation
            final_recommendation = decision_synthesis_obj.actionable_advice
        else:
            summary_message = f"Product intelligence consultation for {p_name}."
            final_recommendation = (
                "Provide your personal measurements to evaluate customized fit and return risk."
            )

        customer_explanation = DecisionSynthesisEngine.generate_customer_explanation(
            tools_used=executed_tools, has_measurements=bool(cust_meas)
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        return AgentResponse(
            intent=intent.value,
            product_id=pid,
            product_name=p_name,
            selected_size=size,
            summary_message=summary_message,
            verdict=verdict,
            fit_assessment=fit_assessment_obj,
            measurement_comparison=measurement_comparison_items,
            ml_prediction=ml_prediction_obj,
            historical_analysis=historical_analysis_obj,
            decision_synthesis=decision_synthesis_obj,
            final_recommendation=final_recommendation,
            evidence_sources=sources,
            missing_information=missing_info,
            customer_explanation=customer_explanation,
            tools_executed=executed_tools,
            execution_metadata={
                "latency_ms": elapsed_ms,
                "execution_mode": mode,
                "timestamp": datetime.now().isoformat(),
            },
        )


agent_controller = AIAgentController()
