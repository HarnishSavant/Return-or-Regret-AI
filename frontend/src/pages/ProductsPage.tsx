import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Shirt,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  X,
  Ruler,
  Info,
  Sparkles,
  Bot
} from 'lucide-react';
import { api } from '../services/api';
import { Product } from '../types';

interface ProductsPageProps {
  onNavigateToAssistant: (productId: string) => void;
}

const CATEGORIES = ['All', 'Shirts', 'T-Shirts', 'Jeans', 'Pants', 'Dresses', 'Outerwear', 'Footwear', 'Activewear'];
const RISKS = ['All', 'Low Risk', 'Medium Risk', 'High Risk'];

export const ProductsPage: React.FC<ProductsPageProps> = ({ onNavigateToAssistant }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [risk, setRisk] = useState('All');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const data = await api.getProducts({ category, risk, search });
      setProducts(data);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [category, risk]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchProducts();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Product Intelligence</h1>
          <p className="text-xs text-slate-500 mt-1">
            Verified apparel catalog with historical return rates, size chart specifications, and design diagnostics.
          </p>
        </div>
        <div className="text-xs text-slate-500 font-medium">
          Showing <span className="font-bold text-slate-900">{products.length}</span> styles
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by product name, ID (e.g. P001), material or fit..."
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-xs bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 text-slate-800"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-medium hover:bg-slate-800 transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 text-xs">
          {/* Category Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-slate-400 font-medium text-[11px] mr-1">Category:</span>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategory(cat)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                  category === cat
                    ? 'bg-orange-500 text-white shadow-2xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Risk Level Pills */}
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400 font-medium text-[11px] mr-1">Risk:</span>
            {RISKS.map((r) => (
              <button
                key={r}
                onClick={() => setRisk(r)}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  risk === r
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Product Grid */}
      {loading ? (
        <div className="text-center py-20 text-xs text-slate-400">Loading catalog items...</div>
      ) : products.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200 p-8">
          <Shirt className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <h3 className="font-semibold text-sm text-slate-700">No products match your filter criteria</h3>
          <p className="text-xs text-slate-400 mt-1">Try resetting the category or search keyword.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {products.map((prod) => (
            <div
              key={prod.product_id}
              className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col hover:border-slate-300 transition-all hover:shadow-md group"
            >
              {/* Product Thumbnail */}
              <div className="relative h-48 bg-slate-100 overflow-hidden">
                <img
                  src={prod.image_url}
                  alt={prod.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-3 left-3 flex items-center space-x-1.5">
                  <span className="px-2 py-0.5 rounded-md bg-slate-900/80 backdrop-blur-md text-white font-mono text-[10px] font-bold">
                    {prod.product_id}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-white/90 backdrop-blur-md text-slate-800 text-[10px] font-semibold">
                    {prod.fit_type}
                  </span>
                </div>
                <div className="absolute top-3 right-3">
                  <span
                    className={`px-2 py-0.5 rounded-md text-[10px] font-bold backdrop-blur-md shadow-sm ${
                      prod.risk_category === 'High Risk'
                        ? 'bg-red-500/90 text-white'
                        : prod.risk_category === 'Medium Risk'
                        ? 'bg-amber-500/90 text-white'
                        : 'bg-emerald-500/90 text-white'
                    }`}
                  >
                    {prod.risk_category} ({prod.historical_return_rate ? Math.round(prod.historical_return_rate * 100) : 20}%)
                  </span>
                </div>
              </div>

              {/* Product Details */}
              <div className="p-4 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                      {prod.category}
                    </span>
                    <span className="text-sm font-bold text-slate-900">${prod.price.toFixed(2)}</span>
                  </div>

                  <h3 className="font-semibold text-sm text-slate-900 mt-1 line-clamp-1">{prod.name}</h3>

                  <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                    {prod.description}
                  </p>

                  <div className="mt-2.5 text-[11px] text-slate-600">
                    <span className="font-medium text-slate-800">Material:</span> {prod.material}
                  </div>

                  {/* Available Sizes Pills */}
                  <div className="mt-3 flex items-center space-x-1.5 flex-wrap gap-y-1">
                    <span className="text-[10px] text-slate-400 mr-1">Sizes:</span>
                    {prod.sizes.map((s) => (
                      <span
                        key={s}
                        className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-mono font-medium border border-slate-200/60"
                      >
                        {s}
                      </span>
                    ))}
                  </div>

                  {/* Known fit quirk notice */}
                  {prod.known_fit_quirks && (
                    <div className="mt-3 p-2 rounded-lg bg-orange-50/70 border border-orange-200/50 text-[10px] text-orange-950 line-clamp-2">
                      <span className="font-semibold text-orange-700">Fit Note: </span>
                      {prod.known_fit_quirks}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedProduct(prod)}
                    className="flex-1 py-1.5 px-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors text-center"
                  >
                    Size Chart &amp; Specs
                  </button>
                  <button
                    onClick={() => onNavigateToAssistant(prod.product_id)}
                    className="flex-1 py-1.5 px-2 rounded-lg bg-orange-500 hover:bg-orange-600 text-white text-xs font-medium transition-colors flex items-center justify-center space-x-1 shadow-sm"
                  >
                    <Bot size={13} />
                    <span>Consult AI</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Product Detail & Size Chart Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200 shadow-xl flex flex-col">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white z-10">
              <div className="flex items-center space-x-3">
                <span className="px-2 py-0.5 rounded bg-slate-900 text-white font-mono text-xs font-bold">
                  {selectedProduct.product_id}
                </span>
                <div>
                  <h3 className="font-semibold text-sm text-slate-900">{selectedProduct.name}</h3>
                  <span className="text-xs text-slate-500">{selectedProduct.category} &bull; ${selectedProduct.price}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedProduct(null)}
                className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5">
              <div>
                <h4 className="font-semibold text-xs text-slate-800 uppercase tracking-wider mb-2">
                  Garment Size Chart (Actual Dimensions in Inches)
                </h4>
                {selectedProduct.size_chart && Object.keys(selectedProduct.size_chart).length > 0 ? (
                  <div className="overflow-x-auto rounded-xl border border-slate-200">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px]">
                        <tr>
                          <th className="p-2.5 font-medium">Size</th>
                          {Object.keys(Object.values(selectedProduct.size_chart)[0] || {}).map((dim) => (
                            <th key={dim} className="p-2.5 font-medium capitalize">{dim}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {Object.entries(selectedProduct.size_chart).map(([sz, dims]) => (
                          <tr key={sz} className="hover:bg-slate-50 font-mono">
                            <td className="p-2.5 font-bold text-slate-900 font-sans">{sz}</td>
                            {Object.values(dims).map((val, idx) => (
                              <td key={idx} className="p-2.5 text-slate-700">{val}"</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs">
                    ⚠️ Official size chart is pending publication for this style. AI Assistant uses category fallback tolerances.
                  </div>
                )}
              </div>

              {/* Fabric & Fit Diagnostics */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Material &amp; Care</span>
                  <div className="font-medium text-slate-800">{selectedProduct.material}</div>
                  <div className="text-slate-500 text-[11px] mt-1">{selectedProduct.care_instructions}</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Return Diagnostic</span>
                  <div className="font-semibold text-orange-600">
                    {selectedProduct.historical_return_rate ? Math.round(selectedProduct.historical_return_rate * 100) : 25}% Return Baseline
                  </div>
                  <div className="text-slate-600 text-[11px] mt-1">
                    {selectedProduct.known_fit_quirks || 'No abnormal return patterns recorded.'}
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-end space-x-2 sticky bottom-0">
              <button
                onClick={() => setSelectedProduct(null)}
                className="px-4 py-2 rounded-lg border border-slate-200 hover:bg-white text-slate-700 text-xs font-medium"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const pid = selectedProduct.product_id;
                  setSelectedProduct(null);
                  onNavigateToAssistant(pid);
                }}
                className="px-4 py-2 rounded-lg bg-orange-500 hover:bg-orange-600 text-white text-xs font-medium flex items-center space-x-1.5 shadow-sm"
              >
                <Bot size={14} />
                <span>Test Fit with AI Assistant</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

