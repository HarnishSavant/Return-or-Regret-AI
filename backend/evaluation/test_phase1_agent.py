"""
Phase 1.2 Comprehensive Evaluation Suite
=========================================
Tests intent classification, structured entity extraction, dynamic tool selection,
and edge cases across at least 30 distinct scenarios covering:
- All 9 canonical intents
- Natural query phrasings and colloquial variations
- Product ID extraction and validation
- Clothing size extraction (letter & numeric)
- Body measurement extraction & cm-to-inches conversion
- Missing required measurements detection
- Ambiguous & conflicting queries
- Out-of-domain and invalid queries
- The dimensions keyword regression query
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.controller import agent_controller
from schemas.agent_schemas import AgentIntent

# 32 comprehensive test cases covering all requirements
EVAL_CASES = [
    # --- PRODUCT_INFORMATION (1-4) ---
    {
        "id": "TC-P1-01",
        "name": "Material inquiry",
        "query": "What material is P001 made from?",
        "expected_intent": AgentIntent.PRODUCT_INFORMATION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_tools": ["product_information_tool"],
    },
    {
        "id": "TC-P1-02",
        "name": "Price inquiry",
        "query": "How much does P002 cost?",
        "expected_intent": AgentIntent.PRODUCT_INFORMATION.value,
        "expected_pid": "P002",
        "expected_size": "M",
        "expected_tools": ["product_information_tool"],
    },
    {
        "id": "TC-P1-03",
        "name": "Fabric care with wash keywords (triggers RAG)",
        "query": "How do I wash P005 and will it shrink?",
        "expected_intent": AgentIntent.PRODUCT_INFORMATION.value,
        "expected_pid": "P005",
        "expected_size": "30",
        "expected_tools": ["product_information_tool", "rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-04",
        "name": "Product description by name",
        "query": "Is the Heritage Oxford shirt cotton or polyester?",
        "expected_intent": AgentIntent.PRODUCT_INFORMATION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_tools": ["product_information_tool"],
    },

    # --- SIZE_INFORMATION (5-8) ---
    {
        "id": "TC-P1-05",
        "name": "Dimensions query (Primary Regression)",
        "query": "What are the dimensions of size M for P001?",
        "expected_intent": AgentIntent.SIZE_INFORMATION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
    },
    {
        "id": "TC-P1-06",
        "name": "Measurements request for size L",
        "query": "Show me the measurements of size L for P003",
        "expected_intent": AgentIntent.SIZE_INFORMATION.value,
        "expected_pid": "P003",
        "expected_size": "L",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
    },
    {
        "id": "TC-P1-07",
        "name": "Chest width specification inquiry",
        "query": "What is the chest width of size XL for P002?",
        "expected_intent": AgentIntent.SIZE_INFORMATION.value,
        "expected_pid": "P002",
        "expected_size": "XL",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
    },
    {
        "id": "TC-P1-08",
        "name": "General size chart request",
        "query": "Show me the size chart for P006",
        "expected_intent": AgentIntent.SIZE_INFORMATION.value,
        "expected_pid": "P006",
        "expected_size": "30",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
    },

    # --- FIT_RECOMMENDATION (9-13) ---
    {
        "id": "TC-P1-09",
        "name": "Fit inquiry with chest measurement",
        "query": "My chest is 40 inches. Will size M fit P001?",
        "expected_intent": AgentIntent.FIT_RECOMMENDATION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_meas": {"chest": 40.0},
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool"],
    },
    {
        "id": "TC-P1-10",
        "name": "Fit inquiry with chest and waist measurements",
        "query": "My chest is 38 inches and waist is 32 inches. Will P001 Size S fit?",
        "expected_intent": AgentIntent.FIT_RECOMMENDATION.value,
        "expected_pid": "P001",
        "expected_size": "S",
        "expected_meas": {"chest": 38.0, "waist": 32.0},
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool"],
    },
    {
        "id": "TC-P1-11",
        "name": "Metric cm-to-inches auto-conversion",
        "query": "My chest is 101.6 cm and waist is 86.4 cm. Will P001 Size M fit?",
        "expected_intent": AgentIntent.FIT_RECOMMENDATION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_meas": {"chest": 40.0, "waist": 34.0},
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool"],
    },
    {
        "id": "TC-P1-12",
        "name": "Fit question missing all measurements",
        "query": "Will P001 fit me comfortably?",
        "expected_intent": AgentIntent.FIT_RECOMMENDATION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "check_missing_info": True,
        "expected_tools": ["product_information_tool", "size_chart_tool"],
    },
    {
        "id": "TC-P1-13",
        "name": "Colloquial fit question (usually wear M)",
        "query": "I usually wear M. Is P002 comfortable for me?",
        "expected_intent": AgentIntent.FIT_RECOMMENDATION.value,
        "expected_pid": "P002",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
    },

    # --- RETURN_RISK_PREDICTION (14-16) ---
    {
        "id": "TC-P1-14",
        "name": "Predicted return probability inquiry",
        "query": "What is the predicted probability of return for P005?",
        "expected_intent": AgentIntent.RETURN_RISK_PREDICTION.value,
        "expected_pid": "P005",
        "expected_size": "30",
        "expected_tools": ["product_information_tool", "return_risk_prediction_tool", "return_history_analyzer_tool"],
    },
    {
        "id": "TC-P1-15",
        "name": "Colloquial return risk query",
        "query": "How risky is buying P007 in size S?",
        "expected_intent": AgentIntent.RETURN_RISK_PREDICTION.value,
        "expected_pid": "P007",
        "expected_size": "S",
        "expected_tools": ["product_information_tool", "return_risk_prediction_tool", "return_history_analyzer_tool"],
    },
    {
        "id": "TC-P1-16",
        "name": "ML prediction model signal inquiry",
        "query": "What is the ML return risk for P008?",
        "expected_intent": AgentIntent.RETURN_RISK_PREDICTION.value,
        "expected_pid": "P008",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "return_risk_prediction_tool", "return_history_analyzer_tool"],
    },

    # --- RETURN_HISTORY_ANALYSIS (17-19) ---
    {
        "id": "TC-P1-17",
        "name": "Why customers return inquiry",
        "query": "Why do customers return P004?",
        "expected_intent": AgentIntent.RETURN_HISTORY_ANALYSIS.value,
        "expected_pid": "P004",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "return_history_analyzer_tool"],
    },
    {
        "id": "TC-P1-18",
        "name": "Common return reasons inquiry",
        "query": "What are the common return reasons for P001?",
        "expected_intent": AgentIntent.RETURN_HISTORY_ANALYSIS.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "return_history_analyzer_tool"],
    },
    {
        "id": "TC-P1-19",
        "name": "Defect pattern inquiry",
        "query": "What are the defect patterns and customer complaints for P008?",
        "expected_intent": AgentIntent.RETURN_HISTORY_ANALYSIS.value,
        "expected_pid": "P008",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "return_history_analyzer_tool"],
    },

    # --- RETURN_POLICY (20-22) ---
    {
        "id": "TC-P1-20",
        "name": "General return policy inquiry",
        "query": "What is the return policy?",
        "expected_intent": AgentIntent.RETURN_POLICY.value,
        "expected_tools": ["rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-21",
        "name": "Refund policy inquiry",
        "query": "What is your refund policy and return window?",
        "expected_intent": AgentIntent.RETURN_POLICY.value,
        "expected_tools": ["rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-22",
        "name": "Can I return inquiry",
        "query": "Can I return this shirt if it does not fit?",
        "expected_intent": AgentIntent.RETURN_POLICY.value,
        "expected_tools": ["rag_retrieval_tool"],
    },

    # --- PURCHASE_DECISION (23-26) ---
    {
        "id": "TC-P1-23",
        "name": "Should I purchase without measurements",
        "query": "Should I purchase P001 in size M?",
        "expected_intent": AgentIntent.PURCHASE_DECISION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_tools": ["product_information_tool", "size_chart_tool", "return_risk_prediction_tool", "return_history_analyzer_tool", "rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-24",
        "name": "Should I buy with chest measurement (full reconciliation)",
        "query": "Should I buy P001 in size M? My chest is 40 inches.",
        "expected_intent": AgentIntent.PURCHASE_DECISION.value,
        "expected_pid": "P001",
        "expected_size": "M",
        "expected_meas": {"chest": 40.0},
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool", "return_risk_prediction_tool", "return_history_analyzer_tool", "rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-25",
        "name": "Is this a good purchase phrasing",
        "query": "Is P002 in size L a good purchase for my measurements?",
        "expected_intent": AgentIntent.PURCHASE_DECISION.value,
        "expected_pid": "P002",
        "expected_size": "L",
        "expected_tools": ["product_information_tool", "size_chart_tool", "return_risk_prediction_tool", "return_history_analyzer_tool", "rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-26",
        "name": "Purchase decision with numeric pants size",
        "query": "Should I buy P005 in size 32 with waist 34 inches?",
        "expected_intent": AgentIntent.PURCHASE_DECISION.value,
        "expected_pid": "P005",
        "expected_size": "32",
        "expected_meas": {"waist": 34.0},
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool", "return_risk_prediction_tool", "return_history_analyzer_tool", "rag_retrieval_tool"],
    },

    # --- GENERAL_PRODUCT_QUESTION (27-28) ---
    {
        "id": "TC-P1-27",
        "name": "Tell me more about product",
        "query": "Tell me more about P003",
        "expected_intent": AgentIntent.GENERAL_PRODUCT_QUESTION.value,
        "expected_pid": "P003",
        "expected_tools": ["product_information_tool", "rag_retrieval_tool"],
    },
    {
        "id": "TC-P1-28",
        "name": "What features should I consider",
        "query": "Which features should I consider for P009?",
        "expected_intent": AgentIntent.GENERAL_PRODUCT_QUESTION.value,
        "expected_pid": "P009",
        "expected_tools": ["product_information_tool", "rag_retrieval_tool"],
    },

    # --- UNKNOWN_INTENT / OUT-OF-DOMAIN / INVALID (29-32) ---
    {
        "id": "TC-P1-29",
        "name": "Out-of-domain general trivia",
        "query": "What is the capital of France?",
        "expected_intent": AgentIntent.UNKNOWN_INTENT.value,
        "expected_tools": [],
    },
    {
        "id": "TC-P1-30",
        "name": "Out-of-catalog luxury product",
        "query": "Do you sell Rolex watches or luxury jewelry?",
        "expected_intent": AgentIntent.UNKNOWN_INTENT.value,
        "expected_tools": [],
    },
    {
        "id": "TC-P1-31",
        "name": "Invalid product ID validation",
        "query": "Will size M fit for product P999?",
        "expected_intent": AgentIntent.UNKNOWN_INTENT.value,
        "expected_pid": "P999",
        "expected_tools": ["product_information_tool"],
    },
    {
        "id": "TC-P1-32",
        "name": "Cryptocurrency question",
        "query": "Can I pay using Bitcoin or cryptocurrency?",
        "expected_intent": AgentIntent.UNKNOWN_INTENT.value,
        "expected_tools": [],
    },
]

def run_suite():
    print("=" * 110)
    print("RETURN OR REGRET AI — PHASE 1.2 EXTENDED INTENT & ENTITY EVALUATION SUITE (32 TESTS)")
    print("=" * 110)

    results = []
    passed = 0

    header = f"{'ID':<10} | {'Expected Intent':<26} | {'Actual Intent':<26} | {'PID':<5} | {'Size':<4} | {'Tools':<5} | Status"
    print(header)
    print("-" * 110)

    for tc in EVAL_CASES:
        t_start = time.time()
        res = agent_controller.process_query(tc["query"])
        latency = (time.time() - t_start) * 1000

        actual_intent = res.get("intent", "")
        actual_pid = res.get("product_id")
        actual_size = res.get("selected_size")
        actual_tools = res.get("tools_executed", [])

        # Validations
        intent_ok = actual_intent == tc["expected_intent"]
        
        pid_ok = True
        if "expected_pid" in tc:
            pid_ok = actual_pid == tc["expected_pid"]

        size_ok = True
        if "expected_size" in tc:
            size_ok = actual_size == tc["expected_size"]

        tools_ok = True
        if "expected_tools" in tc:
            tools_ok = set(actual_tools) == set(tc["expected_tools"])

        meas_ok = True
        if "expected_meas" in tc:
            comp_items = res.get("measurement_comparison") or []
            for dim, expected_val in tc["expected_meas"].items():
                found = any(
                    item.get("dimension", "").lower() == dim.lower() and
                    abs(item.get("body_measurement", 0) - expected_val) <= 0.6
                    for item in comp_items
                )
                if not found:
                    meas_ok = False

        missing_ok = True
        if tc.get("check_missing_info"):
            missing_ok = len(res.get("missing_information", [])) > 0

        all_ok = intent_ok and pid_ok and size_ok and tools_ok and meas_ok and missing_ok

        if all_ok:
            passed += 1
            status_str = "PASS"
        else:
            status_str = "FAIL"
            reasons = []
            if not intent_ok: reasons.append(f"Intent {actual_intent} != {tc['expected_intent']}")
            if not pid_ok: reasons.append(f"PID {actual_pid} != {tc.get('expected_pid')}")
            if not size_ok: reasons.append(f"Size {actual_size} != {tc.get('expected_size')}")
            if not tools_ok: reasons.append(f"Tools {actual_tools} != {tc.get('expected_tools')}")
            if not meas_ok: reasons.append("Measurements extraction mismatch")
            if not missing_ok: reasons.append("Missing info not detected")
            status_str += f" ({', '.join(reasons)})"

        row = (
            f"{tc['id']:<10} | "
            f"{tc['expected_intent']:<26} | "
            f"{actual_intent:<26} | "
            f"{str(actual_pid or '-'):<5} | "
            f"{str(actual_size or '-'):<4} | "
            f"{'OK' if tools_ok else 'ERR':<5} | "
            f"{status_str}"
        )
        print(row)

        results.append({
            "id": tc["id"],
            "name": tc["name"],
            "query": tc["query"],
            "expected_intent": tc["expected_intent"],
            "actual_intent": actual_intent,
            "expected_pid": tc.get("expected_pid"),
            "actual_pid": actual_pid,
            "expected_size": tc.get("expected_size"),
            "actual_size": actual_size,
            "expected_tools": tc.get("expected_tools"),
            "actual_tools": actual_tools,
            "passed": all_ok,
            "latency_ms": round(latency, 1)
        })

    print("-" * 110)
    rate = (passed / len(EVAL_CASES)) * 100
    print(f"TOTAL: {passed}/{len(EVAL_CASES)} Passed ({rate:.1f}%)")
    print("=" * 110)

    # Save to json file
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intent_evaluation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases": len(EVAL_CASES),
            "passed_cases": passed,
            "pass_rate": rate,
            "results": results
        }, f, indent=2)
    print(f"Detailed results saved to: {out_path}")

    return passed == len(EVAL_CASES)

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
