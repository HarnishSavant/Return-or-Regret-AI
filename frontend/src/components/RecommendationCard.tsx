import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  HelpCircle,
  Cpu,
  BarChart3,
  Ruler,
  BookOpen,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  Info
} from 'lucide-react';
import { StructuredAgentResponse, FitVerdict } from '../types';

interface RecommendationCardProps {
  response: StructuredAgentResponse;
  onSelectSize?: (size: string) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  response,
  onSelectSize
}) => {
  const [showExplanation, setShowExplanation] = useState(false);

  const verdict = response.verdict;
  const fitAssessment = response.fit_assessment;
  const compItems = response.measurement_comparison || [];
  const mlPred = response.ml_prediction;
  const hist = response.historical_analysis;
  const decision = response.decision_synthesis;
  const explanation = response.customer_explanation;
  const altCheck = fitAssessment?.alternative_size_check;

  // Verdict style mapper
  const getVerdictBadge = (v?: FitVerdict) => {
    switch (v) {
      case 'Good Fit':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-800',
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />,
          title: 'Good Fit Recommended',
          sub: 'Body measurements align comfortably with garment specifications.'
        };
      case 'Fit Concern':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-900',
          icon: <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />,
          title: 'Fit Concern Identified',
          sub: 'Notable ease variance detected in one or more dimensions.'
        };
      case 'High Fit Concern':
        return {
          bg: 'bg-orange-500/10 border-orange-500/30 text-orange-950',
          icon: <AlertCircle className="w-5 h-5 text-orange-600 shrink-0" />,
          title: 'High Fit Concern — Restriction Detected',
          sub: 'Active physical constriction detected. High probability of size-related return.'
        };
      default:
        return {
          bg: 'bg-slate-500/10 border-slate-500/30 text-slate-800',
          icon: <HelpCircle className="w-5 h-5 text-slate-500 shrink-0" />,
          title: 'Information Incomplete',
          sub: 'Enter customer chest and waist measurements to calculate personalized ease.'
        };
    }
  };

  const badgeStyle = getVerdictBadge(verdict);

  return (
    <div className="space-y-4 my-2">
      {/* 1. Prominent Personalized Fit Verdict Card */}
      {verdict && (
        <div className={`p-4 rounded-xl border ${badgeStyle.bg} shadow-2xs`}>
          <div className="flex items-start space-x-3">
            {badgeStyle.icon}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm">{badgeStyle.title}</span>
                {response.selected_size && (
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-white/80 border border-current font-bold">
                    Size {response.selected_size}
                  </span>
                )}
              </div>
              <p className="text-xs mt-0.5 opacity-90 leading-relaxed">
                {response.summary_message}
              </p>
            </div>
          </div>

          {/* Verified Alternative Size Suggestion Button */}
          {altCheck && altCheck.is_available_in_chart && (
            <div className="mt-3 pt-3 border-t border-current/15 flex items-center justify-between">
              <div className="text-[11px] leading-tight pr-2">
                <span className="font-semibold block">Verified Alternative Size:</span>
                <span>{altCheck.assessment_notes}</span>
              </div>
              {onSelectSize && (
                <button
                  onClick={() => onSelectSize(altCheck.alternative_size)}
                  className="px-3 py-1.5 rounded-lg bg-orange-600 hover:bg-orange-700 text-white font-medium text-xs flex items-center space-x-1 shrink-0 shadow-sm transition-all"
                >
                  <span>Switch to Size {altCheck.alternative_size}</span>
                  <ArrowRight size={13} />
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* 2. Measurement & Ease Comparison Table */}
      {compItems.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden">
          <div className="px-4 py-2.5 bg-slate-50 border-b border-slate-200/80 flex items-center justify-between">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-800">
              <Ruler size={14} className="text-orange-500" />
              <span>Garment vs Body Ease Comparison (Inches)</span>
            </div>
            <span className="text-[10px] text-slate-500 font-medium">
              Profile: {fitAssessment?.fit_type}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-[10px] text-slate-500 uppercase tracking-wider bg-slate-50/50">
                  <th className="py-2 px-3 font-medium">Dimension</th>
                  <th className="py-2 px-3 font-medium">Your Body</th>
                  <th className="py-2 px-3 font-medium">Garment Dimension</th>
                  <th className="py-2 px-3 font-medium">Calculated Ease</th>
                  <th className="py-2 px-3 font-medium">Assessment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                {compItems.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-2 px-3 font-sans font-semibold text-slate-900">{item.dimension}</td>
                    <td className="py-2 px-3 text-slate-700">{item.body_measurement.toFixed(1)}"</td>
                    <td className="py-2 px-3 text-slate-700">{item.garment_measurement.toFixed(1)}"</td>
                    <td className="py-2 px-3 font-bold">
                      <span className={item.ease < 1.0 ? 'text-red-600' : 'text-emerald-600'}>
                        {item.ease >= 0 ? `+${item.ease.toFixed(1)}"` : `${item.ease.toFixed(1)}"`}
                      </span>
                    </td>
                    <td className="py-2 px-3 font-sans">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          item.status === 'tight'
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : item.status === 'loose'
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                      >
                        {item.interpretation}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 3. Multi-Pillar Intelligence Grid (ML Risk & Historical Intelligence) */}
      {(mlPred || hist) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* ML Cohort Return Prediction Card */}
          {mlPred && (
            <div className="p-3.5 rounded-xl bg-white border border-slate-200/90 shadow-2xs space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-900">
                  <Cpu size={14} className="text-orange-500" />
                  <span>ML Return Risk</span>
                </div>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                    mlPred.risk_tier === 'High'
                      ? 'bg-red-50 text-red-700'
                      : mlPred.risk_tier === 'Medium'
                      ? 'bg-amber-50 text-amber-700'
                      : 'bg-emerald-50 text-emerald-700'
                  }`}
                >
                  {mlPred.risk_tier} Risk ({mlPred.predicted_return_percentage}%)
                </span>
              </div>

              <div className="text-[11px] text-slate-600 space-y-1">
                <div>
                  <span className="font-medium text-slate-700">Model:</span> {mlPred.model_name}
                </div>
                {mlPred.key_contributing_signals?.length > 0 && (
                  <div>
                    <span className="font-medium text-slate-700">Signal:</span> {mlPred.key_contributing_signals[0]}
                  </div>
                )}
                <div className="text-[10px] text-slate-400 italic pt-1 border-t border-slate-100">
                  {mlPred.limitations}
                </div>
              </div>
            </div>
          )}

          {/* Historical Product Intelligence Card */}
          {hist && (
            <div className="p-3.5 rounded-xl bg-white border border-slate-200/90 shadow-2xs space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-900">
                  <BarChart3 size={14} className="text-blue-500" />
                  <span>Historical Store Intelligence</span>
                </div>
                <span className="text-[11px] font-bold text-slate-800">
                  {hist.overall_return_rate}% Return Rate
                </span>
              </div>

              <div className="text-[11px] text-slate-600 space-y-1">
                <div>
                  <span className="font-medium text-slate-700">Analyzed:</span> {hist.total_orders_analyzed} orders (vs {hist.category_baseline_rate}% category baseline)
                </div>
                {hist.top_return_reasons?.length > 0 && (
                  <div>
                    <span className="font-medium text-slate-700">Top Reason:</span> {hist.top_return_reasons[0].reason} ({hist.top_return_reasons[0].percentage}%)
                  </div>
                )}
                {hist.known_design_issues && hist.known_design_issues !== 'None reported' && (
                  <div className="text-[10px] text-orange-900 bg-orange-50/80 p-1.5 rounded border border-orange-200/60">
                    <span className="font-semibold text-orange-700">Verified Quirk:</span> {hist.known_design_issues}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. Final Actionable Recommendation Banner */}
      {response.final_recommendation && (
        <div className="p-3.5 rounded-xl bg-slate-900 text-white shadow-sm space-y-1.5">
          <div className="flex items-center space-x-1.5 text-xs font-semibold text-orange-400">
            <Sparkles size={14} />
            <span>Final Shopping Recommendation</span>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed font-medium">
            {response.final_recommendation}
          </p>
        </div>
      )}

      {/* 5. Grounded Citations & Sources */}
      {response.evidence_sources && response.evidence_sources.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[11px]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mr-1">
            Verified Sources:
          </span>
          {response.evidence_sources.map((s, idx) => (
            <span
              key={idx}
              className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-medium border border-slate-200 transition-colors"
              title={s.snippet || s.document}
            >
              <BookOpen size={11} className="text-orange-500" />
              <span>{s.title}</span>
            </span>
          ))}
        </div>
      )}

      {/* 6. Expandable Customer-Friendly Explanation (NO Raw Python Traces) */}
      {explanation && (
        <div className="pt-2 border-t border-slate-100">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="flex items-center justify-between w-full text-[11px] font-medium text-slate-500 hover:text-slate-800 transition-colors"
          >
            <div className="flex items-center space-x-1">
              <Info size={13} className="text-slate-400" />
              <span>How was this recommendation generated?</span>
            </div>
            {showExplanation ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {showExplanation && (
            <div className="mt-2 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-2 leading-relaxed">
              <p className="font-medium text-slate-900">
                {explanation.methodology_summary}
              </p>
              <div>
                <span className="font-semibold block text-[11px] text-slate-600 mb-1">Data Pillars Evaluated:</span>
                <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-slate-600">
                  {explanation.data_sources_used.map((src, i) => (
                    <li key={i}>{src}</li>
                  ))}
                </ul>
              </div>
              <p className="text-[10px] text-slate-400 pt-1 border-t border-slate-200/60">
                {explanation.limitations_notice}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
