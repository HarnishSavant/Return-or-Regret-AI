import React, { useState } from 'react';
import {
  LayoutDashboard,
  BotMessageSquare,
  Shirt,
  ShieldAlert,
  Lightbulb,
  Activity,
  Menu,
  X,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

interface AppLayoutProps {
  currentRoute: string;
  onRouteChange: (route: string) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  currentRoute,
  onRouteChange,
  children
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    {
      id: 'dashboard',
      label: 'Executive Dashboard',
      route: '/dashboard',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      id: 'assistant',
      label: 'AI Shopping Assistant',
      route: '/assistant',
      icon: BotMessageSquare,
      badge: 'Agentic',
    },
    {
      id: 'products',
      label: 'Product Intelligence',
      route: '/products',
      icon: Shirt,
      badge: null,
    },
    {
      id: 'risk-analysis',
      label: 'Return Risk Analysis',
      route: '/risk-analysis',
      icon: ShieldAlert,
      badge: 'ML',
    },
    {
      id: 'insights',
      label: 'Product Insights',
      route: '/insights',
      icon: Lightbulb,
      badge: null,
    },
    {
      id: 'monitoring',
      label: 'System Monitoring',
      route: '/monitoring',
      icon: Activity,
      badge: 'Live',
    },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col md:flex-row antialiased text-slate-800">
      {/* Mobile Top Bar */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-slate-900 text-white border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-orange-500 flex items-center justify-center font-bold text-white shadow-sm">
            R
          </div>
          <div>
            <span className="font-semibold text-sm tracking-tight">Return or Regret</span>
            <span className="text-[10px] block text-orange-400 font-mono">AI DECISION AGENT</span>
          </div>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-1.5 rounded-md hover:bg-slate-800 text-slate-300"
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside
        className={`fixed md:sticky top-0 z-40 h-screen w-64 bg-slate-900 text-slate-200 border-r border-slate-800 flex flex-col transition-transform duration-200 ease-in-out ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 flex items-center justify-center shadow-lg shadow-orange-500/20 text-white font-bold text-base">
              R
            </div>
            <div>
              <div className="font-semibold text-white tracking-tight text-sm">
                Return or Regret <span className="text-orange-400">AI</span>
              </div>
              <div className="text-[11px] text-slate-400 font-medium">
                Decision Intelligence
              </div>
            </div>
          </div>

          <div className="mt-3.5 px-2.5 py-1.5 rounded-md bg-slate-800/60 border border-slate-700/50 flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-[11px] font-medium text-slate-300">Agent Active</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-700/80 text-orange-300 border border-slate-600/50">
              ML v1.0
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
            Core Modules
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentRoute === item.route;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onRouteChange(item.route);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-orange-500 text-white shadow-sm shadow-orange-500/30'
                    : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon size={16} className={isActive ? 'text-white' : 'text-slate-400'} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-semibold tracking-wide ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-slate-800 text-orange-400 border border-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer Principles */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-xs">
          <div className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-800">
            <div className="flex items-center space-x-1.5 text-orange-400 font-medium text-[11px] mb-1">
              <Sparkles size={13} />
              <span>Core Philosophy</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              "Fix the product page, not the customer." Sizing guidance over return penalties.
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-3.5 flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2 text-xs text-slate-500 font-medium">
            <span>Return or Regret AI</span>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="text-slate-900 font-semibold capitalize">
              {currentRoute.replace('/', '').replace('-', ' ') || 'Dashboard'}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200/80 text-[11px] text-slate-600 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>Backend Connected: port 8000</span>
            </div>
            <button
              onClick={() => onRouteChange('/assistant')}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-orange-500 hover:bg-orange-600 text-white text-xs font-medium shadow-sm transition-all"
            >
              <BotMessageSquare size={14} />
              <span>Launch Assistant</span>
            </button>
          </div>
        </header>

        {/* Page Container */}
        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

