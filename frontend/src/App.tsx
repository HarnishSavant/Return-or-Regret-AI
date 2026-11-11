import React, { useState, useEffect } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { AssistantPage } from './pages/AssistantPage';
import { ProductsPage } from './pages/ProductsPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { InsightsPage } from './pages/InsightsPage';
import { MonitoringPage } from './pages/MonitoringPage';

export function App() {
  const [currentRoute, setCurrentRoute] = useState<string>('/dashboard');
  const [activeAssistantProductId, setActiveAssistantProductId] = useState<string>('P001');

  // Sync with browser URL / hash if desired
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '') || '/dashboard';
      if (hash.startsWith('/assistant')) {
        const queryParams = new URLSearchParams(hash.split('?')[1] || '');
        const p = queryParams.get('product');
        if (p) setActiveAssistantProductId(p);
        setCurrentRoute('/assistant');
      } else {
        setCurrentRoute(hash);
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleRouteChange = (route: string) => {
    if (route.startsWith('/assistant')) {
      const parts = route.split('?');
      if (parts[1]) {
        const params = new URLSearchParams(parts[1]);
        const pid = params.get('product');
        if (pid) setActiveAssistantProductId(pid);
      }
      window.location.hash = '/assistant';
      setCurrentRoute('/assistant');
    } else {
      window.location.hash = route;
      setCurrentRoute(route);
    }
  };

  const handleNavigateToAssistant = (productId: string) => {
    setActiveAssistantProductId(productId);
    window.location.hash = `/assistant?product=${productId}`;
    setCurrentRoute('/assistant');
  };

  return (
    <AppLayout currentRoute={currentRoute} onRouteChange={handleRouteChange}>
      {currentRoute === '/dashboard' && (
        <DashboardPage onNavigate={handleRouteChange} />
      )}
      {currentRoute === '/assistant' && (
        <AssistantPage initialProductId={activeAssistantProductId} />
      )}
      {currentRoute === '/products' && (
        <ProductsPage onNavigateToAssistant={handleNavigateToAssistant} />
      )}
      {currentRoute === '/risk-analysis' && (
        <RiskAnalysisPage onNavigateToAssistant={handleNavigateToAssistant} />
      )}
      {currentRoute === '/insights' && <InsightsPage />}
      {currentRoute === '/monitoring' && <MonitoringPage />}
    </AppLayout>
  );
}

export default App;
