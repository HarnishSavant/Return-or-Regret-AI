import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from agent.controller import agent_controller, MONITORING_LOG_PATH
from tools.agent_tools import (
    PRODUCTS_CACHE,
    ORDERS_DF,
    fit_calculator_tool,
    return_risk_prediction_tool,
    return_history_analyzer_tool,
    size_chart_tool,
    product_information_tool
)
from rag.retriever import rag_retriever

app = FastAPI(
    title="Return or Regret AI Backend",
    description="Intelligent Shopping Decision Agent with Predictive Return Risk & Product Defect Intelligence",
    version="1.0.0"
)

# Enable CORS for frontend Vite dev server & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for AI suggestions approval status
SUGGESTIONS_FILE = os.path.join(BASE_DIR, "data", "pending_suggestions.json")

def load_suggestions():
    if os.path.exists(SUGGESTIONS_FILE):
        try:
            with open(SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Initial realistic AI suggestions
    initial_suggestions = [
        {
            "id": "SUGG-001",
            "product_id": "P001",
            "product_name": "Heritage Oxford Slim Shirt",
            "category": "Shirts",
            "trigger_issue": "Customers frequently report tight shoulders (50% of returns cite shoulder/armhole tightness).",
            "severity": "High",
            "ai_suggested_action": "Add explicit shoulder-width measurement range and 'Athletic builds should size up' disclaimer to product sizing card.",
            "estimated_impact": "Reduces avoidable sizing returns by 18-24%.",
            "status": "pending",
            "created_at": "2026-11-10T14:30:00"
        },
        {
            "id": "SUGG-002",
            "product_id": "P004",
            "product_name": "Mercerized Ribbed Polo",
            "category": "T-Shirts",
            "trigger_issue": "Product page completely lacks an official size chart; description completeness is only 65%.",
            "severity": "Critical",
            "ai_suggested_action": "Publish complete garment chest and bicep sleeve band measurements table immediately.",
            "estimated_impact": "Reduces blind sizing guesswork; expected 30% reduction in returns.",
            "status": "pending",
            "created_at": "2026-11-10T15:10:00"
        },
        {
            "id": "SUGG-003",
            "product_id": "P008",
            "product_name": "Silk Satin Bias Cut Midi Dress",
            "category": "Dresses",
            "trigger_issue": "Bias-cut mulberry silk clings across hips, causing 40% of returns to cite 'Size Too Small' on hip seams.",
            "severity": "High",
            "ai_suggested_action": "Upload dynamic hip ease calculator and model proportion notes (e.g. Model is 5'9\", wearing Size S with 36\" hips).",
            "estimated_impact": "Decreases hip-constriction returns by 22%.",
            "status": "pending",
            "created_at": "2026-11-10T16:00:00"
        },
        {
            "id": "SUGG-004",
            "product_id": "P015",
            "product_name": "Chunky Cable-Knit Wool Cardigan",
            "category": "Outerwear",
            "trigger_issue": "No sleeve length measurements provided, leading to customer reports of oversized drape.",
            "severity": "Medium",
            "ai_suggested_action": "Add sleeve length and knit relaxation guidance after hanging.",
            "estimated_impact": "Reduces sizing discrepancy returns by 14%.",
            "status": "pending",
            "created_at": "2026-11-11T09:15:00"
        },
        {
            "id": "SUGG-005",
            "product_id": "P005",
            "product_name": "Selvedge Slim-Taper Denim Jeans",
            "category": "Jeans",
            "trigger_issue": "Initial raw denim waist rigidity leads customers to believe jeans are too small before break-in.",
            "severity": "Low",
            "ai_suggested_action": "Add 'Break-in Advisory: Raw denim waistband naturally loosens by 0.75\" after first week' note.",
            "estimated_impact": "Prevents premature day-one returns by 12%.",
            "status": "approved",
            "created_at": "2026-11-09T11:00:00"
        }
    ]
    with open(SUGGESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(initial_suggestions, f, indent=2)
    return initial_suggestions

def save_suggestions(suggestions):
    with open(SUGGESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(suggestions, f, indent=2)

# --- Schemas ---
class ChatRequest(BaseModel):
    query: str
    context_product_id: Optional[str] = None
    context_measurements: Optional[Dict[str, float]] = None

class RiskPredictRequest(BaseModel):
    product_id: str
    selected_size: str
    bracketing_order: bool = False
    discount_applied: float = 0.0

class FitRecommendRequest(BaseModel):
    product_id: str
    selected_size: str
    customer_measurements: Dict[str, float]

class SuggestionApprovalRequest(BaseModel):
    suggestion_id: str
    action: str = Field(..., description="'approve' or 'reject'")

# --- Endpoints ---

@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "Return or Regret AI Engine",
        "timestamp": datetime.now().isoformat(),
        "catalog_products_count": len(PRODUCTS_CACHE),
        "orders_analyzed_count": len(ORDERS_DF),
        "rag_chunks_indexed": len(rag_retriever.chunks),
        "llm_key_configured": bool(agent_controller.gemini_api_key)
    }

@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    total_orders = len(ORDERS_DF)
    returned_orders = ORDERS_DF[ORDERS_DF["returned"] == 1]
    total_returns = len(returned_orders)
    overall_return_rate = round((total_returns / total_orders) * 100, 1)

    # Avoidable returns: sizing, shoulder tightness, missing guide issues
    avoidable_reasons = ["Size Too Small", "Size Too Large", "Shoulder / Armhole Tightness"]
    avoidable_count = len(returned_orders[returned_orders["return_reason"].isin(avoidable_reasons)])
    avoidable_rate = round((avoidable_count / total_returns) * 100, 1) if total_returns > 0 else 0.0

    # High-risk products (historical return rate > 30%)
    high_risk_prods = [p for p in PRODUCTS_CACHE.values() if p.get("risk_category") == "High Risk"]

    # Category-wise breakdown
    cat_stats = ORDERS_DF.groupby("category")["returned"].agg(["count", "sum"]).reset_index()
    category_rates = [
        {
            "category": row["category"],
            "total_orders": int(row["count"]),
            "returns": int(row["sum"]),
            "return_rate": round((row["sum"] / row["count"]) * 100, 1) if row["count"] > 0 else 0.0
        }
        for _, row in cat_stats.iterrows()
    ]

    # Return reasons distribution
    reason_counts = returned_orders["return_reason"].value_counts().to_dict()
    reasons_distribution = [
        {"name": k, "value": int(v), "percentage": round((v / total_returns) * 100, 1)}
        for k, v in reason_counts.items()
    ]

    # Return trends over time (by month)
    ORDERS_DF["order_month"] = pd.to_datetime(ORDERS_DF["order_date"]).dt.strftime("%Y-%m")
    trend_df = ORDERS_DF.groupby("order_month")["returned"].agg(["count", "sum"]).reset_index()
    monthly_trends = [
        {
            "month": row["order_month"],
            "orders": int(row["count"]),
            "returns": int(row["sum"]),
            "return_rate": round((row["sum"] / row["count"]) * 100, 1)
        }
        for _, row in trend_df.iterrows()
    ]

    # Top high risk products list
    sorted_prods = sorted(PRODUCTS_CACHE.values(), key=lambda x: x.get("historical_return_rate", 0), reverse=True)
    top_high_risk = [
        {
            "product_id": p["product_id"],
            "name": p["name"],
            "category": p["category"],
            "price": p["price"],
            "return_rate": round(p.get("historical_return_rate", 0.0) * 100, 1),
            "risk_category": p.get("risk_category", "Medium Risk"),
            "known_quirk": p.get("known_fit_quirks", "None reported")
        }
        for p in sorted_prods[:5]
    ]

    # Recent monitoring logs
    logs = []
    if os.path.exists(MONITORING_LOG_PATH):
        try:
            with open(MONITORING_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)[:6]
        except Exception:
            logs = []

    return {
        "total_products": len(PRODUCTS_CACHE),
        "total_orders_analyzed": total_orders,
        "overall_return_rate": overall_return_rate,
        "avoidable_return_rate": avoidable_rate,
        "high_risk_product_count": len(high_risk_prods),
        "total_agent_interactions": len(logs) if logs else 14,
        "category_return_rates": category_rates,
        "return_reasons_distribution": reasons_distribution,
        "monthly_trends": monthly_trends,
        "top_high_risk_products": top_high_risk,
        "recent_agent_activity": logs,
        "synthetic_notice": "Demonstration data based on realistic apparel e-commerce distribution patterns."
    }

@app.get("/api/products")
def get_products(
    category: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    results = list(PRODUCTS_CACHE.values())

    if category and category != "All":
        results = [p for p in results if p["category"].lower() == category.lower()]

    if risk and risk != "All":
        results = [p for p in results if p.get("risk_category", "").lower() == risk.lower()]

    if search:
        s = search.lower()
        results = [
            p for p in results
            if s in p["name"].lower() or s in p["product_id"].lower() or s in p["material"].lower()
        ]

    return results

@app.get("/api/products/{product_id}")
def get_product_detail(product_id: str):
    pid = product_id.strip().upper()
    if pid not in PRODUCTS_CACHE:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")
    
    prod = PRODUCTS_CACHE[pid]
    history = return_history_analyzer_tool(pid)
    
    return {
        "product": prod,
        "history": history
    }

@app.post("/api/agent/chat")
def chat_with_agent(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    result = agent_controller.process_query(
        query=req.query,
        context_product_id=req.context_product_id,
        context_measurements=req.context_measurements
    )
    return result

@app.post("/api/risk/predict")
def predict_risk(req: RiskPredictRequest):
    result = return_risk_prediction_tool(
        product_id=req.product_id,
        selected_size=req.selected_size,
        bracketing_order=req.bracketing_order,
        discount_applied=req.discount_applied
    )
    return result

@app.post("/api/fit/recommend")
def recommend_fit(req: FitRecommendRequest):
    result = fit_calculator_tool(
        product_id=req.product_id,
        selected_size=req.selected_size,
        customer_measurements=req.customer_measurements
    )
    return result

@app.get("/api/insights")
def get_insights():
    suggestions = load_suggestions()
    
    # Calculate top fit complaints across catalog
    returned_orders = ORDERS_DF[ORDERS_DF["returned"] == 1]
    
    # Missing information audit
    missing_info_prods = [
        {
            "product_id": p["product_id"],
            "name": p["name"],
            "category": p["category"],
            "missing_item": "Size Chart" if not p["size_guide_available"] else "Detailed Shoulder/Sleeve Dimensions",
            "completeness_score": int(p["description_completeness"] * 100),
            "historical_return_rate": round(p.get("historical_return_rate", 0.0) * 100, 1)
        }
        for p in PRODUCTS_CACHE.values()
        if not p["size_guide_available"] or p["description_completeness"] < 0.75
    ]

    # Repeated fit problems
    fit_problem_prods = [
        {
            "product_id": p["product_id"],
            "name": p["name"],
            "category": p["category"],
            "fit_issue": p.get("known_fit_quirks", "None"),
            "risk_level": p.get("risk_category", "Medium")
        }
        for p in PRODUCTS_CACHE.values()
        if p.get("risk_category") == "High Risk"
    ]

    return {
        "ai_suggestions": suggestions,
        "missing_info_audit": missing_info_prods,
        "repeated_fit_problems": fit_problem_prods
    }

@app.post("/api/insights/approve")
def approve_suggestion(req: SuggestionApprovalRequest):
    suggestions = load_suggestions()
    updated = False
    for s in suggestions:
        if s["id"] == req.suggestion_id:
            s["status"] = "approved" if req.action == "approve" else "rejected"
            s["reviewed_at"] = datetime.now().isoformat()
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Suggestion ID not found.")
    save_suggestions(suggestions)
    return {"status": "success", "suggestion_id": req.suggestion_id, "new_status": s["status"]}

@app.get("/api/monitoring/logs")
def get_monitoring_logs():
    logs = []
    if os.path.exists(MONITORING_LOG_PATH):
        try:
            with open(MONITORING_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    # Calculate performance metrics
    total_calls = len(logs)
    avg_latency = round(sum(l.get("execution_time_ms", 0) for l in logs) / total_calls, 1) if total_calls > 0 else 0.0
    
    # Tool execution frequency
    tool_counts = {}
    for l in logs:
        for t in l.get("tools_called", []):
            tool_counts[t] = tool_counts.get(t, 0) + 1
            
    tool_frequency = [{"tool": k, "executions": v} for k, v in tool_counts.items()]

    return {
        "total_requests_logged": total_calls,
        "average_latency_ms": avg_latency,
        "tool_execution_frequency": tool_frequency,
        "recent_logs": logs[:50]
    }

@app.get("/api/model/metrics")
def get_model_metrics():
    metrics_path = os.path.join(BASE_DIR, "models", "model_metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(status_code=404, detail="Model metrics file not found. Please train models first.")
    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
