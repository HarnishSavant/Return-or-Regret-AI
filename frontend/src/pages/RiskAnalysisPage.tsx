import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Cpu,
  Sparkles,
  Sliders,
  CheckCircle,
  TrendingUp,
  Info,
  ArrowRight,
  Bot
} from 'lucide-react';
import { api } from '../services/api';
import { Product } from '../types';

interface RiskAnalysisPageProps {
  onNavigateToAssistant: (productId: string) => void;
}

export const RiskAnalysisPage: React.FC<RiskAnalysisPageProps> = ({ onNavigateToAssistant }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductId, setSelectedProductId] = useState('P001');
  const [selectedSize, setSelectedSize] = useState('M');
  const [bracketingOrder, setBracketingOrder] = useState(false);
  const [discountApplied, setDiscountApplied] = useState(0.0);

  const [loading, setLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState<any>(null);

  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const prods = await api.getProducts();
        setProducts(prods);
        if (prods.length > 0) {
          setSelectedProductId(prods[0].product_id);
          setSelectedSize(prods[0].sizes[0] || 'M');
        }
      } catch (err) {
        console.error('Failed to load products for risk analysis:', err);
      }
    };
    fetchCatalog();
  }, []);

  const curProduct = products.find(p => p.product_id === selectedProductId);

  // Update selected size when product changes
  useEffect(() => {
    if (curProduct && !curProduct.sizes.includes(selectedSize)) {
      setSelectedSize(curProduct.sizes[0] || 'M');
    }
  }, [selectedProductId, curProduct]);

  const handleRunPrediction = async () => {
    setLoading(true);
    try {
      const res = await api.predictRisk({
        product_id: selectedProductId,
        selected_size: selectedSize,
        bracketing_order: bracketingOrder,
        discount_applied: discountApplied
      });
      setPredictionResult(res);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Run initial prediction when product loaded
  useEffect(() => {
    if (products.length > 0) {
      handleRunPrediction();
    }
  }, [selectedProductId, selectedSize, bracketingOrder, discountApplied]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Return Risk Analysis</h1>
        <p className="text-xs text-slate-500 mt-1">
          Evaluate pre-purchase return probability using trained Scikit-learn predictive models and historical return signals.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Feature Selection Form */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-5">
          <div>
            <h3 className="font-semibold text-xs text-slate-800 uppercase tracking-wider mb-3">
              Pre-Purchase Feature Configuration
            </h3>

            {/* Product Select */}
            <div className="space-y-1.5 mb-4">
              <label className="text-xs font-medium text-slate-700">Product</label>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
              >
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_id} — {p.name} ({p.fit_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Size Select */}
            <div className="space-y-1.5 mb-4">
              <label className="text-xs font-medium text-slate-700">Selected Size</label>
              <div className="flex flex-wrap gap-2">
                {curProduct?.sizes.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setSelectedSize(s)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                      selectedSize === s
                        ? 'bg-orange-500 text-white shadow-2xs'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Discount Slider */}
            <div className="space-y-1.5 mb-4">
              <div className="flex justify-between text-xs">
                <span className="font-medium text-slate-700">Promotional Discount</span>
                <span className="font-semibold text-slate-900">{Math.round(discountApplied * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.4"
                step="0.05"
                value={discountApplied}
                onChange={(e) => setDiscountApplied(parseFloat(e.target.value))}
                className="w-full accent-orange-500 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
              />
              <span className="text-[10px] text-slate-400 block">
                Discounts &gt;20% elevate impulsive return risk by 5-8%.
              </span>
            </div>

            {/* Bracketing Checkbox */}
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 mb-4">
              <label className="flex items-start space-x-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={bracketingOrder}
                  onChange={(e) => setBracketingOrder(e.target.checked)}
                  className="mt-0.5 rounded border-slate-300 text-orange-500 focus:ring-orange-500"
                />
                <div className="text-xs">
                  <span className="font-semibold text-slate-800 block">Bracketing Purchase Intent</span>
                  <span className="text-slate-500 text-[11px] leading-tight block mt-0.5">
                    Customer is ordering 2 or more sizes of this item simultaneously with the intention of returning one.
                  </span>
                </div>
              </label>
            </div>

            <button
              onClick={handleRunPrediction}
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-medium text-xs shadow-sm flex items-center justify-center space-x-2 transition-all"
            >
              <Cpu size={14} />
              <span>{loading ? 'Evaluating Model...' : 'Re-evaluate ML Prediction'}</span>
            </button>
          </div>

          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-400">
            <span className="font-semibold text-slate-700 block mb-1">Target Separation Principle:</span>
            Only pre-purchase attributes (fit silhouette, size availability, description completeness, discount, bracketing) are fed into the model. Never post-purchase return reasons.
          </div>
        </div>

        {/* Right 2 Columns: Prediction Output & Explainable Breakdown */}
        <div className="lg:col-span-2 space-y-6">
          {predictionResult ? (
            <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-6">
              {/* Score Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-100">
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Model Prediction Output
                  </span>
                  <h3 className="text-lg font-bold text-slate-900 mt-0.5">
                    {predictionResult.product_name} &bull; Size {predictionResult.selected_size}
                  </h3>
                  <div className="flex items-center space-x-2 mt-1 text-xs text-slate-500">
                    <span>Model: <span className="font-semibold text-slate-700">{predictionResult.ml_model_used}</span></span>
                    <span>&bull;</span>
                    <span className="text-emerald-600 font-medium">Valid Inference</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Predicted Return Risk</span>
                    <div className="text-3xl font-extrabold text-slate-900">
                      {predictionResult.predicted_return_percentage}%
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1.5 rounded-xl font-bold text-xs uppercase tracking-wider ${
                      predictionResult.risk_level === 'High'
                        ? 'bg-red-50 text-red-700 border border-red-200'
                        : predictionResult.risk_level === 'Medium'
                        ? 'bg-amber-50 text-amber-700 border border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}
                  >
                    {predictionResult.risk_level} Risk
                  </span>
                </div>
              </div>

              {/* Visual Probability Bar */}
              <div>
                <div className="flex justify-between text-xs text-slate-500 mb-1.5 font-medium">
                  <span>0% (Virtually Zero Return)</span>
                  <span className="font-semibold text-slate-800">{predictionResult.predicted_return_percentage}% Risk</span>
                  <span>100% (Definite Return)</span>
                </div>
                <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden p-0.5">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      predictionResult.risk_level === 'High'
                        ? 'bg-gradient-to-r from-amber-500 to-red-500'
                        : predictionResult.risk_level === 'Medium'
                        ? 'bg-gradient-to-r from-blue-500 to-amber-500'
                        : 'bg-gradient-to-r from-emerald-500 to-teal-500'
                    }`}
                    style={{ width: `${Math.min(predictionResult.predicted_return_percentage, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Contributing Product-Level Signals */}
              <div>
                <h4 className="font-semibold text-xs text-slate-800 uppercase tracking-wider mb-2.5">
                  Key Contributing Risk Signals
                </h4>
                <div className="space-y-2">
                  {predictionResult.key_contributing_signals?.map((sig: string, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs text-slate-700 flex items-start space-x-2"
                    >
                      <span className="text-orange-500 font-bold shrink-0 mt-0.5">&bull;</span>
                      <span className="leading-relaxed">{sig}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommended Preventive Actions */}
              <div className="p-4 rounded-xl bg-orange-50/70 border border-orange-200/80">
                <div className="flex items-center space-x-2 text-xs font-semibold text-orange-900 mb-1">
                  <Sparkles size={14} className="text-orange-600" />
                  <span>Recommended Return Prevention Action:</span>
                </div>
                <p className="text-xs text-orange-950 leading-relaxed">
                  {predictionResult.risk_level === 'High'
                    ? `Size ${predictionResult.selected_size} exhibits high fit volatility. Suggest displaying shoulder-width alert and asking customer to confirm body measurements prior to checkout.`
                    : predictionResult.risk_level === 'Medium'
                    ? `Promote single-size purchase confidence by offering complimentary size exchange guarantee if needed.`
                    : `Low return risk detected. Garment specifications and sizing guide are well calibrated for Size ${predictionResult.selected_size}.`}
                </p>

                <div className="mt-3 flex justify-end">
                  <button
                    onClick={() => onNavigateToAssistant(predictionResult.product_id)}
                    className="px-3 py-1.5 rounded-lg bg-orange-600 hover:bg-orange-700 text-white text-xs font-medium flex items-center space-x-1.5 transition-colors shadow-2xs"
                  >
                    <Bot size={13} />
                    <span>Open in AI Shopping Assistant</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 bg-white rounded-xl border border-slate-200 p-8">
              <ShieldAlert className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <h3 className="font-semibold text-sm text-slate-700">Select parameters to run ML analysis</h3>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

