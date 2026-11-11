# Return or Regret AI — Intelligent Shopping Decision Agent

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikitlearn)](https://scikit-learn.org)
[![TailwindCSS](https://img.shields.io/badge/Style-Tailwind%20CSS-06B6D4.svg?logo=tailwindcss)](https://tailwindcss.com)

**Return or Regret AI** is a production-style full-stack web application designed to reduce avoidable e-commerce product returns by providing intelligent, data-backed fit and sizing guidance *before* purchase.

> **Core Philosophy: Fix the product page, not the customer.**  
> Customers are never penalized for sizing uncertainty. Avoidable returns are addressed at the root cause by resolving specification gaps and offering personalized ease calculations.

---

## 🚀 Key Modules & Pages

1. **Executive Dashboard (`/dashboard`)**
   - KPI metrics: Return Rate, Avoidable Return Rate (~68%), High-Risk Product Count.
   - Monthly order and return volume area charts.
   - Return reason distribution donut chart.
   - Category-wise return rate benchmarks.
   - Real-time high-risk product watchlist with known design quirks.

2. **AI Shopping Assistant (`/assistant`) — Flagship Feature**
   - Multi-tool Python decision agent.
   - Real-time garment dimension inspection vs customer body measurements.
   - Transparent tool execution accordion displaying tool parameters and observation outputs.
   - Grounded citations from official return policy, fabric care, and size guide documents.
   - Dual-engine support: Live LLM (Gemini 1.5 Flash) or Deterministic Academic Demonstration Engine.

3. **Product Intelligence (`/products`)**
   - 18 realistic apparel styles across Shirts, T-Shirts, Jeans, Pants, Dresses, Outerwear, Footwear, and Activewear.
   - Interactive search, category filters, and risk tier filters.
   - Modal inspection for garment size charts (inches) and care instructions.

4. **Return Risk Analysis (`/risk-analysis`)**
   - Pre-purchase parameter simulator (Bracketing intention, promotional discount).
   - Live inference via trained Scikit-Learn classification pipeline.
   - Visual probability meter and contributing risk factor breakdown.

5. **Product Insights (`/insights`)**
   - AI-generated product page improvements derived from return clusters.
   - Human approval workflow (Approve / Dismiss buttons connected to backend).
   - Missing information audit and repeated fit complaints index.

6. **System Monitoring (`/monitoring`)**
   - Machine Learning benchmark: Logistic Regression vs Random Forest vs Gradient Boosting.
   - 5-Fold Cross Validation F1, Precision, Recall, ROC-AUC, PR-AUC, and Confusion Matrix.
   - Feature importances chart.
   - Real logged agent execution telemetry (query, intent, tools called, latency in ms).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn, Pandas, NumPy |
| **AI / ML** | Scikit-Learn (Logistic Regression, Random Forest, Gradient Boosting), TF-IDF RAG Vector Store, Joblib |
| **Agent Controller** | Multi-tool Python controller with 6 isolated, registered tools |

---

## 📦 Python Registered Tools

| Tool Name | Responsibility |
| :--- | :--- |
| `product_information_tool` | Retrieves verified fabric composition, care guide, and known fit quirks. |
| `size_chart_tool` | Extracts official garment measurements (chest, waist, shoulder, hip, length). |
| `fit_calculator_tool` | Computes ease tolerance ($\text{Garment} - \text{Body}$) and flags constriction spots. |
| `return_risk_prediction_tool` | Executes the trained Scikit-Learn pipeline using pre-purchase features. |
| `return_history_analyzer_tool` | Analyzes historical return rates, size-specific performance, and return reasons. |
| `rag_retrieval_tool` | Performs vector search over policy, sizing, and fabric knowledge base documents. |

---

## 🏃 Running the Application Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# (Optional) Retrain ML models or regenerate synthetic data
python scripts/generate_data.py
python ml/train_models.py

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend API will be running at `http://127.0.0.1:8000`.  
Interactive Swagger docs available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend will be available at `http://localhost:5173`.

---

## 🎓 Academic Viva & Demonstration Talking Points

1. **Why not just build a standard chatbot?**  
   Standard LLMs hallucinate garment measurements and invent return probabilities. Our agent architecture enforces deterministic tool execution in Python (`size_chart_tool`, `fit_calculator_tool`, `return_risk_prediction_tool`). The LLM or rule engine is strictly constrained by tool observations.

2. **How is Data Leakage prevented?**  
   Target separation is strictly preserved. Features used in model training and inference only include pre-purchase attributes (fit silhouette, size guide availability, price, discount, bracketing). Post-purchase outcome variables (return reasons, refund approvals) are never used as model inputs.

3. **Why did Logistic Regression outperform tree ensembles on this task?**  
   Due to class imbalance (~29.5% return rate), the balanced class-weighting in Logistic Regression achieved higher sensitivity (Recall = 70.37% vs 38.89% for Gradient Boosting), ensuring that high-risk sizing mismatch cases are not missed.

---

## 📄 License
Academic Demonstration Project. Built for portfolio & evaluation.

