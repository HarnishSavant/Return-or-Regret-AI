"""
Intent Classifier Module — Phase 1.2
=====================================
Dedicated, testable module for customer query intent classification
and structured entity extraction.

Architecture:
  1. Score-based multi-intent ranking with keyword clusters
  2. Priority disambiguation rules for overlapping intents
  3. Structured entity extraction (product ID, size, body measurements)
  4. Validation of extracted values against catalog and plausibility bounds

The classifier is stateless and receives the PRODUCTS_CACHE reference
at construction time so it can validate product IDs.
"""

import re
from typing import Dict, Any, Optional, List, Set

from schemas.agent_schemas import (
    AgentIntent,
    ExtractedEntities,
    IntentClassificationResult,
)


# ──────────────────────────────────────────────────────────
# Keyword Clusters for Intent Scoring
# ──────────────────────────────────────────────────────────
# Each cluster maps an intent to a list of (pattern, weight) tuples.
# Patterns are evaluated as case-insensitive substring or regex matches.

_INTENT_KEYWORDS: Dict[AgentIntent, List[tuple]] = {

    AgentIntent.RETURN_POLICY: [
        (r"\breturn policy\b", 10),
        (r"\brefund policy\b", 10),
        (r"\bexchange policy\b", 10),
        (r"\bhow to return\b", 9),
        (r"\bcan i return\b", 9),
        (r"\breturn window\b", 9),
        (r"\bdays to return\b", 9),
        (r"\brefund\b", 7),
        (r"\bexchange\b", 5),
        (r"\breturn this\b", 6),
        (r"\breturn it\b", 5),
        (r"\bpolicy\b", 4),
    ],

    AgentIntent.RETURN_HISTORY_ANALYSIS: [
        (r"\bwhy do customers return\b", 10),
        (r"\bwhy (?:is|are|do|did) .+ returned\b", 9),
        (r"\bwhy returned\b", 9),
        (r"\breturn history\b", 9),
        (r"\bcommon return reasons\b", 9),
        (r"\breturn reasons\b", 8),
        (r"\bdefect patterns?\b", 8),
        (r"\bcustomer complaints?\b", 7),
        (r"\bmost common reasons?\b", 7),
        (r"\breturn rate\b", 5),
        (r"\bfrequently returned\b", 7),
    ],

    AgentIntent.RETURN_RISK_PREDICTION: [
        (r"\bpredicted? (?:return )?probability\b", 10),
        (r"\bml (?:return )?(?:risk|prediction)\b", 10),
        (r"\bpredicted? return\b", 9),
        (r"\breturn probability\b", 9),
        (r"\bhow risky\b", 8),
        (r"\brisk (?:of|for) (?:buying|purchasing|ordering)\b", 8),
        (r"\bml prediction\b", 9),
        (r"\bmachine learning\b", 7),
        (r"\bprediction model\b", 7),
        (r"\breturn risk\b", 9),
        (r"\bml\b", 6),
    ],

    AgentIntent.PURCHASE_DECISION: [
        (r"\bshould i (?:buy|purchase|order|get)\b", 10),
        (r"\bis (?:this|it) (?:a )?good (?:buy|purchase)\b", 9),
        (r"\bgood purchase\b", 8),
        (r"\bworth (?:buying|purchasing|ordering|getting)\b", 8),
        (r"\bdecide on\b", 6),
        (r"\bdecision\b", 4),
        (r"\brecommend (?:buying|purchasing)\b", 8),
        (r"\bis this a good purchase\b", 10),
    ],

    AgentIntent.FIT_RECOMMENDATION: [
        (r"\bwill (?:it|this|size) fit\b", 10),
        (r"\bwill size \w+ fit\b", 10),
        (r"\bfit (?:me|my)\b", 9),
        (r"\bsize recommend\b", 9),
        (r"\brecommend (?:a )?size\b", 9),
        (r"\bwhat size\b", 8),
        (r"\btoo tight\b", 7),
        (r"\btoo loose\b", 7),
        (r"\bcomfortable for me\b", 7),
        (r"\bfit for me\b", 8),
        (r"\bchest is \d+\b", 6),
        (r"\bwaist is \d+\b", 6),
        (r"\bshoulder is \d+\b", 6),
        (r"\bi (?:usually )?wear\b", 5),
        (r"\bfit\b", 2),
        (r"\bsizing\b", 3),
    ],

    AgentIntent.SIZE_INFORMATION: [
        (r"\bsize chart\b", 10),
        (r"\bdimensions?\b", 8),
        (r"\bgarment (?:dimensions?|measurements?)\b", 10),
        (r"\bsize dimensions?\b", 9),
        (r"\bmeasurements? (?:of|for)\b", 8),
        (r"\bshow (?:me )?(?:the )?measurements?\b", 8),
        (r"\bchest (?:width|measurement|dimension)\b", 7),
        (r"\bshoulder width\b", 7),
        (r"\bwaist measurement\b", 7),
        (r"\blength (?:of|for)\b", 5),
        (r"\bsizing details?\b", 8),
        (r"\bsize specs?\b", 8),
        (r"\bsize guide\b", 7),
        (r"\bmeasurements? (?:in|for) size\b", 9),
    ],

    AgentIntent.PRODUCT_INFORMATION: [
        (r"\bwhat material\b", 10),
        (r"\bmade (?:of|from)\b", 9),
        (r"\bfabric\b", 8),
        (r"\bcotton\b", 6),
        (r"\bpolyester\b", 6),
        (r"\bwool\b", 5),
        (r"\bsilk\b", 5),
        (r"\blinen\b", 5),
        (r"\bwash\b", 7),
        (r"\bcare instructions?\b", 8),
        (r"\bhow (?:to|do i) wash\b", 8),
        (r"\bshrink\b", 6),
        (r"\bprice\b", 7),
        (r"\bhow much\b", 7),
        (r"\bcost\b", 6),
        (r"\btell me about\b", 4),
        (r"\bcolou?r\b", 5),
        (r"\bdescription\b", 4),
    ],

    AgentIntent.GENERAL_PRODUCT_QUESTION: [
        (r"\btell me more\b", 6),
        (r"\bwhat features?\b", 5),
        (r"\bwhich features?\b", 5),
        (r"\binformation about\b", 4),
        (r"\bdetails about\b", 4),
    ],

    AgentIntent.UNKNOWN_INTENT: [
        (r"\bweather\b", 10),
        (r"\bcapital of\b", 10),
        (r"\bpresident\b", 10),
        (r"\bbitcoin\b", 10),
        (r"\bcryptocurrency\b", 10),
        (r"\brecipe for\b", 10),
        (r"\bwho wrote\b", 10),
        (r"\btell me a joke\b", 10),
        (r"\brolex\b", 8),
        (r"\bstock market\b", 8),
        (r"\bsports score\b", 8),
        (r"\bplay music\b", 8),
        (r"\bmovie recommendation\b", 8),
    ],
}


class IntentClassifier:
    """
    Score-based intent classifier with priority disambiguation.

    Usage:
        classifier = IntentClassifier(products_cache)
        result = classifier.classify(query, context_product_id, context_measurements)
    """

    def __init__(self, products_cache: Dict[str, Dict[str, Any]]):
        self.products_cache = products_cache
        # Pre-compile all regex patterns for performance
        self._compiled_patterns: Dict[AgentIntent, List[tuple]] = {}
        for intent, patterns in _INTENT_KEYWORDS.items():
            self._compiled_patterns[intent] = [
                (re.compile(pat, re.IGNORECASE), weight)
                for pat, weight in patterns
            ]

    # ──────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────
    def classify(
        self,
        query: str,
        context_product_id: Optional[str] = None,
        context_measurements: Optional[Dict[str, float]] = None,
    ) -> IntentClassificationResult:
        """
        Classify a customer query into one of 9 canonical intents
        and extract structured entities.
        """
        # Step 1: Extract entities
        entities = self._extract_entities(query, context_product_id, context_measurements)

        # Step 2: Score all intents
        scores = self._score_intents(query)

        # Step 3: Apply disambiguation priority rules
        intent, confidence = self._disambiguate(query, scores, entities)

        # Step 4: Determine if clarification is needed
        clarification_required = False
        clarification_question = None

        if intent == AgentIntent.FIT_RECOMMENDATION and not self._has_body_measurements(entities):
            clarification_required = True
            missing = []
            if entities.chest_measurement is None:
                missing.append("chest")
            if entities.waist_measurement is None:
                missing.append("waist")
            clarification_question = (
                f"To provide a personalised fit recommendation, please share your "
                f"{' and '.join(missing)} measurement(s) in inches."
            )

        if intent == AgentIntent.PURCHASE_DECISION and entities.product_id is None:
            clarification_required = True
            clarification_question = "Which product are you considering? Please specify a product ID (e.g. P001)."

        # Step 5: Identify missing information for fit-related intents
        if intent in (AgentIntent.FIT_RECOMMENDATION, AgentIntent.PURCHASE_DECISION):
            if entities.chest_measurement is None:
                entities.missing_required_information.append("Chest / Bust measurement")
            if entities.waist_measurement is None:
                entities.missing_required_information.append("Waist measurement")
            # For slim fit products, shoulder is important
            if entities.product_id and entities.product_id in self.products_cache:
                prod = self.products_cache[entities.product_id]
                if prod.get("fit_type") == "Slim Fit" and entities.shoulder_measurement is None:
                    entities.missing_required_information.append(
                        "Shoulder width measurement (recommended for Slim Fit styles)"
                    )

        return IntentClassificationResult(
            intent=intent,
            extracted_entities=entities,
            confidence=confidence,
            classification_method="deterministic_scoring",
            clarification_required=clarification_required,
            clarification_question=clarification_question,
        )

    # ──────────────────────────────────────────────────────
    # Entity Extraction
    # ──────────────────────────────────────────────────────
    def _extract_entities(
        self,
        query: str,
        context_product_id: Optional[str] = None,
        context_measurements: Optional[Dict[str, float]] = None,
    ) -> ExtractedEntities:

        product_id = self._extract_product_id(query, context_product_id)
        is_invalid_pid = False
        if product_id and product_id not in self.products_cache:
            is_invalid_pid = True

        requested_size = self._extract_size(query, product_id)

        measurements = self._extract_measurements(query)
        # Merge context measurements (explicit API parameters take priority)
        if context_measurements:
            for key, val in context_measurements.items():
                k = key.lower().strip()
                if k in ("chest", "bust") and measurements.get("chest") is None:
                    measurements["chest"] = float(val)
                elif k == "waist" and measurements.get("waist") is None:
                    measurements["waist"] = float(val)
                elif k == "shoulder" and measurements.get("shoulder") is None:
                    measurements["shoulder"] = float(val)
                elif k == "hip" and measurements.get("hip") is None:
                    measurements["hip"] = float(val)
                elif k == "inseam" and measurements.get("inseam") is None:
                    measurements["inseam"] = float(val)

        # Determine product category
        product_category = None
        if product_id and product_id in self.products_cache:
            product_category = self.products_cache[product_id].get("category")

        # Main question: cleaned version of the input query
        main_question = query.strip()

        return ExtractedEntities(
            product_id=product_id,
            is_invalid_product_id=is_invalid_pid,
            requested_size=requested_size,
            chest_measurement=measurements.get("chest"),
            waist_measurement=measurements.get("waist"),
            shoulder_measurement=measurements.get("shoulder"),
            hip_measurement=measurements.get("hip"),
            inseam_measurement=measurements.get("inseam"),
            measurement_unit="inches",
            product_category=product_category,
            main_question=main_question,
            missing_required_information=[],
        )

    def _extract_product_id(self, query: str, context_product_id: Optional[str]) -> Optional[str]:
        """Extract product ID from query text or context."""
        # Try explicit PID pattern (P001, P002, etc.)
        match = re.search(r'\b(P\d{3,4})\b', query, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Fall back to context product ID
        if context_product_id:
            return context_product_id.strip().upper()

        # Try matching product name keywords from catalog
        q_lower = query.lower()
        for pid, product in self.products_cache.items():
            name_words = [w for w in product["name"].lower().split() if len(w) > 3]
            if any(w in q_lower for w in name_words):
                return pid

        return None

    def _extract_size(self, query: str, product_id: Optional[str]) -> Optional[str]:
        """Extract clothing size from query."""
        # Pattern: "size M", "size XL", "size 32"
        size_match = re.search(r'\bsize\s+([A-Za-z0-9]+)\b', query, re.IGNORECASE)
        if size_match:
            candidate = size_match.group(1).upper()
            non_sizes = {"CHART", "GUIDE", "SPECS", "SPEC", "DETAILS", "DIMENSIONS", "MEASUREMENTS", "RUNS", "FITS"}
            if candidate not in non_sizes:
                return candidate

        # Standalone letter sizes (order matters: check multi-char first)
        standalone = re.search(r'\b(XXL|XL|XS|S|M|L)\b', query)
        if standalone:
            return standalone.group(1).upper()

        # Numeric pant sizes (28-42)
        num_match = re.search(r'\b(2[89]|3[0-8]|4[0-2])\b', query)
        if num_match:
            return num_match.group(1)

        # Default to M if product exists and supports it
        if product_id and product_id in self.products_cache:
            sizes = self.products_cache[product_id].get("sizes", [])
            if "M" in sizes:
                return "M"
            elif sizes:
                return sizes[0]

        return None

    def _extract_measurements(self, query: str) -> Dict[str, Optional[float]]:
        """Extract body measurements from query text with auto cm→inch conversion."""
        measurements: Dict[str, Optional[float]] = {}

        patterns = [
            ("chest", r'\b(?:chest|bust)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?'),
            ("waist", r'\b(?:waist)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?'),
            ("shoulder", r'\b(?:shoulder)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?'),
            ("hip", r'\b(?:hip)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?'),
            ("inseam", r'\b(?:inseam)\b(?:[^0-9\n]{0,25})?(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?'),
        ]

        # Also handle shorthand: "42 chest", "36 waist"
        shorthand_patterns = [
            ("chest", r'(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?\s*(?:chest|bust)\b'),
            ("waist", r'(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?\s*(?:waist)\b'),
            ("shoulder", r'(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?\s*(?:shoulder)\b'),
            ("hip", r'(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?\s*(?:hip)\b'),
            ("inseam", r'(\d+(?:\.\d+)?)\s*(?:inch(?:es)?|in|"|cm)?\s*(?:inseam)\b'),
        ]

        for dim, pattern in patterns:
            m = re.search(pattern, query, re.IGNORECASE)
            if m:
                val = float(m.group(1))
                # Auto-convert centimetres to inches
                if val > 60.0 and dim in ("chest", "waist", "hip"):
                    val = round(val / 2.54, 1)
                # Plausibility check
                if 10.0 <= val <= 80.0:
                    measurements[dim] = val

        # Check shorthand patterns for anything not yet matched
        for dim, pattern in shorthand_patterns:
            if dim not in measurements:
                m = re.search(pattern, query, re.IGNORECASE)
                if m:
                    val = float(m.group(1))
                    if val > 60.0 and dim in ("chest", "waist", "hip"):
                        val = round(val / 2.54, 1)
                    if 10.0 <= val <= 80.0:
                        measurements[dim] = val

        return measurements

    # ──────────────────────────────────────────────────────
    # Intent Scoring
    # ──────────────────────────────────────────────────────
    def _score_intents(self, query: str) -> Dict[AgentIntent, float]:
        """Score every intent against the query using compiled regex patterns."""
        scores: Dict[AgentIntent, float] = {intent: 0.0 for intent in AgentIntent}

        for intent, compiled in self._compiled_patterns.items():
            for regex, weight in compiled:
                if regex.search(query):
                    scores[intent] += weight

        return scores

    def _has_body_measurements(self, entities: ExtractedEntities) -> bool:
        return any([
            entities.chest_measurement is not None,
            entities.waist_measurement is not None,
            entities.shoulder_measurement is not None,
            entities.hip_measurement is not None,
            entities.inseam_measurement is not None,
        ])

    # ──────────────────────────────────────────────────────
    # Disambiguation
    # ──────────────────────────────────────────────────────
    def _disambiguate(
        self,
        query: str,
        scores: Dict[AgentIntent, float],
        entities: ExtractedEntities,
    ) -> tuple:
        """
        Apply priority rules to resolve overlapping intents.

        Priority order (highest to lowest):
        1. UNKNOWN_INTENT (if clearly out-of-domain)
        2. RETURN_POLICY (explicit policy inquiry)
        3. RETURN_HISTORY_ANALYSIS (asks about past return reasons)
        4. RETURN_RISK_PREDICTION (asks about ML prediction / risk)
        5. PURCHASE_DECISION (asks whether to buy)
        6. FIT_RECOMMENDATION (has body measurements + fit question)
        7. SIZE_INFORMATION (asks about garment dimensions without body measurements)
        8. PRODUCT_INFORMATION (asks about material / care / price)
        9. GENERAL_PRODUCT_QUESTION (vague product query)
        """
        has_measurements = self._has_body_measurements(entities)

        # Rule 1: Strong UNKNOWN_INTENT signal with NO product-related signals
        product_signal = sum(
            scores[i] for i in AgentIntent
            if i != AgentIntent.UNKNOWN_INTENT
        )
        if scores[AgentIntent.UNKNOWN_INTENT] >= 8 and product_signal < 5:
            return AgentIntent.UNKNOWN_INTENT, 0.95

        # Rule 2: Strong RETURN_POLICY signal
        if scores[AgentIntent.RETURN_POLICY] >= 7:
            return AgentIntent.RETURN_POLICY, 0.93

        # Rule 3: Strong RETURN_HISTORY_ANALYSIS signal
        if scores[AgentIntent.RETURN_HISTORY_ANALYSIS] >= 7:
            return AgentIntent.RETURN_HISTORY_ANALYSIS, 0.92

        # Rule 4: Strong RETURN_RISK_PREDICTION signal
        if scores[AgentIntent.RETURN_RISK_PREDICTION] >= 7:
            return AgentIntent.RETURN_RISK_PREDICTION, 0.91

        # Rule 5: PURCHASE_DECISION overrides FIT when "should I buy/purchase"
        if scores[AgentIntent.PURCHASE_DECISION] >= 8:
            return AgentIntent.PURCHASE_DECISION, 0.90

        # Rule 6: FIT_RECOMMENDATION when body measurements present AND fit-related keywords
        if has_measurements and scores[AgentIntent.FIT_RECOMMENDATION] >= 4:
            return AgentIntent.FIT_RECOMMENDATION, 0.92

        # Rule 6b: FIT_RECOMMENDATION even without measurements if strong fit signal
        if scores[AgentIntent.FIT_RECOMMENDATION] >= 8:
            return AgentIntent.FIT_RECOMMENDATION, 0.88

        # Rule 7: SIZE_INFORMATION — asking about garment dimensions (NOT body fit)
        if scores[AgentIntent.SIZE_INFORMATION] >= 6:
            return AgentIntent.SIZE_INFORMATION, 0.90

        # Rule 8: PRODUCT_INFORMATION
        if scores[AgentIntent.PRODUCT_INFORMATION] >= 5:
            return AgentIntent.PRODUCT_INFORMATION, 0.89

        # Rule 9: PURCHASE_DECISION at lower threshold
        if scores[AgentIntent.PURCHASE_DECISION] >= 4:
            return AgentIntent.PURCHASE_DECISION, 0.80

        # Rule 10: FIT_RECOMMENDATION at lower threshold when measurements are present
        if has_measurements and scores[AgentIntent.FIT_RECOMMENDATION] >= 2:
            return AgentIntent.FIT_RECOMMENDATION, 0.78

        # Rule 11: GENERAL_PRODUCT_QUESTION for vague product queries
        if scores[AgentIntent.GENERAL_PRODUCT_QUESTION] >= 4:
            return AgentIntent.GENERAL_PRODUCT_QUESTION, 0.75

        # Rule 12: If product ID is mentioned but no strong intent signal,
        # treat as general product question
        if entities.product_id and entities.product_id in self.products_cache:
            return AgentIntent.GENERAL_PRODUCT_QUESTION, 0.65

        # Rule 13: If some product-related scores exist but none dominant
        top_intent = max(scores, key=scores.get)
        top_score = scores[top_intent]
        if top_score >= 3 and top_intent != AgentIntent.UNKNOWN_INTENT:
            return top_intent, 0.60

        # Default: UNKNOWN_INTENT
        return AgentIntent.UNKNOWN_INTENT, 0.50

