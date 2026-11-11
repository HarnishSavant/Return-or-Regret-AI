import json
import os
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

from tools.agent_tools import (
    AVAILABLE_TOOLS,
    product_information_tool,
    size_chart_tool,
    fit_calculator_tool,
    return_risk_prediction_tool,
    return_history_analyzer_tool,
    rag_retrieval_tool,
    PRODUCTS_CACHE
)
from schemas.agent_schemas import (
    AgentResponse,
    FitVerdict,
    FitAssessment,
    MeasurementComparisonItem,
    AlternativeSizeEvaluation,
    MLPredictionOutput,
    HistoricalIntelligence,
    DecisionSynthesis,
    EvidenceSource,
    CustomerExplanation
)
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

    def _extract_entities(self, query: str, context_product_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts product ID, sizes, and numeric measurements (chest, waist, hip, shoulder, inseam).
        """
        extracted_pid = None
        is_invalid_pid = False
        
        # Check explicit PID format like P001, P002, etc.
        match_pid = re.search(r'\b(P\d{3,4})\b', query, re.IGNORECASE)
        if match_pid:
            candidate_pid = match_pid.group(1).upper()
            if candidate_pid in PRODUCTS_CACHE:
                extracted_pid = candidate_pid
            else:
                extracted_pid = candidate_pid
                is_invalid_pid = True
        elif context_product_id:
            c_pid = context_product_id.strip().upper()
            if c_pid in PRODUCTS_CACHE:
                extracted_pid = c_pid
            else:
                extracted_pid = c_pid
                is_invalid_pid = True
        else:
            # Match product keywords from catalog
            q_lower = query.lower()
            for pid, p in PRODUCTS_CACHE.items():
                name_words = [w for w in p["name"].lower().split() if len(w) > 3]
                if any(w in q_lower for w in name_words):
                    extracted_pid = pid
                    break

        # Extract size mention
        size = None
        size_match = re.search(r'\bsize\s+([A-Za-z0-9]+)\b', query, re.IGNORECASE)
        if size_match:
            size = size_match.group(1).upper()
        else:
            standalone_match = re.search(r'\b(XS|XXL|XL|S|M|L)\b', query)
            if standalone_match:
                size = standalone_match.group(1).upper()
            else:
                num_size_match = re.search(r'\b(2[89]|3[0-8]|4[0-2])\b', query)
                if num_size_match:
                    size = num_size_match.group(1)

        # Default size M if not specified and valid product exists
        if not size and extracted_pid and extracted_pid in PRODUCTS_CACHE:
            p_obj = PRODUCTS_CACHE[extracted_pid]
            size = "M" if "M" in p_obj["sizes"] else p_obj["sizes"][0]

        # Extract numeric body measurements
        measurements: Dict[str, float] = {}

        # Chest / bust
        m_chest = re.search(r'\b(chest|bust)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_chest:
            val = float(m_chest.group(2))
            if val > 60.0:
                val = round(val / 2.54, 1)
            measurements["chest"] = val

        # Waist
        m_waist = re.search(r'\b(waist)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_waist:
            val = float(m_waist.group(2))
            if val > 60.0:
                val = round(val / 2.54, 1)
            measurements["waist"] = val

        # Hip
        m_hip = re.search(r'\b(hip)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_hip:
            val = float(m_hip.group(2))
            measurements["hip"] = val

        # Shoulder
        m_sh = re.search(r'\b(shoulder)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_sh:
            val = float(m_sh.group(2))
            measurements["shoulder"] = val

        # Inseam
        m_ins = re.search(r'\b(inseam)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_ins:
            val = float(m_ins.group(2))
            measurements["inseam"] = val

        return {
            "product_id": extracted_pid,
            "is_invalid_pid": is_invalid_pid,
            "selected_size": size or "M",
            "customer_measurements": measurements
        }

    def _determine_intent(self, query: str) -> str:
        q = query.lower()

        # Check for completely irrelevant / out-of-domain queries
        if any(w in q for w in ["weather", "capital of", "president", "rolex", "bitcoin", "recipe for", "who wrote", "tell me a joke"]):
            return "UNSUPPORTED_OR_IRRELEVANT"

        if any(w in q for w in ["return policy", "exchange policy", "how to return", "refund", "return window", "days to return", "policy"]):
            return "RETURN_POLICY_INQUIRY"
        elif any(w in q for w in ["why do customers return", "why returned", "return history", "common reasons for return", "defect patterns"]):
            return "RETURN_HISTORY_INQUIRY"
        elif any(w in q for w in ["probability of return", "ml risk", "predicted return", "ml prediction", "predicted probability"]):
            return "RETURN_RISK_INQUIRY"
        elif any(w in q for w in ["should i buy", "should i purchase", "decide on", "decision"]):
            return "COMPLEX_PURCHASE_DECISION"
        elif any(w in q for w in ["size chart", "measurements of", "garment dimensions", "length and chest dimensions"]):
            return "SIZE_CHART_INQUIRY"
        elif any(w in q for w in ["fit", "will it fit", "chest is", "waist is", "sizing", "tight", "loose", "size recommend", "what size"]):
            return "FIT_RECOMMENDATION"
        elif any(w in q for w in ["material", "fabric", "wash", "care", "cotton", "wool", "silk", "price", "how much", "cost"]):
            return "PRODUCT_SPECS_AND_CARE"
        else:
            return "GENERAL_PRODUCT_CONSULTATION"

    def process_query(
        self,
        query: str,
        context_product_id: Optional[str] = None,
        context_measurements: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Intent Detection & Entity Extraction
        intent = self._determine_intent(query)
        entities = self._extract_entities(query, context_product_id)
        
        # Merge explicitly passed context measurements
        if context_measurements:
            for k, v in context_measurements.items():
                if k not in entities["customer_measurements"]:
                    entities["customer_measurements"][k] = float(v)

        pid = entities["product_id"]
        is_invalid_pid = entities["is_invalid_pid"]
        size = entities["selected_size"]
        cust_meas = entities["customer_measurements"]

        # Handling Invalid Product ID
        if is_invalid_pid:
            latency_ms = round((time.time() - start_time) * 1000, 1)
            resp = AgentResponse(
                intent="INVALID_PRODUCT_ID",
                product_id=pid,
                summary_message=f"Product ID '{pid}' is not found in our verified catalog.",
                final_recommendation=f"We could not locate product '{pid}'. Available catalog IDs are: {', '.join(sorted(PRODUCTS_CACHE.keys())[:6])}...",
                missing_information=[f"Valid product identifier (searched: {pid})"],
                customer_explanation=CustomerExplanation(
                    methodology_summary="Product ID lookup failed against catalog registry.",
                    data_sources_used=["Catalog Database"],
                    limitations_notice="Cannot evaluate unlisted product codes."
                ),
                tools_executed=["product_information_tool"],
                execution_metadata={"latency_ms": latency_ms, "execution_mode": "Deterministic Validation"}
            )
            return resp.model_dump()

        # Handling Irrelevant Query
        if intent == "UNSUPPORTED_OR_IRRELEVANT":
            latency_ms = round((time.time() - start_time) * 1000, 1)
            resp = AgentResponse(
                intent="UNSUPPORTED_OR_IRRELEVANT",
                summary_message="I am Return or Regret AI, an assistant dedicated exclusively to apparel fit analysis, return risk prediction, and shopping decision guidance.",
                final_recommendation="Please ask about apparel sizing, garment dimensions, fabric care, or return policies for items in our catalog.",
                missing_information=["In-domain e-commerce question"],
                customer_explanation=CustomerExplanation(
                    methodology_summary="Intent classification identified out-of-domain query.",
                    data_sources_used=["Intent Filter"],
                    limitations_notice="Agent only handles shopping decision, sizing, and product intelligence."
                ),
                tools_executed=[],
                execution_metadata={"latency_ms": latency_ms, "execution_mode": "Intent Filter"}
            )
            return resp.model_dump()

        # Default fallback to P001 if no product specified at all for product inquiries
        if not pid and intent not in ["RETURN_POLICY_INQUIRY"]:
            pid = "P001"

        # 2. DYNAMIC INTENT-DRIVEN TOOL SELECTION
        executed_tools = []
        tool_results = {}

        # Tool Selection Mapping
        if intent == "PRODUCT_SPECS_AND_CARE":
            # ONLY product_information_tool (+ RAG if care inquiry)
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            if any(w in query.lower() for w in ["wash", "care", "shrink"]):
                executed_tools.append("rag_retrieval_tool")
                tool_results["rag_retrieval_tool"] = rag_retrieval_tool(query="fabric care wash temperature shrinkage")

        elif intent == "SIZE_CHART_INQUIRY":
            # ONLY size_chart_tool + product_information_tool
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("size_chart_tool")
            tool_results["size_chart_tool"] = size_chart_tool(product_id=pid, size=size)

        elif intent == "RETURN_POLICY_INQUIRY":
            # ONLY rag_retrieval_tool
            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(query="return window exchange refund policy bracketing")

        elif intent == "RETURN_HISTORY_INQUIRY":
            # ONLY return_history_analyzer_tool + product_information_tool
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

        elif intent == "RETURN_RISK_INQUIRY":
            # ONLY return_risk_prediction_tool + return_history_analyzer_tool
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)
            executed_tools.append("return_risk_prediction_tool")
            tool_results["return_risk_prediction_tool"] = return_risk_prediction_tool(product_id=pid, selected_size=size)
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

        elif intent in ["FIT_RECOMMENDATION", "COMPLEX_PURCHASE_DECISION", "GENERAL_PRODUCT_CONSULTATION"]:
            # Multi-tool workflow
            executed_tools.append("product_information_tool")
            tool_results["product_information_tool"] = product_information_tool(product_id=pid)

            executed_tools.append("size_chart_tool")
            tool_results["size_chart_tool"] = size_chart_tool(product_id=pid, size=size)

            if cust_meas:
                executed_tools.append("fit_calculator_tool")
                tool_results["fit_calculator_tool"] = fit_calculator_tool(
                    product_id=pid,
                    selected_size=size,
                    customer_measurements=cust_meas
                )

            executed_tools.append("return_risk_prediction_tool")
            tool_results["return_risk_prediction_tool"] = return_risk_prediction_tool(product_id=pid, selected_size=size)

            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(query=f"{pid} fit sizing tolerance quirks")

        # 3. STRUCTURED DECISION SYNTHESIS & EVIDENCE VALIDATION
        structured_response = self._synthesize_structured_response(
            query=query,
            intent=intent,
            pid=pid,
            size=size,
            cust_meas=cust_meas,
            executed_tools=executed_tools,
            tool_results=tool_results,
            start_time=start_time
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        # 4. STRUCTURED TELEMETRY LOG ENTRY (for Developer / Academic Monitoring)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "detected_intent": intent,
            "product_id": pid,
            "selected_size": size,
            "customer_measurements": cust_meas,
            "tools_called": executed_tools,
            "execution_time_ms": elapsed_ms,
            "execution_mode": structured_response.execution_metadata.get("execution_mode", "Deterministic Academic Engine"),
            "verdict": structured_response.verdict.value if structured_response.verdict else "N/A",
            "prediction_risk": structured_response.ml_prediction.risk_tier if structured_response.ml_prediction else "N/A",
            "predicted_probability": structured_response.ml_prediction.predicted_return_percentage if structured_response.ml_prediction else "N/A"
        }
        append_monitoring_log(log_entry)

        # Convert to dictionary conforming to AgentResponse schema
        return structured_response.model_dump()

    def _synthesize_structured_response(
        self,
        query: str,
        intent: str,
        pid: str,
        size: str,
        cust_meas: Dict[str, float],
        executed_tools: List[str],
        tool_results: Dict[str, Any],
        start_time: float
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
                sources.append(EvidenceSource(
                    title=c["title"],
                    document=c["document"],
                    confidence=c["confidence"],
                    snippet=c.get("snippet")
                ))

        # Missing information detector
        missing_info: List[str] = []
        if intent in ["FIT_RECOMMENDATION", "COMPLEX_PURCHASE_DECISION"]:
            if "chest" not in cust_meas and "bust" not in cust_meas:
                missing_info.append("Chest / Bust measurement")
            if "waist" not in cust_meas:
                missing_info.append("Waist measurement")
            if prod.get("fit_type") == "Slim Fit" and "shoulder" not in cust_meas:
                missing_info.append("Shoulder width measurement (recommended for Slim Fit styles)")

        # Build Fit Assessment object if fit_calculator was run
        fit_assessment_obj = None
        measurement_comparison_items = None
        if fit_calc and fit_calc.get("status") == "success":
            comp_list = []
            for item in fit_calc.get("measurement_comparison", []):
                comp_list.append(MeasurementComparisonItem(
                    dimension=item["dimension"],
                    body_measurement=item["body_measurement"],
                    garment_measurement=item["garment_measurement"],
                    ease=item["ease"],
                    unit=item.get("unit", "inches"),
                    interpretation=item["interpretation"],
                    status=item["status"]
                ))
            measurement_comparison_items = comp_list

            alt_check_obj = None
            if fit_calc.get("alternative_size_check"):
                alt_raw = fit_calc["alternative_size_check"]
                alt_check_obj = AlternativeSizeEvaluation(
                    alternative_size=alt_raw["alternative_size"],
                    is_available_in_chart=alt_raw["is_available_in_chart"],
                    dimensions=alt_raw.get("dimensions"),
                    ease_analysis=alt_raw.get("ease_analysis"),
                    assessment_notes=alt_raw["assessment_notes"]
                )

            fit_assessment_obj = FitAssessment(
                verdict=FitVerdict(fit_calc.get("verdict", FitVerdict.GOOD_FIT.value)),
                confidence=fit_calc.get("confidence", 0.90),
                fit_type=fit_calc.get("fit_type", "Regular Fit"),
                tight_areas=fit_calc.get("tight_areas", []),
                loose_areas=fit_calc.get("loose_areas", []),
                measurement_comparison=comp_list,
                alternative_size_check=alt_check_obj,
                summary=fit_calc.get("summary", "")
            )

        # Build ML Prediction Output if return_risk was run
        ml_prediction_obj = None
        if risk_pred and risk_pred.get("status") == "success":
            ml_prediction_obj = MLPredictionOutput(
                predicted_return_probability=risk_pred.get("predicted_return_probability", 0.20),
                predicted_return_percentage=risk_pred.get("predicted_return_percentage", 20.0),
                risk_tier=risk_pred.get("risk_tier", "Low"),
                model_name=risk_pred.get("model_name", "Logistic Regression (Balanced)"),
                key_contributing_signals=risk_pred.get("key_contributing_signals", []),
                limitations=risk_pred.get("limitations", "Cohort pre-purchase baseline.")
            )

        # Build Historical Intelligence if return_history was run
        historical_analysis_obj = None
        if hist_analysis and hist_analysis.get("status") == "success":
            historical_analysis_obj = HistoricalIntelligence(
                total_orders_analyzed=hist_analysis.get("total_orders_analyzed", 0),
                overall_return_rate=hist_analysis.get("overall_return_rate", 0.0),
                category_baseline_rate=hist_analysis.get("category_baseline_rate", 20.0),
                risk_category=hist_analysis.get("risk_category", "Medium Risk"),
                top_return_reasons=hist_analysis.get("top_return_reasons", []),
                known_design_issues=hist_analysis.get("known_design_issues", "None reported"),
                representative_feedback=hist_analysis.get("representative_customer_feedback", [])
            )

        # Run Decision Synthesis Engine
        decision_synthesis_obj = None
        verdict = None
        if fit_calc or risk_pred or hist_analysis:
            decision_synthesis_obj = DecisionSynthesisEngine.synthesize(
                prod_info=prod,
                fit_calc=fit_calc,
                risk_pred=risk_pred,
                hist_analysis=hist_analysis,
                selected_size=size,
                customer_measurements=cust_meas
            )
            verdict = decision_synthesis_obj.reconciled_verdict

        # Formulate Final Recommendation & Summary Message
        if intent == "RETURN_POLICY_INQUIRY":
            summary_message = "Our return policy offers a 30-day return window with free size exchanges."
            final_recommendation = (
                "Returns and exchanges are accepted within 30 days of delivery in unworn condition. "
                "Size exchanges are 100% free with prepaid return shipping labels. "
                "Our core policy: 'Fix the product page, not the customer' — you will never be penalized for legitimate sizing uncertainty."
            )
        elif intent == "PRODUCT_SPECS_AND_CARE":
            mat = prod.get("material", "Cotton blend")
            care = prod.get("care_instructions", "Machine wash cold")
            summary_message = f"{p_name} is crafted from {mat} (${prod.get('price', 0):.2f})."
            final_recommendation = f"Fabric composition: {mat}. Care guide: {care}. Air dry to prevent thermal shrinkage."
        elif intent == "SIZE_CHART_INQUIRY":
            summary_message = f"Size chart retrieved for {p_name} ({prod.get('fit_type', 'Regular Fit')})."
            final_recommendation = (
                f"Review the dimensions for Size {size} in the table above. "
                f"To test personal ease and comfort, enter your chest and waist measurements in the customer measurements panel."
            )
        elif intent == "RETURN_HISTORY_INQUIRY":
            rate = hist_analysis.get("overall_return_rate", 20.0) if hist_analysis else 20.0
            summary_message = f"Historical return rate for {p_name} is {rate}% across {hist_analysis.get('total_orders_analyzed', 0) if hist_analysis else 0} analyzed orders."
            top_r = hist_analysis.get("top_return_reasons", [{}])[0].get("reason", "Sizing issues") if hist_analysis else "Fit"
            final_recommendation = f"Primary customer return driver is '{top_r}'. Check your personal measurements against our chart to prevent fit-related returns."
        elif intent == "RETURN_RISK_INQUIRY":
            prob = risk_pred.get("predicted_return_percentage", 20.0) if risk_pred else 20.0
            summary_message = f"Predicted return probability for Size {size} is {prob}% ({risk_pred.get('risk_tier', 'Low') if risk_pred else 'Low'} Risk)."
            final_recommendation = (
                f"Model evaluation: {risk_pred.get('model_name', 'Scikit-learn ML') if risk_pred else 'ML'}. "
                f"This reflects cohort characteristics. To ensure personal fit, verify your body ease against the size chart."
            )
        elif decision_synthesis_obj:
            summary_message = decision_synthesis_obj.reconciliation_explanation
            final_recommendation = decision_synthesis_obj.actionable_advice
        else:
            summary_message = f"Product intelligence consultation for {p_name}."
            final_recommendation = "Provide your personal measurements to evaluate customized fit and return risk."

        customer_explanation = DecisionSynthesisEngine.generate_customer_explanation(
            tools_used=executed_tools,
            has_measurements=bool(cust_meas)
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        return AgentResponse(
            intent=intent,
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
                "timestamp": datetime.now().isoformat()
            }
        )

agent_controller = AIAgentController()
