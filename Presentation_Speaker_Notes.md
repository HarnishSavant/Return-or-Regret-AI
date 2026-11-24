# RETURN OR REGRET AI — Presentation Speaker Notes

**Programme:** M.Sc. Data Science & Spatial Analytics  
**Course / Context:** Mini Project – Artificial Intelligence (2026–2027)  
**Institute:** Symbiosis Institute of Geoinformatics (SIG)  
**Presentation Duration:** ~10–12 Minutes total (45–75 seconds per slide)

---

## Slide 1: Title Slide (Cover)
**Estimated Time:** 45 seconds  
**Slide Visuals:** Deep navy cover, project title, badges for 9-intent agent, pre-purchase ML, ease calculation, RAG, and academic metadata.

### Speaking Script:
> "Good morning, respected professors and external examiners. 
> 
> Today, I am presenting our Artificial Intelligence mini project titled **Return or Regret AI: An Autonomous Multi-Tool AI Agent for Personalized Fit Intelligence and Return Risk Mitigation**.
> 
> In traditional e-commerce, shopping is largely a guessing game when it comes to sizing. Retailers typically respond to high return rates after the fact—often by imposing return fees or restricting return policies. 
> 
> Our project is built on a simple yet transformative engineering philosophy: **'Fix the product page, not the customer — Sizing guidance over return penalties.'** 
> 
> We have built a full-stack, autonomous multi-tool agent system that integrates pre-purchase machine learning, deterministic physical fit tolerance calculations, and semantic RAG retrieval to help customers make the right purchase decision before checkout occurs."

---

## Slide 2: Problem Statement
**Estimated Time:** 60 seconds  
**Slide Visuals:** Macro retail statistics (~30% returns, 67.6% fit-related, $816B cost) vs traditional guessing journey vs AI-assisted flow.

### Speaking Script:
> "Let us look at why this problem is critical. 
> 
> Globally, fashion apparel suffers from the highest return rate of any e-commerce category, hovering near **30%**. According to empirical retail data, **67.6% of these avoidable returns are caused specifically by sizing, fit, and tactile mismatch**.
> 
> This creates an **$816 billion annual reverse logistics crisis** that generates over 24 million metric tons of carbon emissions. Furthermore, it incentivizes customer 'bracketing'—where shoppers deliberately order 2 or 3 adjacent sizes of the same item intending to return the ones that don't fit.
> 
> Why does traditional e-commerce fail here? Because traditional product pages provide static, 2D images and generic sizing charts like 'Chest 38 to 40 inches equals Medium'. But 'vanity sizing' means an M in one brand is an L in another, and static charts ignore customer anatomical build, torso ease, and fabric stretch.
> 
> In contrast, our system replaces blind purchases with an interactive pre-purchase consultation that calculates exact body-to-garment ease differentials, evaluates ML cohort risk, and eliminates sizing guesswork."

---

## Slide 3: Project Objectives & Proposed Solution
**Estimated Time:** 60 seconds  
**Slide Visuals:** Three intelligence pillars (Autonomous Multi-Tool Agent, Pre-Purchase ML Classifier, Grounded Fit & RAG) and core transformation goal.

### Speaking Script:
> "To solve this, we formulated three core technical objectives:
> 
> First, **Autonomous Agent Intelligence**: We engineered an agent controller supporting **9 canonical intent classes** and dynamic tool routing over six specialized Python tools, running deterministically in under 15 milliseconds.
> 
> Second, **Target-Separated Machine Learning**: We developed a predictive ML classification pipeline trained strictly on pre-purchase features—completely free of post-purchase data leakage—to score baseline return risk before an order is placed.
> 
> Third, **Grounded Physical Fit & Semantic RAG**: We implemented a deterministic physical ease engine that calculates exact anatomical differentials per garment silhouette, paired with a TF-IDF vector retrieval engine that indexes curated sizing, fabric care, and policy documentation.
> 
> Together, these three pillars ensure that our recommendations are not generic chat hallucinations, but mathematically grounded and evidence-backed decisions."

---

## Slide 4: System Architecture
**Estimated Time:** 75 seconds  
**Slide Visuals:** 4 architectural tiers: React 19 Client → FastAPI Gateway → AI Agent Core (Intent Classifier & 6 Tools) → Analytical Engines (ML, Fit, RAG, Decision Synthesis).

### Speaking Script:
> "This slide illustrates our full-stack modular architecture and the complete request-response lifecycle.
> 
> At the top is the **Client Layer**, built in **React 19, TypeScript, and Tailwind CSS**. It features six production-style analytical views, including the Executive Dashboard, AI Shopping Assistant, and System Monitoring.
> 
> The client interacts via asynchronous REST requests with our **FastAPI Gateway**, validated by strict Pydantic v2 schemas.
> 
> When a customer query arrives at `/api/agent/chat`, it enters the **AI Agent Core**:
> 1. Our dedicated **Intent Classifier** scores the query across 9 canonical intents using weighted regex patterns and explicit priority disambiguation.
> 2. The **Entity Extractor** extracts key entities: product IDs, requested sizes, customer body measurements, and shopping signals like discounts and bracketing.
> 3. The **Dynamic Tool Router** dispatches only the necessary subset of our six registered tools: the product information tool, size chart tool, fit calculator, return risk predictor, return history analyzer, and RAG retrieval tool.
> 
> The outputs from these tools feed into our **Decision Synthesis Engine**, which resolves conflicting evidence and outputs a fully structured `AgentResponse` to render interactive recommendation cards in the UI."

---

## Slide 5: AI Agent Workflow & Decision Synthesis
**Estimated Time:** 75 seconds  
**Slide Visuals:** 7-Step agent pipeline walkthrough with a real query example, alongside the hierarchical evidence weighting rules.

### Speaking Script:
> "Now let us examine what makes our AI agent genuinely intelligent rather than a superficial chatbot.
> 
> Consider a real customer query: *'I'm looking at P001 Heritage Oxford Shirt. My chest is 40 inches and waist is 34 inches. Will Size M fit, and what is the return risk?'*
> 
> The agent executes a 7-step autonomous pipeline:
> - It classifies the primary intent as `FIT_RECOMMENDATION` with secondary `RETURN_RISK_PREDICTION`.
> - It extracts product `P001`, size `M`, and body dimensions (Chest: 40\", Waist: 34\").
> - It dynamically dispatches five tools concurrently: fetching garment specs, size chart tables, calculating physical ease, running the ML model, and analyzing historical return patterns.
> 
> The crucial innovation is our **Decision Synthesis Engine**. What happens when tools disagree? For example, the ML cohort model might flag a category as high risk, but the customer's personal body measurements fit the garment dimensions perfectly.
> 
> We resolved this through a **strict hierarchical weighting rule**:
> 1. **Personal Physical Fit** receives the highest priority, because individual body ease dictates anatomical comfort.
> 2. **Historical Defect Patterns** receive secondary priority to catch specific structural flaws like narrow armholes or fabric shrinkage.
> 3. **ML Cohort Risk** acts as a baseline probability filter.
> 
> The synthesis engine outputs a unified verdict: recommending Size M for regular builds, but proactively warning that customers with athletic or broad shoulders should take Size L due to P001's known upper-back design quirk."

---

## Slide 6: Machine Learning Pipeline & Return-Risk Prediction
**Estimated Time:** 75 seconds  
**Slide Visuals:** Pre-purchase feature engineering principle, empirical benchmark table across 3 algorithms, ROC-AUC curve, and confusion matrix.

### Speaking Script:
> "Slide 6 presents our Machine Learning methodology and empirical benchmarks.
> 
> A critical design principle here was **Strict Target Separation**. Many naive e-commerce ML models suffer from severe data leakage by including post-purchase fields like return reasons or delivery delays. In our pipeline, we strictly restricted features to attributes observable *before* checkout: garment category, fit type, price, size guide presence, description completeness, promotional discounts, bracketing behavior, and product-level historical return rates.
> 
> We trained and evaluated three supervised classifiers on a stratified 80/20 train/test split of 920 orders: **Logistic Regression, Random Forest, and Gradient Boosting**.
> 
> While Gradient Boosting achieved higher raw accuracy (73.37%), **Logistic Regression was selected as our active production model**. Why? Because in e-commerce return prevention, **Recall is the critical metric**. 
> 
> Logistic Regression delivered **70.37% Recall** and an **ROC-AUC of 0.7520**, compared to only 38.89% recall for Gradient Boosting. In this domain, a False Negative—failing to flag an item that gets returned—costs the retailer reverse shipping and inventory lockup. A False Positive simply results in offering the customer helpful sizing guidance. Furthermore, logistic regression provides well-calibrated probabilities for transparent customer explanations."

---

## Slide 7: RAG, Knowledge Base & Physical Fit Calculation
**Estimated Time:** 60 seconds  
**Slide Visuals:** Comparison of deterministic ease formulas across silhouettes vs TF-IDF vector retrieval over 35 knowledge chunks.

### Speaking Script:
> "On Slide 7, we contrast our two supporting intelligence layers: the Deterministic Physical Fit Engine and the Semantic RAG Engine.
> 
> The **Physical Fit Engine** uses deterministic tailoring mathematics:
> `Ease Differential = Garment Dimension - Body Measurement`.
> 
> We calibrated ease thresholds across three apparel silhouettes:
> - **Slim Fit**: requires 1.5 to 2.5 inches of chest ease for mobility without pulling.
> - **Regular Fit**: calibrated to 2.5 to 4.0 inches.
> - **Relaxed / Oversized**: accommodates 4.0 to 6.5 inches of ease.
> 
> This generates five standardized verdicts: *Perfect Fit, Snug / Tight, Too Small, Loose,* or *Too Large*.
> 
> Complementing this is our **RAG Retrieval Engine**. We indexed 35 semantic chunks across four curated Markdown knowledge guides covering our 30-day return policy, anatomical measuring instructions, fabric shrinkage rates, and garment-specific fit quirks. 
> 
> We utilized a sublinear term frequency TF-IDF vectorizer with cosine similarity scoring. This gives us instant, zero-latency retrieval with zero LLM hallucination risk, providing exact citations for return conditions and garment care."

---

## Slide 8: Application Interface & Working Demonstration
**Estimated Time:** 60 seconds  
**Slide Visuals:** Side-by-side screenshots of the verified Product Intelligence catalog (with P002 verified) and the AI Shopping Assistant with real-time sliders and synthesis card.

### Speaking Script:
> "Slide 8 showcases authentic screenshots from our running application.
> 
> On the left is the **Product Intelligence Catalog**, showcasing our verified 18-style catalog. Every product displays real-time risk tier badges—Low, Medium, or High Risk—based on empirical baselines, and users can filter across silhouettes or hand off directly to the assistant.
> 
> On the right is the **AI Shopping Assistant**. Customers can adjust interactive measurement sliders for chest, waist, and shoulders. 
> 
> When a customer asks about a product, the assistant dynamically renders an evidence-based recommendation card showing:
> - The physical fit verdict and measurement ease differential.
> - The ML cohort return probability and risk tier.
> - Historical return reasons breakdown from previous buyers.
> - And the synthesized actionable advice.
> 
> The entire workflow runs in under 15 milliseconds in our Deterministic Academic Engine mode, proving production viability."

---

## Slide 9: Evaluation, Test Results & Limitations
**Estimated Time:** 60 seconds  
**Slide Visuals:** 3 evaluation cards: Agent test suites (100%), ML test metrics (ROC-AUC 0.752), and honest academic limitations.

### Speaking Script:
> "We subjected our implementation to rigorous automated testing:
> 
> In **Agent Evaluation**, we achieved a **100% pass rate across 32 unit test cases** in `test_phase1_agent.py`, verifying flawless classification across all 9 canonical intents without cross-class confusion.
> 
> In our end-to-end integration suite, we achieved a **100% pass rate across 20 complex scenarios** in `test_scenarios.py`, validating dynamic tool execution, multi-measurement extractions, and edge-case handling.
> 
> For **System Performance**, the agent executes in an average of **6.2 milliseconds**, and the TypeScript frontend builds cleanly with zero errors.
> 
> Being academically rigorous, we also recognize key **limitations**:
> - Our 920-order dataset is synthetic, calibrated to reflect empirical retail distributions; enterprise deployment would require live transactional validation.
> - Our physical engine calculates 2D circumference ease; it does not model complex 3D posture or muscular distribution.
> - Fabric elasticity is modeled using fixed stretch multipliers rather than a real-time cloth physics simulation."

---

## Slide 10: Conclusion & Future Scope
**Estimated Time:** 45 seconds  
**Slide Visuals:** Project contribution summary, 4-phase future scaling roadmap, core philosophy quote, and Q&A closing.

### Speaking Script:
> "To conclude:
> 
> **Return or Regret AI** demonstrates that avoidable e-commerce returns can be systematically prevented before checkout by combining supervised machine learning, physical fit mathematics, and autonomous multi-tool agentic orchestration.
> 
> Looking ahead, our future roadmap includes:
> 1. Developing headless plugins for Shopify and WooCommerce.
> 2. Integrating smartphone camera computer vision for 3D body anthropometric scanning.
> 3. Establishing online reinforcement learning loops from post-delivery customer feedback.
> 4. Expanding multilingual conversational support.
> 
> As our core philosophy states: **'Fix the product page, not the customer — Sizing guidance over return penalties.'**
> 
> Thank you for your time. I am now open to your questions."

---

*End of Presentation Speaker Notes.*

