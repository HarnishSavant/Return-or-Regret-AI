import React, { useEffect, useState } from 'react';
import {
  Package,
  ShoppingCart,
  TrendingDown,
  AlertTriangle,
  Bot,
  Percent,
  ArrowUpRight,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid
} from 'recharts';
import { api } from '../services/api';
import { DashboardSummary } from '../types';

interface DashboardPageProps {
  onNavigate: (route: string) => void;
}

const PIE_COLORS = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#64748b'];

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getDashboardSummary();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3">
        <RefreshCw className="w-8 h-8 text-orange-500 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Loading live executive dashboard metrics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 rounded-xl bg-red-50 border border-red-200 text-red-700">
        <h3 className="font-semibold text-sm">Failed to connect to backend</h3>
        <p className="text-xs mt-1">{error}</p>
        <button
          onClick={fetchDashboard}
          className="mt-3 px-3 py-1.5 rounded-lg bg-red-600 text-white text-xs font-medium hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Title & Status */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Executive Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time returns prevention telemetry, AI agent decision logs & ML risk evaluation.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[11px] px-2.5 py-1 rounded-md bg-amber-50 text-amber-800 border border-amber-200/80 font-medium">
            Synthetic Academic Callset (920 Orders)
          </span>
          <button
            onClick={fetchDashboard}
            className="p-2 rounded-lg bg-white border border-slate-200/80 hover:bg-slate-50 text-slate-600 transition-colors shadow-sm"
            title="Refresh Metrics"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-600">Total Products</span>
            <Package size={16} className="text-blue-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{data.total_products}</div>
          <div className="mt-1 text-[11px] text-slate-500">18 catalog styles</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-600">Orders Analysed</span>
            <ShoppingCart size={16} className="text-emerald-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{data.total_orders_analyzed}</div>
          <div className="mt-1 text-[11px] text-slate-500">Historical dataset</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-600">Return Rate</span>
            <Percent size={16} className="text-orange-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{data.overall_return_rate}%</div>
          <div className="mt-1 text-[11px] text-orange-600 font-medium">Global benchmark</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm border-l-4 border-l-orange-500">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-600">Avoidable Returns</span>
            <TrendingDown size={16} className="text-orange-600" />
          </div>
          <div className="mt-2 text-2xl font-bold text-orange-600">{data.avoidable_return_rate}%</div>
          <div className="mt-1 text-[11px] text-slate-500">Sizing & fit causes</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-600">High Risk Items</span>
            <ShieldAlert size={16} className="text-red-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-red-600">{data.high_risk_product_count}</div>
          <div className="mt-1 text-[11px] text-slate-500">&gt;30% return baseline</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium text-slate-600">AI Agent Queries</span>
            <Bot size={16} className="text-purple-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-purple-600">{data.total_agent_interactions}</div>
          <div className="mt-1 text-[11px] text-slate-500">Tool workflows logged</div>
        </div>
      </div>

      {/* Primary Visualizations Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Trend Area Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-sm text-slate-900">Return & Order Volume Trends</h3>
              <p className="text-xs text-slate-500">Monthly order volume vs returned orders over 2026</p>
            </div>
            <div className="flex items-center space-x-3 text-xs">
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-sm bg-blue-500"></span>
                <span className="text-slate-600">Total Orders</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-sm bg-orange-500"></span>
                <span className="text-slate-600">Returns</span>
              </span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.monthly_trends}>
                <defs>
                  <linearGradient id="orderGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="returnGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                />
                <Area type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#orderGrad)" name="Total Orders" />
                <Area type="monotone" dataKey="returns" stroke="#f97316" strokeWidth={2} fillOpacity={1} fill="url(#returnGrad)" name="Returned Orders" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Return Reasons Donut Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-sm text-slate-900">Return Reasons Distribution</h3>
            <p className="text-xs text-slate-500 mb-3">Customer reported reasons across all returns</p>
          </div>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.return_reasons_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {data.return_reasons_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                  formatter={(val: any, name: any, item: any) => [`${val} returns (${item.payload.percentage}%)`, item.payload.name]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 space-y-1.5 max-h-28 overflow-y-auto pr-1">
            {data.return_reasons_distribution.map((reason, i) => (
              <div key={reason.name} className="flex items-center justify-between text-[11px]">
                <div className="flex items-center space-x-1.5 truncate">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}
                  ></span>
                  <span className="text-slate-700 truncate">{reason.name}</span>
                </div>
                <span className="font-semibold text-slate-900 shrink-0">{reason.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Secondary Row: Category Breakdown & High-Risk Products */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Return Rates Bar Chart */}
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm">
          <div className="mb-4">
            <h3 className="font-semibold text-sm text-slate-900">Category Return Rates</h3>
            <p className="text-xs text-slate-500">Apparel return rates by clothing category</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.category_return_rates} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" unit="%" tick={{ fontSize: 11, fill: '#64748b' }} domain={[0, 45]} />
                <YAxis dataKey="category" type="category" tick={{ fontSize: 11, fill: '#334155' }} width={80} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                  formatter={(val: any) => [`${val}% Return Rate`, 'Rate']}
                />
                <Bar dataKey="return_rate" fill="#f97316" radius={[0, 4, 4, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top High-Risk Products Table */}
        <div className="lg:col-span-2 bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-sm text-slate-900">High-Risk Product Watchlist</h3>
                <p className="text-xs text-slate-500">Products with elevated return rates requiring product-page updates</p>
              </div>
              <button
                onClick={() => onNavigate('/insights')}
                className="text-xs text-orange-600 font-medium hover:text-orange-700 flex items-center space-x-1"
              >
                <span>View AI Fixes</span>
                <ArrowUpRight size={13} />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200/80 text-slate-500 uppercase tracking-wider text-[10px]">
                    <th className="py-2 font-medium">Product</th>
                    <th className="py-2 font-medium">Category</th>
                    <th className="py-2 font-medium">Return Rate</th>
                    <th className="py-2 font-medium">Status</th>
                    <th className="py-2 font-medium">Known Quirk</th>
                    <th className="py-2 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.top_high_risk_products.map((item) => (
                    <tr key={item.product_id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 font-medium text-slate-900">
                        <div className="font-semibold">{item.name}</div>
                        <span className="text-[10px] text-slate-400 font-mono">{item.product_id}</span>
                      </td>
                      <td className="py-2.5 text-slate-600">{item.category}</td>
                      <td className="py-2.5">
                        <span className="font-bold text-orange-600">{item.return_rate}%</span>
                      </td>
                      <td className="py-2.5">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                            item.risk_category === 'High Risk'
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : 'bg-amber-50 text-amber-700 border border-amber-200'
                          }`}
                        >
                          {item.risk_category}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-500 max-w-[200px] truncate" title={item.known_quirk}>
                        {item.known_quirk}
                      </td>
                      <td className="py-2.5 text-right">
                        <button
                          onClick={() => onNavigate(`/assistant?product=${item.product_id}`)}
                          className="px-2.5 py-1 rounded bg-orange-50 hover:bg-orange-100 text-orange-700 font-medium text-[11px] transition-colors"
                        >
                          Consult AI
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center space-x-1">
              <Info size={13} />
              <span>Fixing product descriptions directly reduces avoidable returns.</span>
            </span>
            <button
              onClick={() => onNavigate('/products')}
              className="text-slate-600 hover:text-slate-900 font-medium"
            >
              Browse all 18 products &rarr;
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

