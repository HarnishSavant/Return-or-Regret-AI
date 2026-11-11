# Machine Learning Pipeline Validation & Audit

## 1. Zero Data Leakage Verification
In predictive e-commerce, the most frequent failure mode is **target leakage**—training models on information produced after the order event (e.g. carrier return scans, refund transactions, customer return comments).

### Audit Check:
- **Target Variable ($y$):** `returned` (binary: 0 for kept, 1 for returned).
- **Features Used ($X$):**
  1. `category` (Apparel subcategory)
  2. `fit_type` (Slim Fit, Regular Fit, Relaxed Fit, Oversized, Athletic)
  3. `price` (Garment price)
  4. `size_guide_available` (Binary: 0 or 1)
  5. `description_completeness` (Continuous score: 0.0 to 1.0)
  6. `discount_applied` (Promotional markdown rate: 0.0 to 0.40)
  7. `bracketing_order` (Binary: simultaneous multiple size purchase)
  8. `historical_return_rate` (Product-level prior empirical return rate)
  9. `product_size_return_rate` (Size-specific prior empirical return rate)

**Audit Result:** Confirmed 100% pre-purchase features. Outcome fields (`return_reason`, `customer_feedback`) are strictly excluded from training inputs.

---

## 2. Model Benchmarking & Selection
Models trained using 5-Fold Stratified Cross-Validation on training set (N=736) and evaluated on independent holdout test set (N=184):

| Algorithm | 5-Fold CV F1 | Test Accuracy | Precision | Recall | Test F1 | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Balanced)** | **0.5576** | **68.48%** | **0.4750** | **0.7037** | **0.5672** | **0.7520** | **0.5838** |
| **Random Forest (Depth 6)** | 0.4774 | 69.02% | 0.4776 | 0.5926 | 0.5289 | 0.7083 | 0.5509 |
| **Gradient Boosting** | 0.3915 | 73.37% | 0.5676 | 0.3889 | 0.4615 | 0.6750 | 0.5044 |

### Metric Prioritization:
For return prevention, **Recall** is prioritized over Precision. Missing a true return (False Negative) costs the merchant shipping, handling, and potential inventory depreciation. Logistic Regression achieves 70.37% Recall and the highest ROC-AUC (0.7520).

---

## 3. Global Model Feature Weights

```
product_size_return_rate:  0.2450
historical_return_rate:    0.2180
fit_type_Slim Fit:         0.1620
description_completeness:  0.1340
bracketing_order:          0.0980
size_guide_available:      0.0820
discount_applied:          0.0610
```

Notice: These represent **global model-level weights** across the dataset. The Decision Synthesis Engine clearly explains that these cohort weights do not supersede individual anatomical measurements.
