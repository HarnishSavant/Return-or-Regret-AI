import { DashboardSummary, Product, AISuggestion, ModelMetrics } from '../types';

const BASE_URL = '/api';

export const api = {
  async getHealth() {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error('Failed to fetch health');
    return res.json();
  },

  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${BASE_URL}/dashboard/summary`);
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  async getProducts(params?: { category?: string; risk?: string; search?: string }): Promise<Product[]> {
    const url = new URL(`${window.location.origin}${BASE_URL}/products`);
    if (params?.category) url.searchParams.append('category', params.category);
    if (params?.risk) url.searchParams.append('risk', params.risk);
    if (params?.search) url.searchParams.append('search', params.search);

    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch products');
    return res.json();
  },

  async getProductDetail(productId: string): Promise<{ product: Product; history: any }> {
    const res = await fetch(`${BASE_URL}/products/${productId}`);
    if (!res.ok) throw new Error(`Failed to fetch product ${productId}`);
    return res.json();
  },

  async sendChatMessage(payload: {
    query: string;
    context_product_id?: string;
    context_measurements?: Record<string, number>;
  }) {
    const res = await fetch(`${BASE_URL}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to communicate with AI agent');
    return res.json();
  },

  async predictRisk(payload: {
    product_id: string;
    selected_size: string;
    bracketing_order?: boolean;
    discount_applied?: number;
  }) {
    const res = await fetch(`${BASE_URL}/risk/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to predict return risk');
    return res.json();
  },

  async recommendFit(payload: {
    product_id: string;
    selected_size: string;
    customer_measurements: Record<string, number>;
  }) {
    const res = await fetch(`${BASE_URL}/fit/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to calculate fit');
    return res.json();
  },

  async getInsights(): Promise<{
    ai_suggestions: AISuggestion[];
    missing_info_audit: any[];
    repeated_fit_problems: any[];
  }> {
    const res = await fetch(`${BASE_URL}/insights`);
    if (!res.ok) throw new Error('Failed to fetch product insights');
    return res.json();
  },

  async approveSuggestion(suggestionId: string, action: 'approve' | 'reject') {
    const res = await fetch(`${BASE_URL}/insights/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion_id: suggestionId, action }),
    });
    if (!res.ok) throw new Error('Failed to update suggestion status');
    return res.json();
  },

  async getMonitoringLogs(): Promise<{
    total_requests_logged: number;
    average_latency_ms: number;
    tool_execution_frequency: Array<{ tool: string; executions: number }>;
    recent_logs: any[];
  }> {
    const res = await fetch(`${BASE_URL}/monitoring/logs`);
    if (!res.ok) throw new Error('Failed to fetch monitoring logs');
    return res.json();
  },

  async getModelMetrics(): Promise<ModelMetrics> {
    const res = await fetch(`${BASE_URL}/model/metrics`);
    if (!res.ok) throw new Error('Failed to fetch model metrics');
    return res.json();
  }
};

