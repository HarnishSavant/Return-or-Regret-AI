import json
import os
from typing import Dict, Any, Optional, List
import joblib
import pandas as pd
import numpy as np

from rag.retriever import rag_retriever

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Load products catalog
PRODUCTS_CACHE: Dict[str, Dict[str, Any]] = {}
with open(os.path.join(DATA_DIR, "products.json"), "r", encoding="utf-8") as f:
    _prods = json.load(f)
    for p in _prods:
        PRODUCTS_CACHE[p["product_id"]] = p

# Load orders dataset
ORDERS_DF = pd.read_csv(os.path.join(DATA_DIR, "orders_dataset.csv"))

# Load ML model
MODEL_PAYLOAD = None
try:
    MODEL_PAYLOAD = joblib.load(os.path.join(MODELS_DIR, "best_return_risk_model.joblib"))
except Exception as e:
    print(f"Warning: Could not load trained ML model: {e}")

# Tool 1: product_information_tool
def product_information_tool(product_id: str) -> Dict[str, Any]:
    """
    Retrieves complete verified product information, specifications, materials, and care instructions.
    """
    pid = product_id.strip().upper()
    if pid not in PRODUCTS_CACHE:
        return {
            "status": "error",
            "message": f"Product '{product_id}' was not found in catalog. Available product IDs: {', '.join(sorted(PRODUCTS_CACHE.keys()))}"
        }
    p = PRODUCTS_CACHE[pid]
    return {
        "status": "success",
        "product_id": p["product_id"],
        "name": p["name"],
        "category": p["category"],
        "price": p["price"],
        "fit_type": p["fit_type"],
        "material": p["material"],
        "available_sizes": p["sizes"],
        "size_guide_available": p["size_guide_available"],
        "description": p["description"],
        "care_instructions": p["care_instructions"],
        "known_fit_quirks": p.get("known_fit_quirks", "None reported"),
        "historical_return_rate": round(p.get("historical_return_rate", 0.0) * 100, 1),
        "risk_category": p.get("risk_category", "Unknown")
    }

# Tool 2: size_chart_tool
def size_chart_tool(product_id: str, size: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the authentic garment size chart dimensions (in inches).
    """
    pid = product_id.strip().upper()
    if pid not in PRODUCTS_CACHE:
        return {"status": "error", "message": f"Product '{product_id}' not found."}
    
    p = PRODUCTS_CACHE[pid]
    chart = p.get("size_chart", {})
    if not chart:
        return {
            "status": "warning",
            "message": f"Product {pid} does not have an official size chart published.",
            "size_guide_available": False
        }

    if size:
        s_upper = size.strip().upper()
        if s_upper in chart:
            return {
                "status": "success",
                "product_id": pid,
                "product_name": p["name"],
                "size": s_upper,
                "measurements_inches": chart[s_upper]
            }
        else:
            return {
                "status": "error",
                "message": f"Size '{size}' not found for product {pid}. Available sizes: {list(chart.keys())}",
                "available_sizes": list(chart.keys())
            }

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "fit_type": p["fit_type"],
        "full_size_chart": chart
    }

# Tool 3: fit_calculator_tool
def fit_calculator_tool(product_id: str, selected_size: str, customer_measurements: Dict[str, float]) -> Dict[str, Any]:
    """
    Compares customer body measurements against the exact garment dimensions to calculate ease tolerance and fit verdict.
    """
    pid = product_id.strip().upper()
    s_upper = selected_size.strip().upper()
    
    if pid not in PRODUCTS_CACHE:
        return {"status": "error", "message": f"Product '{product_id}' not found."}
    
    p = PRODUCTS_CACHE[pid]
    chart = p.get("size_chart", {})
    if s_upper not in chart:
        return {"status": "error", "message": f"Size '{selected_size}' not in size chart for {pid}. Available: {list(chart.keys())}"}

    garment_meas = chart[s_upper]
    fit_type = p["fit_type"]
    
    deltas = {}
    verdicts = {}
    tight_points = []
    loose_points = []
    
    # Analyze each provided measurement
    for dim, body_val in customer_measurements.items():
        dim_key = dim.lower().strip()
        if dim_key in garment_meas:
            g_val = garment_meas[dim_key]
            # Inseam / Length is direct comparison, not circumference ease
            if dim_key in ["inseam", "length", "foot_length_in"]:
                delta = round(g_val - body_val, 2)
                deltas[dim_key] = {"garment": g_val, "body": body_val, "difference": delta}
                if delta < -0.5:
                    tight_points.append(f"{dim_key} is too short by {abs(delta)} inches")
                elif delta > 2.0:
                    loose_points.append(f"{dim_key} is notably long (+{delta} inches)")
                verdicts[dim_key] = "Adequate" if abs(delta) <= 1.0 else ("Short" if delta < 0 else "Long")
            elif dim_key == "shoulder":
                # Shoulder width ease: typically needs 0.0 to 1.0 inch ease
                delta = round(g_val - body_val, 2)
                deltas[dim_key] = {"garment": g_val, "body": body_val, "ease": delta}
                if delta < -0.2:
                    tight_points.append(f"Shoulders too tight ({abs(delta)} inch deficit; pulls across yoke)")
                    verdicts[dim_key] = "Tight across shoulders"
                elif delta < 0.5:
                    verdicts[dim_key] = "Fitted / Tailored shoulder"
                else:
                    verdicts[dim_key] = "Comfortable shoulder ease"
            else:
                # Circumference measurements (Chest, Waist, Hip, Bust)
                ease = round(g_val - body_val, 2)
                deltas[dim_key] = {"garment": g_val, "body": body_val, "ease": ease}
                
                # Minimum ease thresholds based on fit type
                min_ease = 1.5 if fit_type == "Slim Fit" else (2.5 if fit_type == "Regular Fit" else 4.0)
                
                if ease < 0.5:
                    tight_points.append(f"{dim_key.title()} is severely constricted (only {ease}\" ease; button pull/chafing)")
                    verdicts[dim_key] = "Severely Tight"
                elif ease < min_ease:
                    tight_points.append(f"{dim_key.title()} has snug ease ({ease}\" vs recommended {min_ease}\" for {fit_type})")
                    verdicts[dim_key] = "Snug / Form-Fitting"
                elif ease > min_ease + 4.5:
                    loose_points.append(f"{dim_key.title()} has excessive excess fabric (+{ease}\" ease)")
                    verdicts[dim_key] = "Excessively Loose"
                else:
                    verdicts[dim_key] = "Optimal Comfort Fit"

    # Overall fit assessment
    overall_verdict = "Recommended Fit"
    confidence = 0.90
    recommendation = f"Size {s_upper} is well-proportioned for your measurements."

    if tight_points:
        overall_verdict = "High Return Risk — Likely Too Small"
        confidence = 0.92
        # Check next size if available
        sizes = p["sizes"]
        cur_idx = sizes.index(s_upper) if s_upper in sizes else -1
        next_size = sizes[cur_idx + 1] if cur_idx >= 0 and cur_idx + 1 < len(sizes) else None
        
        rec_next = f" Consider sizing up to {next_size} for adequate mobility." if next_size else ""
        recommendation = f"Size {s_upper} will likely feel tight on: {'; '.join(tight_points)}.{rec_next}"
    elif loose_points and not tight_points:
        overall_verdict = "Likely Too Roomy"
        confidence = 0.82
        recommendation = f"Size {s_upper} exhibits surplus ease: {'; '.join(loose_points)}. If you prefer a tailored profile, consider sizing down."

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "selected_size": s_upper,
        "fit_type": fit_type,
        "measurement_analysis": deltas,
        "dimension_verdicts": verdicts,
        "tight_areas": tight_points,
        "loose_areas": loose_points,
        "overall_verdict": overall_verdict,
        "confidence": confidence,
        "recommendation_summary": recommendation
    }

# Tool 4: return_risk_prediction_tool
def return_risk_prediction_tool(
    product_id: str,
    selected_size: str,
    bracketing_order: bool = False,
    discount_applied: float = 0.0
) -> Dict[str, Any]:
    """
    Executes the trained Scikit-Learn Machine Learning pipeline to predict return probability using pre-purchase features.
    """
    pid = product_id.strip().upper()
    s_upper = selected_size.strip().upper()

    if pid not in PRODUCTS_CACHE:
        return {"status": "error", "message": f"Product '{product_id}' not found."}

    p = PRODUCTS_CACHE[pid]
    
    # Calculate historical size-specific return rate from orders dataset
    size_orders = ORDERS_DF[(ORDERS_DF["product_id"] == pid) & (ORDERS_DF["selected_size"] == s_upper)]
    if not size_orders.empty:
        size_return_rate = float(size_orders["returned"].mean())
    else:
        size_return_rate = float(p.get("historical_return_rate", 0.20))

    hist_rate = float(p.get("historical_return_rate", 0.20))

    # Construct input feature DataFrame
    sample_df = pd.DataFrame([{
        "category": p["category"],
        "fit_type": p["fit_type"],
        "price": float(p["price"]),
        "size_guide_available": 1 if p["size_guide_available"] else 0,
        "description_completeness": float(p["description_completeness"]),
        "discount_applied": float(discount_applied),
        "bracketing_order": 1 if bracketing_order else 0,
        "historical_return_rate": hist_rate,
        "product_size_return_rate": size_return_rate
    }])

    predicted_prob = 0.25
    model_name = "Rule-based fallback"

    if MODEL_PAYLOAD and "pipeline" in MODEL_PAYLOAD:
        pipeline = MODEL_PAYLOAD["pipeline"]
        model_name = MODEL_PAYLOAD.get("best_model_name", "Trained ML Model")
        try:
            prob_arr = pipeline.predict_proba(sample_df)
            predicted_prob = float(prob_arr[0][1])
        except Exception as e:
            print(f"ML inference error: {e}")
            predicted_prob = hist_rate
    else:
        predicted_prob = hist_rate

    # Determine risk tier
    if predicted_prob >= 0.35:
        risk_level = "High"
    elif predicted_prob >= 0.20:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Identify contributing factors
    signals = []
    if size_return_rate > 0.30:
        signals.append(f"Size '{s_upper}' has an elevated historical return rate of {round(size_return_rate*100, 1)}%.")
    if not p["size_guide_available"]:
        signals.append("Missing official size guide increases sizing guesswork.")
    if p["description_completeness"] < 0.75:
        signals.append("Product description completeness is below catalog standard.")
    if bracketing_order:
        signals.append("Customer is purchasing multiple sizes (bracketing intention).")
    if p["fit_type"] == "Slim Fit":
        signals.append("Slim-fit garments exhibit 40% higher return variance due to shoulder/ribcage tightness.")

    if not signals:
        signals.append("Standard pre-purchase risk profile with verified dimensions.")

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "selected_size": s_upper,
        "predicted_return_probability": round(predicted_prob, 4),
        "predicted_return_percentage": round(predicted_prob * 100, 1),
        "risk_level": risk_level,
        "ml_model_used": model_name,
        "key_contributing_signals": signals,
        "pre_purchase_features": {
            "category": p["category"],
            "fit_type": p["fit_type"],
            "price": p["price"],
            "historical_return_rate": round(hist_rate * 100, 1),
            "size_return_rate": round(size_return_rate * 100, 1),
            "bracketing_order": bracketing_order
        }
    }

# Tool 5: return_history_analyzer_tool
def return_history_analyzer_tool(product_id: str) -> Dict[str, Any]:
    """
    Analyses historical return records, primary defect reasons, and customer feedback for the given product.
    """
    pid = product_id.strip().upper()
    if pid not in PRODUCTS_CACHE:
        return {"status": "error", "message": f"Product '{product_id}' not found."}

    p = PRODUCTS_CACHE[pid]
    p_orders = ORDERS_DF[ORDERS_DF["product_id"] == pid]
    
    if p_orders.empty:
        return {
            "status": "warning",
            "message": f"No historical order data available for {pid}.",
            "product_id": pid
        }

    total_orders = len(p_orders)
    returned_orders = p_orders[p_orders["returned"] == 1]
    total_returns = len(returned_orders)
    return_rate = round((total_returns / total_orders) * 100, 1) if total_orders > 0 else 0.0

    # Reasons breakdown
    reason_counts = returned_orders["return_reason"].value_counts().to_dict()
    reason_breakdown = [
        {"reason": reason, "count": int(count), "percentage": round((count / total_returns) * 100, 1)}
        for reason, count in reason_counts.items()
    ]

    # Size-level return rates
    size_stats = p_orders.groupby("selected_size")["returned"].agg(["count", "sum"]).reset_index()
    size_breakdown = [
        {
            "size": row["selected_size"],
            "orders": int(row["count"]),
            "returns": int(row["sum"]),
            "return_rate": round((row["sum"] / row["count"]) * 100, 1) if row["count"] > 0 else 0.0
        }
        for _, row in size_stats.iterrows()
    ]

    # Recent feedback snippets
    recent_feedback = returned_orders["customer_feedback"].dropna().tail(4).tolist()

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "total_orders_analyzed": total_orders,
        "total_returns": total_returns,
        "overall_return_rate": return_rate,
        "risk_category": p.get("risk_category", "Medium Risk"),
        "top_return_reasons": reason_breakdown,
        "size_performance": size_breakdown,
        "representative_customer_feedback": recent_feedback,
        "known_design_issues": p.get("known_fit_quirks", "None identified")
    }

# Tool 6: rag_retrieval_tool
def rag_retrieval_tool(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Performs semantic vector search across product specifications, size guides, fabric guides, and return policies.
    """
    matches = rag_retriever.search(query=query, top_k=top_k)
    citations = []
    for m in matches:
        citations.append({
            "source_document": m["source"],
            "section_title": m["title"],
            "similarity_score": m["score"],
            "snippet": m["content"]
        })

    return {
        "status": "success",
        "query": query,
        "total_results": len(citations),
        "citations": citations
    }

# Registry mapping
AVAILABLE_TOOLS = {
    "product_information_tool": product_information_tool,
    "size_chart_tool": size_chart_tool,
    "fit_calculator_tool": fit_calculator_tool,
    "return_risk_prediction_tool": return_risk_prediction_tool,
    "return_history_analyzer_tool": return_history_analyzer_tool,
    "rag_retrieval_tool": rag_retrieval_tool
}

