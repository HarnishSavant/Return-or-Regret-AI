# RETURN OR REGRET AI — Comprehensive Viva Q&A Guide

**Programme:** M.Sc. Data Science & Spatial Analytics  
**Course:** Mini Project – Artificial Intelligence (2026–2027)  
**Institute:** Symbiosis Institute of Geoinformatics (SIG)

This document contains 30 rigorous, implementation-grounded Viva examination questions and detailed technical answers to prepare the candidate for external evaluation.

---

## SECTION 1: PROBLEM STATEMENT & DOMAIN UNDERSTANDING

### Q1: Why did you choose the e-commerce fashion return problem for an Artificial Intelligence project?
**Answer:**
Fashion e-commerce suffers from an average return rate of approximately 25% to 30%, which is nearly three times higher than brick-and-mortar retail. Over 67% of these returns stem directly from preventable sizing, fit, and tactile mismatches. Traditional e-commerce platforms approach this as a post-purchase logistics problem—charging return shipping fees or restocking penalties. 

We chose this problem because it represents a high-impact, pre-purchase decision problem where Artificial Intelligence can intervene proactively. By combining machine learning risk scoring, mathematical physical fit validation, and agentic multi-tool reasoning before payment, we solve the root cause rather than penalizing the customer after delivery.

---

### Q2: What is "bracketing" in online shopping, and how does your system detect and handle it?
**Answer:**
"Bracketing" is a customer purchasing behavior where a shopper orders multiple adjacent sizes of the same garment (e.g., ordering both Size M and Size L of product P001) with the deliberate intent to try them at home and return the size that does not fit.

In our system, bracketing is handled in two ways:
1. **Entity Extraction & ML Signal:** Our agent's entity extractor scans for multi-size queries or flags the `bracketing_order` boolean parameter. In our trained Scikit-learn model, `bracketing_order` is an active feature (importance weight 0.0566) that substantially elevates pre-purchase return risk probability.
2. **Proactive Sizing Guidance:** When detected, the agent intervenes with personalized torso ease calculations, identifying the exact correct size so the customer only needs to buy one garment.

---

### Q3: What is "vanity sizing", and why do static size charts fail to solve it?
**Answer:**
Vanity sizing is the practice where fashion brands deliberately label garments with smaller size numbers or letters to flatter customers (e.g., a 34-inch waist labeled as a size 30 or 32). Consequently, a "Medium" in one brand may measure 40 inches in the chest, while in another it measures 43 inches.

Static size charts fail because:
1. They display static 2D tables that do not clarify whether measurements represent garment dimensions or body circumference.
2. They do not account for silhouette ease (slim vs. oversized drape).
3. They ignore fabric elasticity (100% rigid cotton vs. 2% elastane blend).
4. Customers rarely interpret tolerance differentials correctly without an intelligent agent.

---

## SECTION 2: AI AGENT ARCHITECTURE & INTENT CLASSIFICATION

### Q4: Explain the difference between a traditional chatbot and an "AI Agent" as implemented in your project.
**Answer:**
A traditional chatbot relies primarily on keyword matching or a generative LLM that outputs conversational text without executing deterministic backend logic or interacting with enterprise systems.

In contrast, our project implements an **Autonomous Multi-Tool AI Agent**:
1. It parses unstructured customer queries into structured **intents and entities**.
2. It dynamically decides which backend Python tools must be executed based on intent and missing information.
3. It gathers structured evidence from multiple heterogeneous sources (ML models, catalog databases, knowledge bases, tailoring algorithms).
4. It resolves conflicting signals through a **Decision Synthesis Engine**.
5. It returns a strongly typed, verifiable Pydantic `AgentResponse` containing execution telemetry, confidence scores, and structured UI components.

---

### Q5: What are the 9 canonical intents supported by your agent, and how are they classified?
**Answer:**
The 9 canonical intents defined in `backend/schemas/agent_schemas.py` are:
1. `PRODUCT_INFORMATION`: Queries about fabric, care instructions, origin, and design quirks.
2. `SIZE_INFORMATION`: Requests for official size chart tables, measurements, or dimensional specs.
3. `FIT_RECOMMENDATION`: Queries asking whether a specific size will fit given personal body measurements.
4. `RETURN_RISK_PREDICTION`: Queries asking for return risk probabilities or ML risk evaluations.
5. `RETURN_HISTORY_ANALYSIS`: Queries asking about previous return defect rates or customer feedback.
6. `RETURN_POLICY`: Inquiries about return windows, condition tags, refunds, or shipping policies.
7. `PURCHASE_DECISION`: Complex multi-faceted queries asking whether to buy or keep an item.
8. `GENERAL_PRODUCT_QUESTION`: Broad styling or catalog inquiries.
9. `UNKNOWN_INTENT`: Unrelated queries, off-topic requests, or unsupported actions.

They are classified by our dedicated `IntentClassifier` in `backend/agent/intent_classifier.py` using weighted compiled regex patterns and priority-based disambiguation.

---

### Q6: Why did you use regex pattern weighting instead of a heavy LLM or BERT model for intent classification?
**Answer:**
We designed our intent classification for production efficiency, determinism, and zero-token latency:
1. **Latency & Cost:** A BERT model or cloud LLM call introduces 200–1200 ms of network and inference latency plus recurring API billing. Our compiled regex scoring engine executes in **sub-1 millisecond** (total agent turn is ~6.2 ms).
2. **Deterministic Reproducibility:** In an academic and enterprise setting, decisions must be 100% reproducible for auditing. Regex score disambiguation guarantees zero hallucinations or stochastic variability.
3. **Rigorous Verification:** In automated unit tests (`test_phase1_agent.py`), this classifier achieved **100.0% accuracy across 32 benchmark test cases**, proving exceptional precision for the domain vocabulary.

---

### Q7: How does the agent handle ambiguous or multi-intent queries?
**Answer:**
Our `IntentClassifier` computes a continuous match score for each intent based on keyword weights (e.g., words like `size chart` or `measurements` carry high weights). 

When multiple intents trigger:
1. A **score difference threshold** is checked: if the highest scoring intent leads by a clear margin, it is selected.
2. If two intents have close scores, an explicit **domain priority hierarchy** resolves ties:
   `PURCHASE_DECISION` > `FIT_RECOMMENDATION` > `RETURN_RISK_PREDICTION` > `SIZE_INFORMATION` > `PRODUCT_INFORMATION` > `RETURN_POLICY` > `RETURN_HISTORY_ANALYSIS`.
3. In multi-tool routing, secondary intents still trigger secondary tools (e.g., if a user asks about fit and return risk, both the fit calculator and ML predictor are dispatched simultaneously).

---

## SECTION 3: AGENT TOOLS & DYNAMIC TOOL ROUTING

### Q8: What are the 6 registered agent tools in your project, and what are their specific responsibilities?
**Answer:**
All six tools reside in `backend/tools/agent_tools.py`:
1. `product_information_tool`: Retrieves product descriptions, material composition, care instructions, and known fit quirks from `data/products.json`.
2. `size_chart_tool`: Fetches exact garment measurements (chest, waist, shoulders, length) for specific product sizes.
3. `fit_calculator_tool`: Deterministically calculates ease differentials between garment specifications and customer body measurements.
4. `return_risk_prediction_tool`: Invokes the serialized Scikit-learn Logistic Regression model to compute pre-purchase return probability.
5. `return_history_analyzer_tool`: Aggregates historical return rates, common defect reasons, and customer feedback from `orders_dataset.csv`.
6. `rag_retrieval_tool`: Performs TF-IDF cosine similarity search over Markdown knowledge documents for return policies, sizing methods, and fabric care.

---

### Q9: How does dynamic tool routing work in the Agent Controller?
**Answer:**
In `backend/agent/controller.py`, tool dispatching is driven by intent routing rules and entity completeness:
- If intent is `PRODUCT_INFORMATION` → executes `product_information_tool` and `rag_retrieval_tool`.
- If intent is `SIZE_INFORMATION` → executes `product_information_tool` and `size_chart_tool`.
- If intent is `FIT_RECOMMENDATION` → executes `product_information_tool`, `size_chart_tool`, and `fit_calculator_tool`; if measurements are missing, prompts the user.
- If intent is `RETURN_RISK_PREDICTION` → executes `product_information_tool`, `return_risk_prediction_tool`, and `return_history_analyzer_tool`.
- If intent is `PURCHASE_DECISION` → executes all tools to synthesize a comprehensive pre-purchase evaluation.

Tools are only called when required, minimizing compute overhead.

---

## SECTION 4: MACHINE LEARNING & RETURN RISK PREDICTION

### Q10: What dataset was used to train the machine learning models?
**Answer:**
We trained on an e-commerce order dataset of **920 order records** located in `backend/data/orders_dataset.csv`. The dataset includes product categories, fit types, retail pricing, size guide availability, description completeness scores, promotional discounts, bracketing flags, and historical return outcomes. We utilized an 80/20 stratified train/test split: **736 training samples and 184 held-out test samples**.

---

### Q11: Explain the "Target Separation Principle" and why it is crucial to avoid data leakage in return prediction.
**Answer:**
Data leakage occurs when a model is trained on features that would not actually be available at inference time in the real world. In e-commerce return modeling, common naive mistakes include feeding post-purchase features—such as delivery transit duration, courier delay flags, return reason codes, or post-delivery survey ratings.

Under our **Target Separation Principle**, our ML pipeline strictly isolates the target variable (`is_returned`) and permits **only pre-purchase features observable before the user clicks 'Checkout'**:
- Garment category, fit silhouette, item price, size guide presence, description completeness, discount applied, bracketing order boolean, and catalog-level historical return rates.
This guarantees genuine predictive power rather than artificial post-hoc correlation.

---

### Q12: Why did you compare Logistic Regression, Random Forest, and Gradient Boosting, and why was Logistic Regression selected?
**Answer:**
We benchmarked three diverse supervised learning algorithms:
- **Logistic Regression:** Linear, highly interpretable probabilistic baseline with L2 regularization.
- **Random Forest:** Ensemble of decorrelated decision trees capturing non-linear feature interactions.
- **Gradient Boosting:** Sequential ensemble optimizing loss through gradient descent on residuals.

**Why Logistic Regression was chosen:**
While Gradient Boosting achieved higher raw accuracy (73.37%), Logistic Regression was superior on our primary domain objective:
1. **Recall:** Logistic Regression achieved **70.37% Recall** compared to 59.26% for Random Forest and only 38.89% for Gradient Boosting. In return prevention, minimizing False Negatives (missing a return that actually happens) is far more important than minimizing False Positives.
2. **Discriminative Ability:** Logistic Regression achieved the highest **ROC-AUC of 0.7520** (vs 0.7083 for RF and 0.6750 for GB) and PR-AUC of 0.5838.
3. **Calibrated Probabilities:** Logistic Regression produces smooth sigmoid probabilities that directly map to intuitive risk percentages for customer display.

---

### Q13: What were the most important features driving the ML return-risk predictions?
**Answer:**
Based on our feature importance and coefficient analysis:
1. `product_size_return_rate` (Importance: **0.3282** / 32.8%): Specific product-and-size combinations that have historically high returns are the strongest predictor.
2. `category_Footwear` (Importance: **0.1039** / 10.4%): Footwear inherently has higher return rates due to rigid foot ergonomics.
3. `historical_return_rate` (Importance: **0.0654** / 6.5%): Baseline product defect rate.
4. `bracketing_order` (Importance: **0.0566** / 5.7%): Multi-size ordering intent.
5. `category_Outerwear` & `category_Dresses` (Importance: ~5.0%): Silhouette and drape sensitivity.

---

## SECTION 5: PHYSICAL FIT CALCULATION & EASE MATHEMATICS

### Q14: What is "garment ease", and how does the fit calculator compute it?
**Answer:**
In garment construction and tailoring, **ease** is the difference between the physical circumference of the finished garment and the customer's anatomical body measurement:
$$\text{Ease Differential} = \text{Garment Dimension} - \text{Body Measurement}$$

Garment ease allows the wearer to breathe, sit, bend, and move comfortably. Zero ease means skin-tight contact with no stretch, while negative ease means the garment cannot physically close without elastane stretch.

---

### Q15: How are ease tolerances calibrated for different apparel silhouettes in your system?
**Answer:**
Different silhouettes require distinct ease allowances to achieve their intended design drape:
- **Slim Fit:** Requires **1.5" to 2.5"** chest ease and **1.5" to 2.5"** waist ease. Less than 1.0" causes fabric pulling and button gap; over 2.5" loses the slim profile.
- **Regular Fit:** Requires **2.5" to 4.0"** chest ease and **2.5" to 4.0"** waist ease for comfortable business and daily wear.
- **Relaxed / Oversized:** Accommodates **4.0" to 6.5"** chest ease for intentional boxy drape.

Our `fit_calculator_tool` compares measurements against these calibrated thresholds to generate deterministic verdicts: `Perfect Fit`, `Snug / Tight`, `Too Small`, `Loose`, or `Too Large`.

---

## SECTION 6: RETRIEVAL-AUGMENTED GENERATION (RAG)

### Q16: What is RAG, and why is it needed in this project if you already have a database?
**Answer:**
Retrieval-Augmented Generation (RAG) is an AI pattern where contextual knowledge is retrieved from an external corpus and supplied to an agent to produce grounded, hallucination-free answers.

While structured attributes (prices, sizes) reside in `products.json`, unstructured domain intelligence—such as the exact 30-day return policy conditions, tag preservation rules, how to properly position a measuring tape, raw denim shrinkage during first wash, and specific garment quirks—resides in rich Markdown knowledge documents. RAG allows the agent to semantically retrieve exact paragraphs and cite verified policies.

---

### Q17: Describe your RAG indexing and retrieval implementation.
**Answer:**
Our RAG pipeline is implemented in `backend/knowledge_base/`:
1. **Corpus:** 4 curated Markdown documents (`return_policy.md`, `sizing_and_measurement_guide.md`, `materials_and_fabric_care.md`, `product_catalog_and_fit_notes.md`).
2. **Chunking:** The corpus is split into **35 semantic chunks**, preserving section headers and context.
3. **Vector Index:** We use a Scikit-learn `TfidfVectorizer` configured with sublinear term frequency scaling ($1 + \log(TF)$) and English stop-word filtering.
4. **Scoring:** Query text is vectorized, and **cosine similarity** is calculated against all chunk vectors. Chunks exceeding a similarity threshold are returned with relevance ranks.
5. **Advantage:** Zero embedding model latency, zero external API costs, 100% deterministic local retrieval.

---

## SECTION 7: DECISION SYNTHESIS & CONFLICT RESOLUTION

### Q18: What is the Decision Synthesis Engine, and what problem does it solve?
**Answer:**
The Decision Synthesis Engine (implemented in `backend/agent/decision_engine.py`) is the cognitive core of the agent. In a complex multi-tool agent, individual tools frequently provide **contradictory evidence**:
- For example: The ML return risk model flags an item as "High Risk" (because 35% of all buyers return it), BUT the customer's personal measurements reveal a "Perfect Fit" on chest, waist, and shoulders.
- Or: The physical ease is mathematically acceptable, BUT historical return logs reveal that 50% of buyers returned the shirt due to snug armholes.

A naive chatbot would either hallucinate or confuse the user. Our Decision Synthesis Engine applies deterministic evidence-weighting rules to reconcile these discrepancies into a coherent, actionable verdict.

---

### Q19: What is the hierarchical evidence weighting rule used by your decision engine?
**Answer:**
The decision engine prioritizes evidence in the following order:
1. **Personal Physical Fit (Highest Weight):** Individual body measurements vs. actual garment specs are the primary determinant of comfort. If chest ease is negative, the garment physically will not fit regardless of cohort statistics.
2. **Historical Defect Quirks (Medium Weight):** Empirical return feedback (e.g., tight shoulders or shrinkage after washing) modifies the verdict with targeted cautionary advice.
3. **ML Cohort Risk Model (Contextual Weight):** Provides broad demographic probability. If physical fit is confirmed, high ML risk is explained as a category-level anomaly, reassuring the customer while explaining the risk factors.

---

### Q20: What are the two execution modes of your AI agent: Gemini LLM Mode vs Deterministic Academic Engine Mode?
**Answer:**
Our agent supports two switchable execution modes:
1. **Deterministic Academic Engine Mode (Default):** Runs entirely locally in Python using deterministic rule-based synthesis, Scikit-learn ML, and TF-IDF RAG. It has **sub-15ms latency, zero token costs, and 100% reproducible responses**, making it ideal for academic benchmarking and high-throughput production.
2. **Gemini LLM Mode:** Can be toggled when an API key is provided, using Google Gemini 1.5/2.0 to generate natural, conversational prose while strictly adhering to the structured evidence payload synthesized by the Python backend.

---

## SECTION 8: SYSTEM EVALUATION & PERFORMANCE

### Q21: How did you evaluate the performance of your system?
**Answer:**
We established a comprehensive three-tier evaluation methodology:
1. **Intent Classification & Entity Extraction:** Evaluated across 32 structured test cases in `test_phase1_agent.py`, achieving **100.0% accuracy (32/32 passed)**.
2. **End-to-End Agent Scenarios:** Evaluated across 20 multi-step integration scenarios in `test_scenarios.py`, covering single-size queries, bracketing, unknown intents, and edge cases, achieving a **100.0% pass rate (20/20 passed)**.
3. **Machine Learning Model Benchmark:** Evaluated across 184 held-out test instances with 5-fold cross-validation, measuring Accuracy (68.48%), Precision (47.50%), Recall (70.37%), F1 (0.5672), ROC-AUC (0.7520), and PR-AUC (0.5838).
4. **Latency Benchmarking:** Measured average agent response latency of **6.2 milliseconds**.

---

### Q22: Explain the confusion matrix of your selected Logistic Regression model.
**Answer:**
Evaluated on the 184 held-out test samples:
- **True Negatives (TN) = 88:** Garments correctly predicted as kept and actually kept.
- **True Positives (TP) = 38:** Garments correctly predicted as returned and actually returned.
- **False Positives (FP) = 42:** Garments predicted as returned, but the customer kept them.
- **False Negatives (FN) = 16:** Garments predicted as kept, but the customer returned them.

This yields a **Recall of $38 / (38 + 16) = 70.37\%$**. We intentionally tuned the classification threshold to minimize False Negatives (only 16), ensuring the agent captures over 70% of potential return events before they occur.

---

### Q23: How do you know your frontend and backend integration is robust?
**Answer:**
1. **Type Safety:** The frontend uses TypeScript with strict Pydantic-mirrored interfaces in `frontend/src/types/index.ts`. Running `npm run build` succeeds cleanly with zero TypeScript or JSX compile errors.
2. **Verified Image Pipeline:** All 18 products have local, verified JPEG assets in `frontend/public/images/products/` with fallback error handlers.
3. **Telemetry & Observability:** The system logs every API request to an in-memory ring buffer, displaying live latency metrics, model metrics, and confusion matrices on the System Monitoring page (`/monitoring`).

---

## SECTION 9: LIMITATIONS & FUTURE SCOPE

### Q24: What are the main limitations of your current implementation?
**Answer:**
We identify four honest academic limitations:
1. **Synthetic Order Data:** The 920 orders were synthetically generated to reflect known retail distributions; validation on millions of live transactions is necessary for enterprise deployment.
2. **2D vs. 3D Body Representation:** The fit engine currently compares 1D circumference measurements (chest, waist, shoulders); it does not model 3D body curvature, posture, or muscle-to-fat distribution.
3. **Simplified Fabric Elasticity:** Fabric stretch is represented via categorical parameters rather than real-time finite-element 3D cloth physics simulations.
4. **Catalog Scope:** The current implementation demonstrates 18 styles across 8 categories; enterprise scaling would require automated ingestion of thousands of dynamic brand size charts.

---

### Q25: How would you scale this project for enterprise deployment on platforms like Shopify or Amazon?
**Answer:**
1. **Headless SDK / E-Commerce Widgets:** Package the React assistant as a lightweight embeddable web component or Shopify App that integrates into product detail pages via storefront APIs.
2. **Computer Vision Body Scanning:** Integrate mobile smartphone camera capture to extract anthropometric 3D landmarks automatically using computer vision (e.g., MediaPipe or PoseNet), removing the need for manual tape measuring.
3. **Online Continuous Learning:** Implement streaming feedback pipelines (e.g., Kafka + online ML) to continuously update garment ease tolerances and return-risk coefficients whenever a customer submits post-delivery feedback.
4. **Multi-Brand OCR Size Parsing:** Use vision-language models to automatically ingest and normalize PDF/image size charts from fashion suppliers into standard JSON format.

---

## SECTION 10: RAPID-FIRE TECHNICAL CHECKS

### Q26: What is Pydantic v2 and where is it used?
**Answer:**
Pydantic v2 is a high-performance Python data validation library using Rust core. It is used in `backend/schemas/agent_schemas.py` to define strict schemas for `AgentIntent`, `ExtractedEntities`, `FitVerdict`, and `AgentResponse`.

### Q27: What is the difference between ROC-AUC and PR-AUC?
**Answer:**
ROC-AUC evaluates the trade-off between True Positive Rate and False Positive Rate across all thresholds. PR-AUC evaluates Precision vs. Recall, which is especially informative for imbalanced datasets where the positive class (returns) is a minority. Our model achieved 0.7520 ROC-AUC and 0.5838 PR-AUC.

### Q28: How does the system handle a user who inputs measurements in centimeters instead of inches?
**Answer:**
The `EntityExtractor` includes unit detection regexes (`cm` vs `in` / `inches`). If centimeters are detected (e.g. `102 cm`), the extractor automatically converts them to inches ($1\text{ in} = 2.54\text{ cm}$) before passing them to the physical fit engine.

### Q29: What happens if a customer asks an off-topic question like "What is the capital of France?"
**Answer:**
The `IntentClassifier` detects zero apparel/sizing keyword patterns, assigning it a top score of 0, which defaults to `UNKNOWN_INTENT`. The agent politely clarifies its role as a pre-purchase fashion decision assistant and prompts the customer to ask about sizing, fit, or return policies.

### Q30: What is the single most important takeaway of this project?
**Answer:**
**"Fix the product page, not the customer."** Artificial intelligence can proactively eliminate preventable e-commerce returns by providing pre-purchase sizing confidence and transparent evidence synthesis, creating a win-win for both consumer satisfaction and sustainable retail economics.

---

*End of Viva Questions and Answers.*

