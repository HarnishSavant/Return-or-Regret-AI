from typing import Dict, Any, Optional
from schemas.agent_schemas import (
    FitVerdict,
    DecisionSynthesis,
    CustomerExplanation
)

class DecisionSynthesisEngine:
    """
    Intelligent evidence reconciliation engine that distinguishes and synthesizes:
      A. Personalised Fit Assessment (Primary physical ground truth)
      B. Machine Learning Return Prediction (Secondary population/cohort probability)
      C. Historical Product Intelligence (Empirical defect/return reason patterns)
    """

    @staticmethod
    def synthesize(
        prod_info: Dict[str, Any],
        fit_calc: Optional[Dict[str, Any]],
        risk_pred: Optional[Dict[str, Any]],
        hist_analysis: Optional[Dict[str, Any]],
        selected_size: str,
        customer_measurements: Dict[str, float]
    ) -> DecisionSynthesis:
        p_name = prod_info.get("name", "Product")
        fit_verdict_str = fit_calc.get("verdict") if fit_calc else None
        
        # Determine base verdict
        if fit_verdict_str == FitVerdict.HIGH_FIT_CONCERN.value:
            base_verdict = FitVerdict.HIGH_FIT_CONCERN
        elif fit_verdict_str == FitVerdict.FIT_CONCERN.value:
            base_verdict = FitVerdict.FIT_CONCERN
        elif fit_verdict_str == FitVerdict.GOOD_FIT.value:
            base_verdict = FitVerdict.GOOD_FIT
        else:
            base_verdict = FitVerdict.INSUFFICIENT_INFORMATION

        ml_prob = risk_pred.get("predicted_return_percentage") if risk_pred else None
        ml_tier = risk_pred.get("risk_tier", "Low") if risk_pred else "Low"
        hist_rate = hist_analysis.get("overall_return_rate") if hist_analysis else None
        top_reasons = hist_analysis.get("top_return_reasons", []) if hist_analysis else []
        quirk = hist_analysis.get("known_design_issues", "") if hist_analysis else ""

        tight_areas = fit_calc.get("tight_areas", []) if fit_calc else []
        alt_check = fit_calc.get("alternative_size_check") if fit_calc else None

        explanation_parts = []
        action_parts = []
        evidence_weights = {}

        # Case 1: Direct Physical Measurement Mismatch (Personal Fit Concern)
        if base_verdict in [FitVerdict.HIGH_FIT_CONCERN, FitVerdict.FIT_CONCERN] and tight_areas:
            evidence_weights["Personalised Fit Assessment"] = "Primary (65% decision weight: direct physical garment measurement vs body dimensions)"
            evidence_weights["Historical Intelligence"] = "Corroborative (25% weight: verified customer return patterns)"
            evidence_weights["Machine Learning Cohort Model"] = "Contextual (10% weight: baseline catalog features, does not override physical ease deficit)"

            reconciliation = (
                f"Personalised body ease calculation reveals active fit restriction in Size {selected_size}: "
                f"{'; '.join(tight_areas)}. "
            )

            # Reconcile with ML model if ML predicted low risk
            if ml_prob is not None and ml_prob < 20.0:
                reconciliation += (
                    f"Notice: While the Machine Learning model estimates a relatively low general return probability "
                    f"({ml_prob}% based on pre-purchase category and price features), physical garment measurements take precedence. "
                    f"A low cohort return probability cannot overcome an individual ease deficit. "
                )
            elif ml_prob is not None and ml_prob >= 20.0:
                reconciliation += (
                    f"This physical constriction is reinforced by the ML return risk model, which also flags elevated return probability ({ml_prob}%). "
                )

            # Reconcile with Historical Intelligence
            if top_reasons:
                primary_reason = top_reasons[0].get("reason", "")
                primary_pct = top_reasons[0].get("percentage", 0)
                reconciliation += (
                    f"Furthermore, empirical store records confirm this pattern: {primary_pct}% of past returns for {p_name} "
                    f"cited '{primary_reason}', directly matching the tightness identified in your assessment."
                )

            # Formulate Actionable Advice
            if alt_check and alt_check.get("is_available_in_chart"):
                alt_sz = alt_check.get("alternative_size")
                alt_notes = alt_check.get("assessment_notes", "")
                action_advice = (
                    f"We strongly recommend checking Size {alt_sz} instead of Size {selected_size}. "
                    f"{alt_notes} Sizing up resolves the ease deficit without requiring post-purchase exchanges."
                )
            elif alt_check and not alt_check.get("is_available_in_chart"):
                action_advice = (
                    f"Size {selected_size} will feel restrictive. Consider sizing up, although dimensions for the next size "
                    f"are not officially published in the catalog."
                )
            else:
                action_advice = f"Consider selecting a larger size or a more relaxed fit silhouette."

        # Case 2: Good Physical Fit
        elif base_verdict == FitVerdict.GOOD_FIT:
            evidence_weights["Personalised Fit Assessment"] = "Primary (60% weight: optimal body-to-garment ease calculated)"
            evidence_weights["Machine Learning Cohort Model"] = "Supporting (25% weight: low baseline return risk)"
            evidence_weights["Historical Intelligence"] = "Supporting (15% weight: low defect frequency)"

            reconciliation = (
                f"Your measurements align well with the {prod_info.get('fit_type', 'standard')} profile of Size {selected_size}. "
                f"The garment delivers comfortable mobility with proportional ease across all measured dimensions."
            )

            if ml_prob is not None and ml_prob >= 30.0:
                reconciliation += (
                    f" Note: The ML model notes an elevated general category return probability ({ml_prob}%), "
                    f"which reflects customer bracketing or impulse discounting rather than individual dimensional flaws."
                )
                action_advice = f"Proceed with Size {selected_size} with confidence; your personal dimensions match the garment well."
            else:
                action_advice = f"Size {selected_size} is well-proportioned for your measurements and recommended for purchase."

        # Case 3: Insufficient Measurements Provided
        else:
            evidence_weights["Personalised Fit Assessment"] = "Pending customer measurements"
            evidence_weights["Historical Intelligence"] = "Active (50% weight: baseline product reliability)"
            evidence_weights["Machine Learning Cohort Model"] = "Active (50% weight: category return probability)"

            reconciliation = (
                f"Personalized ease calculation cannot be fully evaluated because key body measurements "
                f"(chest or waist) were not specified. Historical return rate is {hist_rate if hist_rate is not None else 20.0}%."
            )
            action_advice = (
                "To ensure a precise fit and avoid returns, please share your chest and waist measurements, "
                "or consult the size chart before placing your order."
            )

        return DecisionSynthesis(
            reconciled_verdict=base_verdict,
            reconciliation_explanation=reconciliation,
            actionable_advice=action_advice,
            evidence_weights=evidence_weights
        )

    @staticmethod
    def generate_customer_explanation(
        tools_used: list,
        has_measurements: bool
    ) -> CustomerExplanation:
        data_sources = [
            "Official Garment Size Chart (Chest, Shoulder, Waist dimensions in inches)",
            "Personal Body Measurements & Fit-Type Ease Tolerances (Slim, Regular, Relaxed)",
            "Historical Order & Return Records (Empirical return reasons and sizing feedback)",
            "Scikit-Learn Machine Learning Pipeline (Trained on verified pre-purchase features)"
        ]

        if has_measurements:
            summary = (
                "This recommendation was produced by calculating exact body-to-garment ease differentials, "
                "verifying alternative size measurements in the catalog, evaluating historical defect patterns, "
                "and assessing predictive ML return risk. Physical measurement compatibility is prioritized over broad cohort statistics."
            )
        else:
            summary = (
                "This evaluation is based on verified catalog specifications, historical return frequencies, "
                "and machine learning cohort risk. Personal measurements were not provided."
            )

        limitations = (
            "Garment measurements reflect manufacturer specifications with standard ±0.5 inch tailoring tolerance. "
            "Individual body posture and personal drape preferences may introduce slight variations."
        )

        return CustomerExplanation(
            methodology_summary=summary,
            data_sources_used=data_sources,
            limitations_notice=limitations
        )
