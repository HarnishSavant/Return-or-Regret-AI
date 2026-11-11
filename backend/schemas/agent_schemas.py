from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class FitVerdict(str, Enum):
    GOOD_FIT = "Good Fit"
    FIT_CONCERN = "Fit Concern"
    HIGH_FIT_CONCERN = "High Fit Concern"
    INSUFFICIENT_INFORMATION = "Insufficient Information"

class MeasurementComparisonItem(BaseModel):
    dimension: str
    body_measurement: float
    garment_measurement: float
    ease: float
    unit: str = "inches"
    interpretation: str  # e.g. "Severely Tight (0.0\" ease)", "Optimal Comfort Fit", "Tailored Fit"
    status: str          # "tight", "optimal", "loose", "adequate"

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

class DecisionSynthesis(BaseModel):
    reconciled_verdict: FitVerdict
    reconciliation_explanation: str
    actionable_advice: str
    evidence_weights: Dict[str, str]

class EvidenceSource(BaseModel):
    title: str
    document: str
    confidence: str
    snippet: Optional[str] = None

class CustomerExplanation(BaseModel):
    methodology_summary: str
    data_sources_used: List[str]
    limitations_notice: str

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
