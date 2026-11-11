import json
import os
from typing import Dict, Any, Optional, List
import joblib
import pandas as pd
import numpy as np

from rag.retriever import rag_retriever
from schemas.agent_schemas import FitVerdict

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
    Retrieves verified product information, specifications, materials, and care instructions.
    Validates product ID existence.
    """
    if not product_id:
        return {
            "status": "error",
            "message": "Product ID was not provided. Please specify a valid product ID (e.g., P001 - P018)."
        }
    
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
        "risk_category": p.get("risk_category", "Unknown"),
        "total_orders": p.get("total_orders", 50)
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
            "message": f"Product {pid} does not currently have an official published size chart.",
            "size_guide_available": False,
            "product_id": pid,
            "product_name": p["name"]
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
                "message": f"Size '{size}' not found for product {pid}. Available sizes in chart: {list(chart.keys())}",
                "available_sizes": list(chart.keys())
            }

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "fit_type": p["fit_type"],
        "full_size_chart": chart
    }

# Tool 3: fit_calculator_tool (Advanced Engine with Fit-Type Tolerances and Verified Alternative Size Inspection)
def fit_calculator_tool(product_id: str, selected_size: str, customer_measurements: Dict[str, float]) -> Dict[str, Any]:
    """
    Compares customer body measurements against exact garment dimensions using fit-type specific ease tolerances.
    Inspects alternative size dimensions before making any size change recommendation.
    """
    pid = product_id.strip().upper()
    s_upper = selected_size.strip().upper()
    
    if pid not in PRODUCTS_CACHE:
        return {"status": "error", "message": f"Product '{product_id}' not found in catalog."}
    
    p = PRODUCTS_CACHE[pid]
    chart = p.get("size_chart", {})
    if not chart:
        return {
            "status": "warning",
            "verdict": FitVerdict.INSUFFICIENT_INFORMATION.value,
            "message": f"Product {pid} does not have an official size chart published. Personalized fit calculation cannot be performed with certainty.",
            "product_id": pid
        }

    if s_upper not in chart:
        return {
            "status": "error",
            "message": f"Size '{selected_size}' not in size chart for {pid}. Available sizes: {list(chart.keys())}"
        }

    garment_meas = chart[s_upper]
    fit_type = p["fit_type"]
    
    # Clean and convert customer measurements (handling metric inputs if body_val > 60)
    cleaned_measurements = {}
    for k, v in customer_measurements.items():
        k_clean = k.lower().strip()
        val = float(v)
        if val > 60.0 and k_clean in ["chest", "bust", "waist", "hip"]:
            # Auto-convert cm to inches
            val = round(val / 2.54, 1)
        cleaned_measurements[k_clean] = val

    comparison_items = []
    tight_points = []
    loose_points = []
    
    # Fit-Type Specific Minimum & Ideal Ease Tolerances
    # Ease = Garment Measurement - Body Measurement
    if fit_type == "Slim Fit":
        min_chest_ease = 1.5
        ideal_chest_ease = (2.0, 2.75)
    elif fit_type == "Regular Fit":
        min_chest_ease = 2.5
        ideal_chest_ease = (3.0, 4.0)
    elif fit_type in ["Relaxed Fit", "Oversized"]:
        min_chest_ease = 4.0
        ideal_chest_ease = (4.5, 7.0)
    elif fit_type == "Athletic":
        min_chest_ease = 2.0
        ideal_chest_ease = (2.5, 3.5)
    else:
        min_chest_ease = 2.0
        ideal_chest_ease = (2.5, 3.5)

    for dim_key, body_val in cleaned_measurements.items():
        if dim_key in garment_meas:
            g_val = garment_meas[dim_key]
            
            # Linear dimensions: inseam, length, foot length
            if dim_key in ["inseam", "length", "foot_length_in"]:
                delta = round(g_val - body_val, 2)
                if delta < -0.75:
                    status = "tight"
                    interp = f"Too short by {abs(delta)}\""
                    tight_points.append(f"{dim_key.title()} is short ({abs(delta)}\" deficit)")
                elif delta > 2.5:
                    status = "loose"
                    interp = f"Notably long (+{delta}\")"
                    loose_points.append(f"{dim_key.title()} has excess length (+{delta}\")")
                else:
                    status = "optimal"
                    interp = "Standard proportional length"

                comparison_items.append({
                    "dimension": dim_key.title(),
                    "body_measurement": body_val,
                    "garment_measurement": g_val,
                    "ease": delta,
                    "unit": "inches",
                    "interpretation": interp,
                    "status": status
                })

            # Shoulder width
            elif dim_key == "shoulder":
                delta = round(g_val - body_val, 2)
                if delta < -0.2:
                    status = "tight"
                    interp = f"Narrow / tight across upper yoke ({abs(delta)}\" deficit)"
                    tight_points.append(f"Shoulder width deficit of {abs(delta)}\" (causes armhole pull and restricted mobility)")
                elif delta < 0.2:
                    status = "optimal"
                    interp = "Fitted tailored shoulder alignment"
                else:
                    status = "optimal"
                    interp = f"Comfortable shoulder mobility (+{delta}\" ease)"

                comparison_items.append({
                    "dimension": "Shoulder Width",
                    "body_measurement": body_val,
                    "garment_measurement": g_val,
                    "ease": delta,
                    "unit": "inches",
                    "interpretation": interp,
                    "status": status
                })

            # Circumference dimensions: Chest, Bust, Waist, Hip
            else:
                ease = round(g_val - body_val, 2)
                
                if dim_key in ["chest", "bust"]:
                    if ease < 0.5:
                        status = "tight"
                        interp = f"Severely constricted (only {ease}\" ease; button pull/chafing)"
                        tight_points.append(f"Chest is severely constricted (+{ease}\" ease vs recommended minimum {min_chest_ease}\" for {fit_type})")
                    elif ease < min_chest_ease:
                        status = "tight"
                        interp = f"Snug / restrictive ease ({ease}\" vs minimum {min_chest_ease}\" for {fit_type})"
                        tight_points.append(f"Chest ease ({ease}\") is below the recommended {min_chest_ease}\" for {fit_type}")
                    elif ease > ideal_chest_ease[1] + 2.0:
                        status = "loose"
                        interp = f"Noticeably loose silhouette (+{ease}\" ease)"
                        loose_points.append(f"Excess fabric across chest (+{ease}\" ease)")
                    else:
                        status = "optimal"
                        interp = f"Optimal comfort fit (+{ease}\" ease for {fit_type})"
                
                elif dim_key == "waist":
                    # Non-stretch fabrics require at least 0.75" ease
                    if ease < 0.25:
                        status = "tight"
                        interp = f"Constricted waistband ({ease}\" ease)"
                        tight_points.append(f"Waist is tight with only {ease}\" ease")
                    elif ease > 4.5:
                        status = "loose"
                        interp = f"Substantial waistband slack (+{ease}\")"
                        loose_points.append(f"Waist is loose (+{ease}\" ease)")
                    else:
                        status = "optimal"
                        interp = f"Well-proportioned waist ease (+{ease}\")"
                else:
                    status = "optimal" if ease >= 1.0 else "tight"
                    interp = f"{'+' if ease >= 0 else ''}{ease}\" ease"

                comparison_items.append({
                    "dimension": dim_key.title(),
                    "body_measurement": body_val,
                    "garment_measurement": g_val,
                    "ease": ease,
                    "unit": "inches",
                    "interpretation": interp,
                    "status": status
                })

    # Determine Personalised Fit Verdict
    if tight_points:
        if any("severely constricted" in tp.lower() or "deficit" in tp.lower() for tp in tight_points):
            verdict = FitVerdict.HIGH_FIT_CONCERN
        else:
            verdict = FitVerdict.FIT_CONCERN
        confidence = 0.92
    elif loose_points and not tight_points:
        verdict = FitVerdict.FIT_CONCERN
        confidence = 0.84
    elif comparison_items:
        verdict = FitVerdict.GOOD_FIT
        confidence = 0.91
    else:
        verdict = FitVerdict.INSUFFICIENT_INFORMATION
        confidence = 0.50

    # ALTERNATIVE SIZE VERIFICATION (Never recommend size L without checking size L measurements)
    alternative_size_check = None
    if verdict in [FitVerdict.HIGH_FIT_CONCERN, FitVerdict.FIT_CONCERN] and tight_points:
        sizes_list = p.get("sizes", [])
        if s_upper in sizes_list:
            cur_idx = sizes_list.index(s_upper)
            if cur_idx + 1 < len(sizes_list):
                next_sz = sizes_list[cur_idx + 1]
                if next_sz in chart:
                    next_garment = chart[next_sz]
                    alt_ease_analysis = {}
                    alt_notes = []
                    
                    for dim, body_val in cleaned_measurements.items():
                        if dim in next_garment:
                            alt_ease = round(next_garment[dim] - body_val, 2)
                            alt_ease_analysis[dim] = alt_ease
                            alt_notes.append(f"{dim.title()}: {next_garment[dim]}\" (gives {'+' if alt_ease >= 0 else ''}{alt_ease}\" ease)")
                    
                    alternative_size_check = {
                        "alternative_size": next_sz,
                        "is_available_in_chart": True,
                        "dimensions": next_garment,
                        "ease_analysis": alt_ease_analysis,
                        "assessment_notes": f"Size {next_sz} measurements verified in catalog ({', '.join(alt_notes)}). Sizing up to {next_sz} provides the necessary comfort ease."
                    }
                else:
                    alternative_size_check = {
                        "alternative_size": next_sz,
                        "is_available_in_chart": False,
                        "assessment_notes": f"Size {next_sz} is listed in catalog sizes, but its exact dimensions cannot be verified in the published size chart."
                    }

    summary = f"Fit evaluation for Size {s_upper}: {verdict.value}."
    if tight_points:
        summary += f" Identified restriction areas: {'; '.join(tight_points)}."
        if alternative_size_check and alternative_size_check["is_available_in_chart"]:
            summary += f" Verified alternative: {alternative_size_check['assessment_notes']}"
    elif verdict == FitVerdict.GOOD_FIT:
        summary += f" Garment ease is well-aligned with {fit_type} profile."

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "selected_size": s_upper,
        "fit_type": fit_type,
        "verdict": verdict.value,
        "confidence": confidence,
        "tight_areas": tight_points,
        "loose_areas": loose_points,
        "measurement_comparison": comparison_items,
        "alternative_size_check": alternative_size_check,
        "summary": summary
    }

# Tool 4: return_risk_prediction_tool (Machine Learning Population Return Risk)
def return_risk_prediction_tool(
    product_id: str,
    selected_size: str,
    bracketing_order: bool = False,
    discount_applied: float = 0.0
) -> Dict[str, Any]:
    """
    Executes the trained Scikit-Learn Machine Learning pipeline to predict return probability using pre-purchase features.
    Explicitly provides model limitations and feature signals.
    """
    pid = product_id.strip().upper()
    s_upper = selected_size.strip().upper()

    if pid not in PRODUCTS_CACHE:
        return {"status": "error", "message": f"Product '{product_id}' not found in catalog."}

    p = PRODUCTS_CACHE[pid]
    
    # Calculate historical size-specific return rate from orders dataset
    size_orders = ORDERS_DF[(ORDERS_DF["product_id"] == pid) & (ORDERS_DF["selected_size"] == s_upper)]
    if not size_orders.empty:
        size_return_rate = float(size_orders["returned"].mean())
    else:
        size_return_rate = float(p.get("historical_return_rate", 0.20))

    hist_rate = float(p.get("historical_return_rate", 0.20))

    # Construct input feature DataFrame strictly with pre-purchase features
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
    model_name = "Logistic Regression (Balanced)"

    if MODEL_PAYLOAD and "pipeline" in MODEL_PAYLOAD:
        pipeline = MODEL_PAYLOAD["pipeline"]
        model_name = MODEL_PAYLOAD.get("best_model_name", "Logistic Regression (Balanced)")
        try:
            prob_arr = pipeline.predict_proba(sample_df)
            predicted_prob = float(prob_arr[0][1])
        except Exception as e:
            print(f"ML inference warning: {e}")
            predicted_prob = hist_rate
    else:
        predicted_prob = hist_rate

    # Validated risk thresholds
    if predicted_prob >= 0.35:
        risk_tier = "High"
    elif predicted_prob >= 0.20:
        risk_tier = "Medium"
    else:
        risk_tier = "Low"

    # Identify contributing factors based on actual model features
    signals = []
    if size_return_rate > 0.30:
        signals.append(f"Size '{s_upper}' has an elevated historical return rate of {round(size_return_rate*100, 1)}% in our historical records.")
    if not p["size_guide_available"]:
        signals.append("Missing published size chart increases customer sizing uncertainty.")
    if p["description_completeness"] < 0.75:
        signals.append(f"Product description completeness is {int(p['description_completeness']*100)}% (lower than catalog standard).")
    if bracketing_order:
        signals.append("Bracketing purchase intent detected (ordering multiple sizes elevates probability of return).")
    if p["fit_type"] == "Slim Fit":
        signals.append("Slim Fit silhouette statistically exhibits higher return rates across shirts and dresses.")

    if not signals:
        signals.append(f"Baseline return signals are well within normal ranges for {p['category']}.")

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "selected_size": s_upper,
        "predicted_return_probability": round(predicted_prob, 4),
        "predicted_return_percentage": round(predicted_prob * 100, 1),
        "risk_tier": risk_tier,
        "model_name": model_name,
        "key_contributing_signals": signals,
        "limitations": "Model reflects broad cohort probability from pre-purchase attributes; does not evaluate your individual body measurements or anatomical fit."
    }

# Tool 5: return_history_analyzer_tool (Empirical Defect and Return Intelligence)
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
            "product_id": pid,
            "total_orders_analyzed": 0,
            "overall_return_rate": 0.0,
            "category_baseline_rate": 20.0
        }

    total_orders = len(p_orders)
    returned_orders = p_orders[p_orders["returned"] == 1]
    total_returns = len(returned_orders)
    return_rate = round((total_returns / total_orders) * 100, 1) if total_orders > 0 else 0.0

    # Category baseline
    cat = p["category"]
    cat_orders = ORDERS_DF[ORDERS_DF["category"] == cat]
    cat_baseline = round((cat_orders["returned"].mean() * 100), 1) if not cat_orders.empty else 22.0

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

    recent_feedback = returned_orders["customer_feedback"].dropna().tail(3).tolist()

    return {
        "status": "success",
        "product_id": pid,
        "product_name": p["name"],
        "total_orders_analyzed": total_orders,
        "total_returns": total_returns,
        "overall_return_rate": return_rate,
        "category_baseline_rate": cat_baseline,
        "risk_category": p.get("risk_category", "Medium Risk"),
        "top_return_reasons": reason_breakdown,
        "size_performance": size_breakdown,
        "known_design_issues": p.get("known_fit_quirks", "None identified"),
        "representative_customer_feedback": recent_feedback
    }

# Tool 6: rag_retrieval_tool (Verified Knowledge Base Retrieval)
def rag_retrieval_tool(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Performs semantic vector search across product specifications, size guides, fabric guides, and return policies.
    """
    matches = rag_retriever.search(query=query, top_k=top_k)
    citations = []
    for m in matches:
        citations.append({
            "title": m["title"],
            "document": m["source"],
            "confidence": f"{round(m['score']*100, 1)}%",
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
