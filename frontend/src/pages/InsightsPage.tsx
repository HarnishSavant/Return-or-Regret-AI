import React, { useState, useEffect } from 'react';
import {
  Lightbulb,
  CheckCircle,
  XCircle,
  Clock,
  Sparkles,
  AlertTriangle,
  FileQuestion,
  ArrowRight,
  TrendingUp,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { AISuggestion } from '../types';

export const InsightsPage: React.FC = () => {
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [missingInfo, setMissingInfo] = useState<any[]>([]);
  const [fitProblems, setFitProblems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const res = await api.getInsights();
      setSuggestions(res.ai_suggestions);
      setMissingInfo(res.missing_info_audit);
      setFitProblems(res.repeated_fit_problems);
    } catch (err) {
      console.error('Failed to load insights:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleApproveReject = async (id: string, action: 'approve' | 'reject') => {
    setActionInProgress(id);
    try {
      await api.approveSuggestion(id, action);
      setSuggestions(prev =>
        prev.map(s => (s.id === id ? { ...s, status: action === 'approve' ? 'approved' : 'rejected' } : s))
      );
    } catch (err) {
      console.error('Failed to update suggestion status:', err);
    } finally {
      setActionInProgress(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Philosophy Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-slate-700/60">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-orange-500/20 text-orange-400 text-[11px] font-semibold mb-2 border border-orange-500/30">
            <Sparkles size={12} />
            <span>Root-Cause Return Prevention</span>
          </div>
          <h2 className="text-xl font-bold tracking-tight">"Fix the Product Page, Not the Customer."</h2>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
            Avoidable returns are caused by information deficits on the product page — missing shoulder specs, uncommunicated non-stretch fabrics, or unclear fit drape. Never penalise customers for legitimate sizing uncertainty.
          </p>
        </div>
        <button
          onClick={fetchInsights}
          className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 flex items-center space-x-1.5 shrink-0"
        >
          <RefreshCw size={13} />
          <span>Refresh Audit</span>
        </button>
      </div>

      {/* Main Section: AI Suggested Product Improvements */}
      <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
        <div>
          <h3 className="font-semibold text-sm text-slate-900">
            AI-Generated Product Page Improvements (Pending Human Approval)
          </h3>
          <p className="text-xs text-slate-500">
            Automated recommendations derived from customer return feedback clusters and sizing friction points.
          </p>
        </div>

        {loading ? (
          <div className="text-center py-10 text-xs text-slate-400">Auditing product telemetry...</div>
        ) : (
          <div className="space-y-3">
            {suggestions.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold px-1.5 py-0.5 rounded bg-slate-900 text-white">
                      {item.product_id}
                    </span>
                    <span className="font-semibold text-xs text-slate-900">{item.product_name}</span>
                    <span className="text-[10px] text-slate-400">&bull;</span>
                    <span className="text-[11px] text-slate-500">{item.category}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        item.severity === 'Critical'
                          ? 'bg-red-100 text-red-800'
                          : item.severity === 'High'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {item.severity}
                    </span>
                  </div>

                  <div className="text-xs text-slate-700">
                    <span className="font-semibold text-slate-900">Trigger:</span> {item.trigger_issue}
                  </div>

                  <div className="text-xs text-slate-800 bg-white p-2.5 rounded-lg border border-slate-200/80">
                    <span className="font-semibold text-orange-600 block text-[11px] mb-0.5">Proposed PDP Change:</span>
                    {item.ai_suggested_action}
                  </div>

                  <div className="text-[11px] text-emerald-700 font-medium">
                    ⚡ Estimated Impact: {item.estimated_impact}
                  </div>
                </div>

                {/* Status & Approval Actions */}
                <div className="flex flex-col sm:flex-row items-end sm:items-center space-y-2 sm:space-y-0 sm:space-x-2 shrink-0">
                  {item.status === 'approved' ? (
                    <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-semibold flex items-center space-x-1 border border-emerald-200">
                      <CheckCircle size={14} />
                      <span>Approved for Production</span>
                    </span>
                  ) : item.status === 'rejected' ? (
                    <span className="px-3 py-1 rounded-full bg-slate-200 text-slate-600 text-xs font-semibold flex items-center space-x-1">
                      <XCircle size={14} />
                      <span>Rejected</span>
                    </span>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleApproveReject(item.id, 'reject')}
                        disabled={actionInProgress === item.id}
                        className="px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-100 text-slate-600 text-xs font-medium transition-colors"
                      >
                        Dismiss
                      </button>
                      <button
                        onClick={() => handleApproveReject(item.id, 'approve')}
                        disabled={actionInProgress === item.id}
                        className="px-3.5 py-1.5 rounded-lg bg-orange-500 hover:bg-orange-600 text-white text-xs font-medium transition-colors flex items-center space-x-1 shadow-sm"
                      >
                        <CheckCircle size={13} />
                        <span>Approve Fix</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Audits Row: Repeated Fit Issues & Missing Specs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Repeated Fit Problems */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center space-x-2">
            <AlertTriangle size={16} className="text-red-500" />
            <h3 className="font-semibold text-sm text-slate-900">Repeated Fit Complaints Audit</h3>
          </div>
          <p className="text-xs text-slate-500">Products demonstrating clustered return reason patterns</p>

          <div className="space-y-2 mt-2">
            {fitProblems.map((p) => (
              <div key={p.product_id} className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs">
                <div className="flex items-center justify-between font-semibold text-slate-900 mb-1">
                  <span>{p.product_id} — {p.name}</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-red-100 text-red-800">{p.risk_level}</span>
                </div>
                <div className="text-slate-600 text-[11px] leading-relaxed">{p.fit_issue}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Missing Information Audit */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center space-x-2">
            <FileQuestion size={16} className="text-amber-500" />
            <h3 className="font-semibold text-sm text-slate-900">Missing Information Inventory</h3>
          </div>
          <p className="text-xs text-slate-500">Products with incomplete specification sheets or omitted size charts</p>

          <div className="space-y-2 mt-2">
            {missingInfo.map((p) => (
              <div key={p.product_id} className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs">
                <div className="flex items-center justify-between font-semibold text-slate-900 mb-1">
                  <span>{p.product_id} — {p.name}</span>
                  <span className="text-[10px] text-orange-600 font-bold">{p.historical_return_rate}% Return Rate</span>
                </div>
                <div className="text-slate-600 text-[11px]">
                  <span className="text-amber-700 font-semibold">Missing: </span>
                  {p.missing_item} (Description completeness: {p.completeness_score}%)
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

