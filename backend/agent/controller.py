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
    logs.insert(0, log_entry) # Most recent first
    # Keep last 500 logs
    logs = logs[:500]
    with open(MONITORING_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

class AIAgentController:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def _extract_entities(self, query: str, context_product_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts product ID, sizes, and numeric measurements (chest, waist, hip, shoulder, inseam, height, weight).
        """
        extracted_pid = None
        
        # Check explicit PID format like P001, P002, etc.
        match_pid = re.search(r'\b(P0\d{2})\b', query, re.IGNORECASE)
        if match_pid:
            extracted_pid = match_pid.group(1).upper()
        elif context_product_id:
            extracted_pid = context_product_id.strip().upper()
        else:
            # Match product keywords
            q_lower = query.lower()
            for pid, p in PRODUCTS_CACHE.items():
                name_words = [w for w in p["name"].lower().split() if len(w) > 3]
                if any(w in q_lower for w in name_words):
                    extracted_pid = pid
                    break

        # Default fallback to P001 if no product specified at all
        if not extracted_pid:
            extracted_pid = "P001"

        # Extract size mention (S, M, L, XL, XXL, 30, 32, 34, etc.)
        size = None
        size_match = re.search(r'\bsize\s+([A-Za-z0-9]+)\b', query, re.IGNORECASE)
        if size_match:
            size = size_match.group(1).upper()
        else:
            # Check standalone letter sizes
            standalone_match = re.search(r'\b(XS|XXL|XL|S|M|L)\b', query)
            if standalone_match:
                size = standalone_match.group(1).upper()
            else:
                num_size_match = re.search(r'\b(2[89]|3[0-8]|4[0-2])\b', query)
                if num_size_match:
                    size = num_size_match.group(1)

        # Default size M if not specified
        if not size:
            p_obj = PRODUCTS_CACHE.get(extracted_pid)
            size = "M" if p_obj and "M" in p_obj["sizes"] else (p_obj["sizes"][0] if p_obj else "M")

        # Extract numeric body measurements
        measurements: Dict[str, float] = {}
        # Chest / bust
        m_chest = re.search(r'\b(chest|bust)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_chest:
            val = float(m_chest.group(2))
            measurements["chest"] = val

        # Waist
        m_waist = re.search(r'\bwaist\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_waist:
            val = float(m_waist.group(2))
            measurements["waist"] = val

        # Hip
        m_hip = re.search(r'\bhip\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_hip:
            val = float(m_hip.group(2))
            measurements["hip"] = val

        # Shoulder
        m_sh = re.search(r'\bshoulder\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_sh:
            val = float(m_sh.group(2))
            measurements["shoulder"] = val

        # Inseam
        m_ins = re.search(r'\binseam\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|\"|cm)?', query, re.IGNORECASE)
        if m_ins:
            val = float(m_ins.group(2))
            measurements["inseam"] = val

        return {
            "product_id": extracted_pid,
            "selected_size": size,
            "customer_measurements": measurements
        }

    def _determine_intent(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["return policy", "exchange policy", "how to return", "refund", "return window", "days to return"]):
            return "RETURN_POLICY_INQUIRY"
        elif any(w in q for w in ["fit", "will it fit", "size m", "chest", "waist", "tight", "loose", "size recommend", "which size"]):
            return "FIT_RECOMMENDATION"
        elif any(w in q for w in ["risk", "return rate", "probability of return", "why returned", "return history"]):
            return "RETURN_RISK_ANALYSIS"
        elif any(w in q for w in ["size chart", "measurements", "dimensions", "length", "sleeve"]):
            return "SIZE_CHART_INQUIRY"
        elif any(w in q for w in ["material", "fabric", "wash", "care", "cotton", "wool", "silk"]):
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
        size = entities["selected_size"]
        cust_meas = entities["customer_measurements"]

        # 2. Tool Execution Workflow
        executed_tools = []
        tool_results = {}

        # Always fetch product details
        executed_tools.append("product_information_tool")
        prod_info = product_information_tool(product_id=pid)
        tool_results["product_information_tool"] = prod_info

        # Route workflows based on intent
        if intent in ["FIT_RECOMMENDATION", "SIZE_CHART_INQUIRY", "GENERAL_PRODUCT_CONSULTATION"]:
            # Execute Size Chart Tool
            executed_tools.append("size_chart_tool")
            tool_results["size_chart_tool"] = size_chart_tool(product_id=pid, size=size)

            # If measurements exist, execute Fit Calculator Tool
            if cust_meas:
                executed_tools.append("fit_calculator_tool")
                tool_results["fit_calculator_tool"] = fit_calculator_tool(
                    product_id=pid,
                    selected_size=size,
                    customer_measurements=cust_meas
                )

            # Execute Return History Analyzer Tool
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

            # Execute Return Risk ML Prediction Tool
            executed_tools.append("return_risk_prediction_tool")
            tool_results["return_risk_prediction_tool"] = return_risk_prediction_tool(
                product_id=pid,
                selected_size=size
            )

            # Execute RAG Retrieval Tool
            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(
                query=f"{prod_info.get('name', pid)} fit dimensions sizing tolerance quirks"
            )

        elif intent == "RETURN_RISK_ANALYSIS":
            executed_tools.append("return_history_analyzer_tool")
            tool_results["return_history_analyzer_tool"] = return_history_analyzer_tool(product_id=pid)

            executed_tools.append("return_risk_prediction_tool")
            tool_results["return_risk_prediction_tool"] = return_risk_prediction_tool(
                product_id=pid,
                selected_size=size
            )

            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(query=f"{pid} return reasons defect patterns")

        elif intent == "RETURN_POLICY_INQUIRY":
            executed_tools.append("rag_retrieval_tool")
            tool_results["rag_retrieval_tool"] = rag_retrieval_tool(query="Return exchange window refund process bracketing policy")

        # 3. Synthesize Final Explainable Response
        final_answer, sources, execution_mode = self._generate_response(
            query=query,
            intent=intent,
            entities=entities,
            tool_results=tool_results
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        # 4. Structure Log Entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "detected_intent": intent,
            "product_id": pid,
            "selected_size": size,
            "customer_measurements": cust_meas,
            "tools_called": executed_tools,
            "execution_time_ms": elapsed_ms,
            "execution_mode": execution_mode,
            "status": "success",
            "prediction_risk": tool_results.get("return_risk_prediction_tool", {}).get("risk_level", "N/A"),
            "predicted_probability": tool_results.get("return_risk_prediction_tool", {}).get("predicted_return_percentage", "N/A")
        }
        append_monitoring_log(log_entry)

        return {
            "query": query,
            "intent": intent,
            "entities": entities,
            "tools_executed": executed_tools,
            "tool_results": tool_results,
            "final_answer": final_answer,
            "sources": sources,
            "execution_mode": execution_mode,
            "latency_ms": elapsed_ms
        }

    def _generate_response(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        tool_results: Dict[str, Any]
    ):
        prod = tool_results.get("product_information_tool", {})
        fit_calc = tool_results.get("fit_calculator_tool", {})
        risk_pred = tool_results.get("return_risk_prediction_tool", {})
        hist_analysis = tool_results.get("return_history_analyzer_tool", {})
        rag = tool_results.get("rag_retrieval_tool", {})
        size_chart = tool_results.get("size_chart_tool", {})

        citations = []
        if rag and "citations" in rag:
            for c in rag["citations"][:3]:
                citations.append({
                    "title": c["section_title"],
                    "document": c["source_document"],
                    "confidence": f"{round(c['similarity_score']*100, 1)}%"
                })

        # Try Live LLM API if key is present
        if self.gemini_api_key:
            try:
                system_prompt = (
                    "You are 'Return or Regret AI', an expert intelligent e-commerce decision assistant.\n"
                    "Your goal is to prevent avoidable customer returns by providing precise, evidence-based recommendations.\n"
                    "Base your answer strictly on the Python tool execution results provided.\n"
                    "Do NOT invent measurements or probabilities. If data is missing, explicitly say so.\n"
                    "Format responses with clear markdown: Fit Recommendation, Garment Dimension Comparison, Return Risk Profile, and Advice."
                )
                
                context_summary = {
                    "user_query": query,
                    "product_info": prod,
                    "fit_calculator": fit_calc,
                    "ml_return_risk_prediction": risk_pred,
                    "historical_return_data": hist_analysis,
                    "verified_knowledge_base_citations": rag.get("citations", [])
                }

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{system_prompt}\n\nTOOL OBSERVATIONS:\n{json.dumps(context_summary, indent=2)}\n\nUSER QUESTION: {query}"}
                        ]
                    }]
                }

                resp = httpx.post(url, json=payload, timeout=8.0)
                if resp.status_code == 200:
                    data = resp.json()
                    llm_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return llm_text, citations, "Live LLM Engine (Gemini 1.5 Flash)"
            except Exception as e:
                print(f"LLM API call failed or timed out ({e}). Falling back to deterministic engine.")

        # Deterministic Academic Demonstration Engine (Transparent & Explainable)
        p_name = prod.get("name", "Product")
        p_cat = prod.get("category", "Apparel")
        p_fit = prod.get("fit_type", "Regular Fit")
        p_price = prod.get("price", 0.0)
        selected_size = entities.get("selected_size", "M")
        cust_meas = entities.get("customer_measurements", {})

        sections = []

        if intent == "RETURN_POLICY_INQUIRY":
            sections.append(f"### Return & Exchange Policy Summary\n")
            sections.append("- **Return Window:** 30 calendar days from delivery date.")
            sections.append("- **Size Exchanges:** 100% Free with complimentary return shipping label.")
            sections.append("- **No Customer Penalty:** We fix the product page, not the customer. Legitimate returns never penalize your account.")
            sections.append("- **Condition:** Items must be in unwashed, unworn condition with original tags intact.")
            sections.append("- **Refund Processing:** Issued within 3-5 business days upon warehouse quality inspection.")
            sections.append("\n*Tip: If you're deciding between two consecutive sizes, provide your measurements below to avoid bracket-ordering!*")

        elif fit_calc and fit_calc.get("status") == "success":
            verdict = fit_calc.get("overall_verdict", "Fit Analysis Complete")
            rec_summary = fit_calc.get("recommendation_summary", "")
            tight_areas = fit_calc.get("tight_areas", [])
            meas_analysis = fit_calc.get("measurement_analysis", {})

            sections.append(f"### Fit Verdict for {p_name} (Size {selected_size})\n")
            
            if "Too Small" in verdict or "Tight" in verdict:
                sections.append(f"⚠️ **Assessment:** **{verdict}**")
            elif "Roomy" in verdict:
                sections.append(f"ℹ️ **Assessment:** **{verdict}**")
            else:
                sections.append(f"✅ **Assessment:** **{verdict}**")

            sections.append(f"\n{rec_summary}\n")

            # Garment vs Body Breakdown
            sections.append("#### 📐 Measurement & Ease Comparison")
            for dim, vals in meas_analysis.items():
                g_val = vals.get("garment")
                b_val = vals.get("body")
                ease = vals.get("ease", vals.get("difference", 0.0))
                sections.append(f"- **{dim.title()}:** Garment is **{g_val}\"** vs your body **{b_val}\"** (Ease: **{'+' if ease >= 0 else ''}{ease}\"**)")

            # Return Risk Signal from ML
            if risk_pred and risk_pred.get("status") == "success":
                prob = risk_pred.get("predicted_return_percentage", 20.0)
                risk_lvl = risk_pred.get("risk_level", "Medium")
                model_used = risk_pred.get("ml_model_used", "Scikit-Learn ML")
                sections.append(f"\n#### 🤖 Return Risk ML Prediction")
                sections.append(f"- **Predicted Return Probability:** **{prob}%** ({risk_lvl} Risk Tier)")
                sections.append(f"- **Model Evaluated:** {model_used} (Trained on verified pre-purchase features)")
                
                signals = risk_pred.get("key_contributing_signals", [])
                if signals:
                    sections.append(f"- **Contributing Factors:** {'; '.join(signals)}")

            # Historical Return Patterns
            if hist_analysis and hist_analysis.get("status") == "success":
                ret_rate = hist_analysis.get("overall_return_rate", 20.0)
                top_reasons = hist_analysis.get("top_return_reasons", [])
                quirks = hist_analysis.get("known_design_issues", "")
                
                sections.append(f"\n#### 📊 Historical Product Intelligence")
                sections.append(f"- **Historical Return Rate:** **{ret_rate}%** across {hist_analysis.get('total_orders_analyzed', 0)} analyzed orders.")
                if top_reasons:
                    top_r = top_reasons[0]
                    sections.append(f"- **Primary Return Reason:** {top_r['reason']} ({top_r['percentage']}% of returns).")
                if quirks and quirks != "None reported":
                    sections.append(f"- **Known Design Quirk:** {quirks}")

        elif size_chart and size_chart.get("status") == "success":
            chart = size_chart.get("full_size_chart", {})
            sections.append(f"### Sizing Information for {p_name}\n")
            sections.append(f"- **Category:** {p_cat} | **Fit Silhouette:** {p_fit} | **Price:** ${p_price:.2f}")
            sections.append(f"- **Material:** {prod.get('material', 'Standard Blend')}")
            sections.append(f"\n**Available Sizes & Dimensions (Inches):**")
            for sz, dims in list(chart.items())[:5]:
                dim_str = ", ".join([f"{k.capitalize()}: {v}\"" for k, v in dims.items()])
                sections.append(f"- **Size {sz}:** {dim_str}")
            
            sections.append("\n*To get an exact fit match, reply with your body measurements (e.g., 'My chest is 40 inches and waist is 34')!*")

        else:
            sections.append(f"### Product Consultation: {p_name}\n")
            sections.append(f"- **Category:** {p_cat} | **Fit Type:** {p_fit} | **Price:** ${p_price:.2f}")
            sections.append(f"- **Fabric Composition:** {prod.get('material', 'Standard Blend')}")
            sections.append(f"- **Care Instructions:** {prod.get('care_instructions', 'Standard machine wash')}")
            sections.append(f"- **Historical Return Rate:** {prod.get('historical_return_rate', 20.0)}% ({prod.get('risk_category', 'Medium Risk')})")
            if prod.get("known_fit_quirks"):
                sections.append(f"- **Fit Advisory:** {prod.get('known_fit_quirks')}")

        final_text = "\n".join(sections)
        mode = "Deterministic Academic Engine (Rule & Model-Driven)"
        return final_text, citations, mode

agent_controller = AIAgentController()
