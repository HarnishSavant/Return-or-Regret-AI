# Machine Learning Model Benchmark & Evaluation

## 1. Benchmark Results on Holdout Test Set (N = 184)

The models were evaluated using Stratified 5-Fold Cross Validation on the training set and assessed on an unseen 20% holdout test set.

| Model Algorithm | 5-Fold CV F1 | Test Accuracy | Precision | Recall | Test F1-Score | ROC-AUC | PR-AUC | Selection |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Balanced)** | **0.5576** | **68.48%** | **0.4750** | **0.7037** | **0.5672** | **0.7520** | **0.5838** | **Selected Best** |
| **Random Forest (Depth 6)** | 0.4774 | 69.02% | 0.4776 | 0.5926 | 0.5289 | 0.7083 | 0.5509 | Benchmarked |
| **Gradient Boosting** | 0.3915 | 73.37% | 0.5676 | 0.3889 | 0.4615 | 0.6750 | 0.5044 | Benchmarked |

### Model Selection Rationale:
In return risk prevention, **Recall** is prioritized over pure accuracy because a false negative (failing to flag an avoidable return before purchase) results in high shipping and restocking costs. Logistic Regression achieved the highest Recall (70.37%), highest ROC-AUC (0.7520), and highest combined F1 score.

---

## 2. Confusion Matrix Analysis (Logistic Regression)

```
                     Predicted No Return (0)   Predicted Return (1)
Actual Kept (0)                88                       42
Actual Returned (1)            16                       38
```

- **True Negatives:** 88 items correctly identified as low return risk.
- **True Positives:** 38 items correctly flagged for return risk prior to checkout.
- **False Negatives:** 16 returns missed.
- **False Positives:** 42 items flagged with advisory guidance even though the customer kept the item (acceptable trade-off in preventive shopping assistants).

---

## 3. Top Feature Importances (Model Weights)

1. `product_size_return_rate` (0.2450): Historical return rate for the selected size.
2. `historical_return_rate` (0.2180): Baseline return frequency for the product.
3. `fit_type_Slim Fit` (0.1620): Slim silhouettes cause higher sizing friction.
4. `description_completeness` (0.1340): Incomplete specifications increase customer uncertainty.
5. `bracketing_order` (0.0980): Multi-size cart purchases strongly correlate with returns.
6. `size_guide_available` (0.0820): Products lacking published charts suffer elevated returns.

