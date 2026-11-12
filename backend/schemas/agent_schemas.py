from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ──────────────────────────────────────────────────────────
# Canonical Agent Intent Enum (Phase 1.2 — 9 Standardized)
# ──────────────────────────────────────────────────────────
class AgentIntent(str, Enum):
    PRODUCT_INFORMATION = "PRODUCT_INFORMATION"
    SIZE_INFORMATION = "SIZE_INFORMATION"
    FIT_RECOMMENDATION = "FIT_RECOMMENDATION"
    RETURN_RISK_PREDICTION = "RETURN_RISK_PREDICTION"
    RETURN_HISTORY_ANALYSIS = "RETURN_HISTORY_ANALYSIS"
    RETURN_POLICY = "RETURN_POLICY"
    PURCHASE_DECISION = "PURCHASE_DECISION"
    GENERAL_PRODUCT_QUESTION = "GENERAL_PRODUCT_QUESTION"
    UNKNOWN_INTENT = "UNKNOWN_INTENT"


# ──────────────────────────────────────────────────────────
# Fit Verdict
# ──────────────────────────────────────────────────────────
class FitVerdict(str, Enum):
    GOOD_FIT = "Good Fit"
    FIT_CONCERN = "Fit Concern"
    HIGH_FIT_CONCERN = "High Fit Concern"
    INSUFFICIENT_INFORMATION = "Insufficient Information"


# ──────────────────────────────────────────────────────────
# Entity Extraction Schemas (Phase 1.2)
# ──────────────────────────────────────────────────────────
class ExtractedEntities(BaseModel):
    """Structured entities extracted from the customer query."""
    product_id: Optional[str] = None
    is_invalid_product_id: bool = False
    requested_size: Optional[str] = None
    chest_measurement: Optional[float] = None
    waist_measurement: Optional[float] = None
    shoulder_measurement: Optional[float] = None
    hip_measurement: Optional[float] = None
    inseam_measurement: Optional[float] = None
    measurement_unit: str = Field(default="inches", description="Unit for all measurements: 'inches' or 'cm' (auto-converted to inches)")
    product_category: Optional[str] = None
    main_question: str = ""
    missing_required_information: List[str] = Field(default_factory=list)

    @field_validator("chest_measurement", "waist_measurement", "shoulder_measurement", "hip_measurement", "inseam_measurement", mode="before")
    @classmethod
    def validate_measurement_range(cls, v: Any) -> Optional[float]:
        if v is None:
            return None
        val = float(v)
        if val <= 0:
            return None  # Reject non-positive values silently
        if val > 200:
            return None  # Reject implausible values (> 200 inches or cm)
        return val


class IntentClassificationResult(BaseModel):
    """Complete classification output from the intent classifier."""
    intent: AgentIntent
    extracted_entities: ExtractedEntities
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    classification_method: str = "deterministic_scoring"
    clarification_required: bool = False
    clarification_question: Optional[str] = None


# ──────────────────────────────────────────────────────────
# Measurement Comparison & Fit Assessment
# ──────────────────────────────────────────────────────────
class MeasurementComparisonItem(BaseModel):
    dimension: str
    body_measurement: float
    garment_measurement: float
    ease: float
    unit: str = "inches"
    interpretation: str
    status: str  # "tight", "optimal", "loose", "adequate"


class AlternativeSizeEvaluation(BaseModel):
    alternative_size: str
    is_available_in_chart: bool
    dimensions: Optional[Dict[str, float]] = None
    ease_analysis: Optional[Dict[str, float]] = None
    assessment_notes: str


class FitAssessment(BaseModel):
    verdict: FitVerdict
    confidence: float
    fit_type: str
    tight_areas: List[str] = Field(default_factory=list)
    loose_areas: List[str] = Field(default_factory=list)
    measurement_comparison: List[MeasurementComparisonItem] = Field(default_factory=list)
    alternative_size_check: Optional[AlternativeSizeEvaluation] = None
    summary: str


# ──────────────────────────────────────────────────────────
# ML Prediction & Historical Intelligence
# ──────────────────────────────────────────────────────────
class MLPredictionOutput(BaseModel):
    predicted_return_probability: float
    predicted_return_percentage: float
    risk_tier: str       # "Low", "Medium", "High"
    model_name: str
    key_contributing_signals: List[str] = Field(default_factory=list)
    limitations: str


class HistoricalIntelligence(BaseModel):
    total_orders_analyzed: int
    overall_return_rate: float
    category_baseline_rate: float
    risk_category: str
    top_return_reasons: List[Dict[str, Any]] = Field(default_factory=list)
    known_design_issues: str
    representative_feedback: List[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────
# Decision Synthesis
# ──────────────────────────────────────────────────────────
class DecisionSynthesis(BaseModel):
    reconciled_verdict: FitVerdict
    reconciliation_explanation: str
    actionable_advice: str
    evidence_weights: Dict[str, str]


# ──────────────────────────────────────────────────────────
# Evidence & Explanation
# ──────────────────────────────────────────────────────────
class EvidenceSource(BaseModel):
    title: str
    document: str
    confidence: str
    snippet: Optional[str] = None


class CustomerExplanation(BaseModel):
    methodology_summary: str
    data_sources_used: List[str]
    limitations_notice: str


# ──────────────────────────────────────────────────────────
# Agent Response (API Contract)
# ──────────────────────────────────────────────────────────
class AgentResponse(BaseModel):
    intent: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    selected_size: Optional[str] = None
    summary_message: str
    verdict: Optional[FitVerdict] = None
    fit_assessment: Optional[FitAssessment] = None
    measurement_comparison: Optional[List[MeasurementComparisonItem]] = None
    ml_prediction: Optional[MLPredictionOutput] = None
    historical_analysis: Optional[HistoricalIntelligence] = None
    decision_synthesis: Optional[DecisionSynthesis] = None
    final_recommendation: str
    evidence_sources: List[EvidenceSource] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    customer_explanation: CustomerExplanation
    tools_executed: List[str] = Field(default_factory=list)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
