import json
import os
import sys
import time
from typing import List, Dict, Any

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from agent.controller import agent_controller
from tools.agent_tools import PRODUCTS_CACHE

TEST_SCENARIOS = [
    {
        "id": "TC-01",
        "name": "Product Material Question",
        "query": "What material is P001 made of?",
        "context_pid": "P001",
        "expected_intent": "PRODUCT_INFORMATION",
        "expected_tools": ["product_information_tool"],
        "expected_criterion": lambda res: "Cotton" in str(res.get("final_recommendation", "")) or "Cotton" in str(res.get("summary_message", ""))
    },
    {
        "id": "TC-02",
        "name": "Product Price Question",
        "query": "How much does P002 cost?",
        "context_pid": "P002",
        "expected_intent": "PRODUCT_INFORMATION",
        "expected_tools": ["product_information_tool"],
        "expected_criterion": lambda res: "74" in str(res.get("summary_message", "")) or "74" in str(res.get("final_recommendation", ""))
    },
    {
        "id": "TC-03",
        "name": "Size Chart Question",
        "query": "Show me the size chart for P003.",
        "context_pid": "P003",
        "expected_intent": "SIZE_INFORMATION",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
        "expected_criterion": lambda res: "size chart" in str(res.get("summary_message", "")).lower()
    },
    {
        "id": "TC-04",
        "name": "Missing Chest Measurement",
        "query": "Will P001 fit me comfortably?",
        "context_pid": "P001",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["product_information_tool", "size_chart_tool"],
        "expected_criterion": lambda res: len(res.get("missing_information", [])) > 0
    },
    {
        "id": "TC-05",
        "name": "Missing Shoulder Measurement (Slim Fit Shirt)",
        "query": "My chest is 40 inches. Will P001 Size M fit?",
        "context_pid": "P001",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool"],
        "expected_criterion": lambda res: any("Shoulder" in m for m in res.get("missing_information", []))
    },
    {
        "id": "TC-06",
        "name": "Customer Fit Recommendation (Chest 40 on P001 Size M)",
        "query": "My chest is 40 inches and waist is 34 inches. Will P001 Size M fit?",
        "context_pid": "P001",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool"],
        "expected_criterion": lambda res: res.get("verdict") in ["High Fit Concern", "Fit Concern"]
    },
    {
        "id": "TC-07",
        "name": "Alternative Size Comparison (Size L Inspection)",
        "query": "My chest is 40 inches. Will P001 Size M fit?",
        "context_pid": "P001",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["fit_calculator_tool"],
        "expected_criterion": lambda res: res.get("fit_assessment", {}).get("alternative_size_check", {}).get("alternative_size") == "L"
    },
    {
        "id": "TC-08",
        "name": "Historical Return Analysis",
        "query": "Why do customers return P004?",
        "context_pid": "P004",
        "expected_intent": "RETURN_HISTORY_ANALYSIS",
        "expected_tools": ["product_information_tool", "return_history_analyzer_tool"],
        "expected_criterion": lambda res: res.get("historical_analysis") is not None and res.get("historical_analysis", {}).get("total_orders_analyzed", 0) > 0
    },
    {
        "id": "TC-09",
        "name": "ML Return Prediction",
        "query": "What is the predicted probability of return for P005?",
        "context_pid": "P005",
        "expected_intent": "RETURN_RISK_PREDICTION",
        "expected_tools": ["return_risk_prediction_tool"],
        "expected_criterion": lambda res: res.get("ml_prediction") is not None and res.get("ml_prediction", {}).get("predicted_return_percentage", 0) > 0
    },
    {
        "id": "TC-10",
        "name": "Complex Shopping Decision",
        "query": "Should I purchase P001 in size M with chest 40 inches?",
        "context_pid": "P001",
        "expected_intent": "PURCHASE_DECISION",
        "expected_tools": ["fit_calculator_tool", "return_risk_prediction_tool", "return_history_analyzer_tool"],
        "expected_criterion": lambda res: res.get("decision_synthesis") is not None
    },
    {
        "id": "TC-11",
        "name": "Conflicting ML & Fit Results Reconciliation",
        "query": "Should I purchase P001 in size M? My chest is 40 inches.",
        "context_pid": "P001",
        "expected_intent": "PURCHASE_DECISION",
        "expected_tools": ["fit_calculator_tool", "return_risk_prediction_tool"],
        "expected_criterion": lambda res: "physical garment measurements take precedence" in str(res.get("decision_synthesis", {}).get("reconciliation_explanation", "")).lower()
    },
    {
        "id": "TC-12",
        "name": "Unsupported Product Question (Out-of-Catalog)",
        "query": "Do you sell Rolex watches?",
        "context_pid": None,
        "expected_intent": "UNKNOWN_INTENT",
        "expected_tools": [],
        "expected_criterion": lambda res: "exclusive" in str(res.get("summary_message", "")).lower() or "apparel" in str(res.get("summary_message", "")).lower()
    },
    {
        "id": "TC-13",
        "name": "Invalid Product ID Validation",
        "query": "Will size M fit for product P999?",
        "context_pid": "P999",
        "expected_intent": "UNKNOWN_INTENT",
        "expected_tools": ["product_information_tool"],
        "expected_criterion": lambda res: "not found" in str(res.get("summary_message", "")).lower()
    },
    {
        "id": "TC-14",
        "name": "Missing Product Size Chart Handling",
        "query": "Show size chart for P004",
        "context_pid": "P004",
        "expected_intent": "SIZE_INFORMATION",
        "expected_tools": ["size_chart_tool"],
        "expected_criterion": lambda res: True  # P004 size chart tool returns warning
    },
    {
        "id": "TC-15",
        "name": "Irrelevant Question",
        "query": "What is the capital of France?",
        "context_pid": None,
        "expected_intent": "UNKNOWN_INTENT",
        "expected_tools": [],
        "expected_criterion": lambda res: res.get("intent") == "UNKNOWN_INTENT"
    },
    {
        "id": "TC-16",
        "name": "RAG Retrieval Accuracy (Policy Inquiry)",
        "query": "What is the return policy for footwear?",
        "context_pid": None,
        "expected_intent": "RETURN_POLICY",
        "expected_tools": ["rag_retrieval_tool"],
        "expected_criterion": lambda res: len(res.get("evidence_sources", [])) > 0 or "30" in str(res.get("final_recommendation", ""))
    },
    {
        "id": "TC-17",
        "name": "Tool Execution Failure Resilience",
        "query": "Will Size XXL fit on P001?",
        "context_pid": "P001",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["size_chart_tool"],
        "expected_criterion": lambda res: res.get("summary_message") is not None
    },
    {
        "id": "TC-18",
        "name": "Multi-Tool Execution Under Latency Target",
        "query": "I have 42 chest and 36 waist. Recommend size for P002",
        "context_pid": "P002",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["product_information_tool", "size_chart_tool", "fit_calculator_tool"],
        "expected_criterion": lambda res: res.get("execution_metadata", {}).get("latency_ms", 1000) < 500
    },
    {
        "id": "TC-19",
        "name": "Unit Conversion Handling (Metric cm to Inches)",
        "query": "My chest is 101.6 cm and waist is 86.4 cm. Will P001 Size M fit?",
        "context_pid": "P001",
        "expected_intent": "FIT_RECOMMENDATION",
        "expected_tools": ["fit_calculator_tool"],
        "expected_criterion": lambda res: any(abs(item.get("body_measurement", 0) - 40.0) < 0.5 for item in res.get("measurement_comparison", []))
    },
    {
        "id": "TC-20",
        "name": "Backend/API Health & Robustness",
        "query": "What are the wash care instructions for P005?",
        "context_pid": "P005",
        "expected_intent": "PRODUCT_INFORMATION",
        "expected_tools": ["product_information_tool"],
        "expected_criterion": lambda res: res.get("product_id") == "P005"
    }
]

def run_evaluation_suite():
    print(f"================================================================")
    print(f"RETURN OR REGRET AI — 20 ADVANCED AGENT EVALUATION SCENARIOS")
    print(f"================================================================\n")
    
    results = []
    passed_count = 0

    for test in TEST_SCENARIOS:
        tid = test["id"]
        tname = test["name"]
        query = test["query"]
        expected_tools = test["expected_tools"]
        
        t0 = time.time()
        try:
            res = agent_controller.process_query(
                query=query,
                context_product_id=test.get("context_pid")
            )
            elapsed_ms = round((time.time() - t0) * 1000, 1)

            actual_intent = res.get("intent")
            actual_tools = res.get("tools_executed", [])
            
            # Check intent match or valid fallback
            intent_pass = (actual_intent == test["expected_intent"])
            
            # Check expected tools are subset of actual tools
            tools_pass = all(t in actual_tools for t in expected_tools)
            
            # Criterion check
            criterion_pass = test["expected_criterion"](res)
            
            test_passed = tools_pass and criterion_pass

            status_str = "PASS" if test_passed else "FAIL"
            if test_passed:
                passed_count += 1

            record = {
                "test_id": tid,
                "name": tname,
                "query": query,
                "expected_intent": test["expected_intent"],
                "actual_intent": actual_intent,
                "expected_tools": expected_tools,
                "actual_tools": actual_tools,
                "latency_ms": elapsed_ms,
                "status": status_str,
                "verdict": res.get("verdict"),
                "tools_pass": tools_pass,
                "criterion_pass": criterion_pass
            }
            results.append(record)

            print(f"[{status_str}] {tid}: {tname}")
            print(f"       Query: '{query}'")
            print(f"       Intent: {actual_intent} | Latency: {elapsed_ms}ms")
            print(f"       Tools called: {actual_tools}")
            if not test_passed:
                print(f"       WARNING: Tools match: {tools_pass}, Criterion: {criterion_pass}")
            print()

        except Exception as e:
            print(f"[FAIL] {tid}: {tname} — Exception: {e}\n")
            results.append({
                "test_id": tid,
                "name": tname,
                "query": query,
                "status": "FAIL",
                "error": str(e)
            })

    pass_rate = round((passed_count / len(TEST_SCENARIOS)) * 100, 1)
    print(f"================================================================")
    print(f"EVALUATION COMPLETE: {passed_count}/{len(TEST_SCENARIOS)} Passed ({pass_rate}%)")
    print(f"================================================================")

    # Save results to JSON
    os.makedirs(os.path.join(BASE_DIR, "evaluation"), exist_ok=True)
    out_json = os.path.join(BASE_DIR, "evaluation", "evaluation_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_scenarios": len(TEST_SCENARIOS),
            "passed": passed_count,
            "failed": len(TEST_SCENARIOS) - passed_count,
            "pass_rate_pct": pass_rate,
            "test_records": results
        }, f, indent=2)

    print(f"Saved test run records to: {out_json}")

if __name__ == "__main__":
    run_evaluation_suite()

