# Machine Learning & AI Agent Methodology

## 1. Zero Data Leakage Principle
A critical flaw in naive e-commerce return prediction is target leakage—training on variables that only exist after purchase (e.g. return shipping status, customer return comments, or refund reason).

In **Return or Regret AI**, models are strictly restricted to **pre-purchase signals** available at the exact moment a customer is browsing or adding to bag:
- `category` (Shirts, Jeans, T-Shirts, Dresses, Outerwear, Footwear, Activewear)
- `fit_type` (Slim Fit, Regular Fit, Relaxed Fit, Oversized, Athletic)
- `price` (Continuous)
- `size_guide_available` (Binary: 0 or 1)
- `description_completeness` (Continuous 0.0 to 1.0)
- `discount_applied` (Continuous 0.0 to 0.40)
- `bracketing_order` (Binary: customer ordering multiple sizes)
- `historical_return_rate` (Product-level historical return rate)
- `product_size_return_rate` (Specific size historical return rate)

---

## 2. Model Training Pipeline
The ML pipeline in `backend/ml/train_models.py` benchmarks three candidate classifiers:
1. **Logistic Regression (with L2 Regularization & Class Weight Balancing)**
2. **Random Forest Classifier (Ensemble of 150 Decision Trees with Depth=6)**
3. **Gradient Boosting Classifier (120 Estimators with Learning Rate=0.08)**

### Preprocessing & Splitting:
- **Stratified Train/Test Split:** 80% Training (736 samples), 20% Holdout Test (184 samples).
- **ColumnTransformer:**
  - Numeric features: `StandardScaler()`
  - Categorical features: `OneHotEncoder(handle_unknown='ignore')`
- **5-Fold Stratified Cross-Validation:** Computed across the training set to prevent optimistic overfitting.

---

## 3. RAG Knowledge Engine & Vector Retrieval
- **Knowledge Base Source Files:**
  - `knowledge_base/return_policy.md`
  - `knowledge_base/sizing_and_measurement_guide.md`
  - `knowledge_base/materials_and_fabric_care.md`
  - `knowledge_base/product_catalog_and_fit_notes.md`
- **Chunking Strategy:** Markdown header-aware semantic splitting.
- **Vector Index:** TF-IDF with sublinear term-frequency scaling and cosine similarity scoring.
- **Retrieval Threshold:** Minimum cosine similarity threshold (0.05) to eliminate non-relevant hallucinations.

