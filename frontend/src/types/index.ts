export interface Product {
  product_id: string;
  name: string;
  category: string;
  price: number;
  fit_type: string;
  material: string;
  sizes: string[];
  size_guide_available: boolean;
  description_completeness: number;
  image_url: string;
  description: string;
  care_instructions: string;
  known_fit_quirks: string;
  size_chart: Record<string, Record<string, number>>;
  historical_return_rate?: number;
  total_orders?: number;
  risk_category?: string;
}

export interface DashboardSummary {
  total_products: number;
  total_orders_analyzed: number;
  overall_return_rate: number;
  avoidable_return_rate: number;
  high_risk_product_count: number;
  total_agent_interactions: number;
  category_return_rates: Array<{
    category: string;
    total_orders: number;
    returns: number;
    return_rate: number;
  }>;
  return_reasons_distribution: Array<{
    name: string;
    value: number;
    percentage: number;
  }>;
  monthly_trends: Array<{
    month: string;
    orders: number;
    returns: number;
    return_rate: number;
  }>;
  top_high_risk_products: Array<{
    product_id: string;
    name: string;
    category: string;
    price: number;
    return_rate: number;
    risk_category: string;
    known_quirk: string;
  }>;
  recent_agent_activity: any[];
  synthetic_notice: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: string;
  intent?: string;
  tools_executed?: string[];
  tool_results?: Record<string, any>;
  sources?: Array<{
    title: string;
    document: string;
    confidence: string;
  }>;
  execution_mode?: string;
  latency_ms?: number;
}

export interface AISuggestion {
  id: string;
  product_id: string;
  product_name: string;
  category: string;
  trigger_issue: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  ai_suggested_action: string;
  estimated_impact: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  reviewed_at?: string;
}

export interface ModelMetrics {
  trained_at: string;
  total_samples: number;
  train_samples: number;
  test_samples: number;
  best_model: string;
  models_benchmark: Record<string, {
    model_name: string;
    cv_f1_mean: number;
    cv_f1_std: number;
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    confusion_matrix: number[][];
    test_sample_count: number;
  }>;
  feature_importances: Record<string, number>;
  synthetic_data_disclaimer: string;
}

