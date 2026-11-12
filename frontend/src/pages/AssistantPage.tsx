import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Bot,
  Ruler,
  RotateCcw,
  Zap,
  Info,
  Sparkles,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import { Product, ChatMessage, StructuredAgentResponse } from '../types';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { RecommendationCard } from '../components/RecommendationCard';

interface AssistantPageProps {
  initialProductId?: string;
}

export const AssistantPage: React.FC<AssistantPageProps> = ({ initialProductId }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string>(initialProductId || 'P001');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  
  // Customer measurements state
  const [measurements, setMeasurements] = useState<{
    chest?: number;
    waist?: number;
    shoulder?: number;
    hip?: number;
    inseam?: number;
  }>({
    chest: 40.0,
    waist: 34.0,
    shoulder: 18.0
  });

  const [inputQuery, setInputQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentStep, setAgentStep] = useState<string>('');

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'agent',
      text: "👋 Welcome to **Return or Regret AI**! I'm your intelligent pre-purchase shopping decision agent.\n\nAsk about sizing, fabric comfort, or return risk for any catalog item. Adjust your measurements in the panel to test personal fit and receive evidence-grounded recommendations before you buy.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      execution_mode: 'Decision Engine Active'
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load products on mount
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const prods = await api.getProducts();
        setProducts(prods);
        const cur = prods.find(p => p.product_id === selectedProductId) || prods[0];
        if (cur) {
          setSelectedProduct(cur);
          setSelectedProductId(cur.product_id);
        }
      } catch (err) {
        console.error('Failed to load products for assistant:', err);
      }
    };
    fetchCatalog();
  }, [initialProductId]);

  useEffect(() => {
    if (products.length > 0) {
      const p = products.find(item => item.product_id === selectedProductId);
      if (p) setSelectedProduct(p);
    }
  }, [selectedProductId, products]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing, agentStep]);

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || isProcessing) return;

    const userMsgId = `user-${Date.now()}`;
    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputQuery('');
    setIsProcessing(true);

    // Dynamic customer-friendly pipeline indicators
    setAgentStep('1. Identifying query intent and customer measurements...');
    setTimeout(() => {
      setAgentStep('2. Comparing garment ease against fit tolerances...');
    }, 350);
    setTimeout(() => {
      setAgentStep('3. Consulting ML return risk & historical defect patterns...');
    }, 700);
    setTimeout(() => {
      setAgentStep('4. Synthesizing evidence-based recommendation...');
    }, 1050);

    try {
      const response: StructuredAgentResponse = await api.sendChatMessage({
        query: textToSend,
        context_product_id: selectedProductId,
        context_measurements: measurements as any
      });

      const agentMsgId = `agent-${Date.now()}`;
      const agentMessage: ChatMessage = {
        id: agentMsgId,
        sender: 'agent',
        text: response.summary_message || response.final_recommendation,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        structuredResponse: response,
        execution_mode: response.execution_metadata?.execution_mode || 'Decision Synthesis Engine',
        latency_ms: response.execution_metadata?.latency_ms
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          sender: 'agent',
          text: `⚠️ **Agent Error:** ${err.message || 'Could not connect to Python backend server.'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          execution_mode: 'System Failure'
        }
      ]);
    } finally {
      setIsProcessing(false);
      setAgentStep('');
    }
  };

  const handleSelectAlternativeSize = (newSize: string) => {
    handleSendMessage(`How does Size ${newSize} compare for my measurements on ${selectedProductId}?`);
  };

  const suggestedQuestions = [
    `I usually wear size M and my chest measurement is 40 inches. Will ${selectedProductId} fit me?`,
    `What material is ${selectedProductId} made of and how do I care for it?`,
    `Why do customers return ${selectedProductId}? Check historical defects.`,
    `What is our return policy if this item does not fit?`
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-8.5rem)]">
      {/* Left Column: Product Context & Measurements Sidebar */}
      <div className="lg:col-span-1 bg-white rounded-xl border border-slate-200/80 shadow-sm flex flex-col h-full overflow-hidden">
        {/* Product Selector Header */}
        <div className="p-4 border-b border-slate-100 bg-slate-50/50">
          <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
            Active Product Under Evaluation
          </label>
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(e.target.value)}
            className="w-full text-xs font-medium px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
          >
            {products.map(p => (
              <option key={p.product_id} value={p.product_id}>
                {p.product_id} — {p.name} (${p.price})
              </option>
            ))}
          </select>
        </div>

        {/* Selected Product Card Summary */}
        {selectedProduct && (
          <div className="p-4 border-b border-slate-100 overflow-y-auto">
            <div className="flex space-x-3">
              <img
                src={selectedProduct.image_url || `/images/products/${selectedProduct.product_id}.jpg`}
                alt={selectedProduct.name}
                onError={(e) => {
                  const target = e.currentTarget;
                  if (!target.src.endsWith('/images/products/P001.jpg')) {
                    target.src = '/images/products/P001.jpg';
                  }
                }}
                className="w-16 h-16 rounded-lg object-cover border border-slate-200 shrink-0 shadow-sm"
              />
              <div className="min-w-0 flex-1">
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                  {selectedProduct.category}
                </span>
                <h4 className="font-semibold text-xs text-slate-900 truncate mt-1">
                  {selectedProduct.name}
                </h4>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs font-bold text-slate-900">${selectedProduct.price}</span>
                  <span className="text-[10px] text-slate-400">&bull;</span>
                  <span className="text-[10px] text-slate-600">{selectedProduct.fit_type}</span>
                </div>
              </div>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Return Baseline</span>
                <span className="font-bold text-orange-600">
                  {selectedProduct.historical_return_rate ? Math.round(selectedProduct.historical_return_rate * 100) : 25}%
                </span>
              </div>
              <div className="p-2 rounded bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[10px]">Risk Tier</span>
                <span className="font-semibold text-slate-800">
                  {selectedProduct.risk_category || 'Medium Risk'}
                </span>
              </div>
            </div>

            {selectedProduct.known_fit_quirks && (
              <div className="mt-2.5 p-2 rounded-lg bg-orange-50/70 border border-orange-200/60 text-[11px] text-orange-900">
                <span className="font-semibold block text-[10px] text-orange-700">Verified Quirk:</span>
                {selectedProduct.known_fit_quirks}
              </div>
            )}
          </div>
        )}

        {/* Customer Measurements Section */}
        <div className="flex-1 p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-2.5">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-800">
              <Ruler size={14} className="text-orange-500" />
              <span>Customer Measurements</span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono">Inches</span>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600">Chest / Bust</span>
                <span className="font-semibold text-slate-900">{measurements.chest || 40}"</span>
              </div>
              <input
                type="range"
                min="32"
                max="52"
                step="0.5"
                value={measurements.chest || 40}
                onChange={(e) => setMeasurements({ ...measurements, chest: parseFloat(e.target.value) })}
                className="w-full accent-orange-500 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600">Waist</span>
                <span className="font-semibold text-slate-900">{measurements.waist || 34}"</span>
              </div>
              <input
                type="range"
                min="26"
                max="46"
                step="0.5"
                value={measurements.waist || 34}
                onChange={(e) => setMeasurements({ ...measurements, waist: parseFloat(e.target.value) })}
                className="w-full accent-orange-500 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600">Shoulder Width</span>
                <span className="font-semibold text-slate-900">{measurements.shoulder || 18}"</span>
              </div>
              <input
                type="range"
                min="14"
                max="22"
                step="0.5"
                value={measurements.shoulder || 18}
                onChange={(e) => setMeasurements({ ...measurements, shoulder: parseFloat(e.target.value) })}
                className="w-full accent-orange-500 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
              />
            </div>
          </div>

          <div className="mt-4 p-2.5 rounded-lg bg-blue-50 border border-blue-100 text-[11px] text-blue-900 leading-relaxed">
            <span className="font-semibold block mb-0.5 text-blue-800">Ground-Truth Ease Matching:</span>
            Your measurements are directly evaluated against authentic garment dimensions with fit-type tolerances.
          </div>
        </div>
      </div>

      {/* Right 3 Columns: Conversational Agent Terminal */}
      <div className="lg:col-span-3 bg-white rounded-xl border border-slate-200/80 shadow-sm flex flex-col h-full overflow-hidden">
        {/* Chat Header */}
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/40">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-orange-500 text-white flex items-center justify-center shadow-sm">
              <Bot size={18} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-xs text-slate-900">Return or Regret AI Assistant</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold border border-emerald-200">
                  Decision Engine Active
                </span>
              </div>
              <span className="text-[11px] text-slate-500">Autonomous evidence synthesis &amp; personalized ease calculation</span>
            </div>
          </div>

          <button
            onClick={() => {
              setMessages([
                {
                  id: 'welcome-reset',
                  sender: 'agent',
                  text: `Chat session reset. Ask about **${selectedProduct?.name || selectedProductId}** or any other catalog item!`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                  execution_mode: 'Decision Engine Active'
                }
              ]);
            }}
            className="p-1.5 rounded-lg hover:bg-slate-200/60 text-slate-500 hover:text-slate-800 transition-colors"
            title="Clear Chat History"
          >
            <RotateCcw size={15} />
          </button>
        </div>

        {/* Message Stream */}
        <div className="flex-1 p-5 overflow-y-auto space-y-5">
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            const structured = msg.structuredResponse;

            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
              >
                {/* Message Header */}
                <div className="flex items-center space-x-2 mb-1 text-[11px] text-slate-400">
                  <span className="font-medium text-slate-600">
                    {isUser ? 'Customer' : 'AI Decision Agent'}
                  </span>
                  <span>&bull;</span>
                  <span>{msg.timestamp}</span>
                  {msg.latency_ms && (
                    <>
                      <span>&bull;</span>
                      <span className="text-orange-600 font-mono text-[10px]">{msg.latency_ms}ms</span>
                    </>
                  )}
                  {msg.execution_mode && (
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-500 border border-slate-200">
                      {msg.execution_mode}
                    </span>
                  )}
                </div>

                {/* Bubble Container */}
                <div
                  className={`max-w-[90%] md:max-w-[85%] rounded-2xl px-4 py-3.5 text-xs leading-relaxed ${
                    isUser
                      ? 'bg-orange-500 text-white rounded-br-none shadow-sm'
                      : 'bg-slate-50/70 text-slate-800 border border-slate-200/80 rounded-bl-none shadow-sm'
                  }`}
                >
                  {/* If structured response is present, render rich customer-facing recommendation widgets */}
                  {structured ? (
                    <RecommendationCard
                      response={structured}
                      onSelectSize={handleSelectAlternativeSize}
                    />
                  ) : (
                    <MarkdownRenderer content={msg.text} />
                  )}
                </div>
              </div>
            );
          })}

          {/* Typing & Reasoning Animation */}
          {isProcessing && (
            <div className="flex flex-col items-start space-y-2">
              <div className="flex items-center space-x-2 text-[11px] text-orange-600 font-medium">
                <Zap size={14} className="animate-bounce" />
                <span>AI Agent Synthesizing Recommendation</span>
              </div>
              <div className="p-3 rounded-xl rounded-bl-none bg-slate-900 text-slate-200 border border-slate-800 text-xs shadow-md space-y-2 max-w-md">
                <div className="flex items-center space-x-2 font-mono text-[11px] text-orange-400">
                  <span className="w-2 h-2 rounded-full bg-orange-500 animate-ping"></span>
                  <span>{agentStep}</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-gradient-to-r from-orange-500 to-amber-400 h-full w-2/3 animate-pulse"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Quick Questions Bar */}
        <div className="px-5 py-2 bg-slate-50 border-t border-slate-100 overflow-x-auto flex space-x-2 text-[11px]">
          <span className="text-slate-400 font-medium whitespace-nowrap self-center text-[10px] uppercase tracking-wide">
            Prompts:
          </span>
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q)}
              disabled={isProcessing}
              className="whitespace-nowrap px-2.5 py-1 rounded-full bg-white hover:bg-orange-50 hover:text-orange-700 hover:border-orange-200 text-slate-600 border border-slate-200 transition-colors shadow-2xs font-medium"
            >
              {q.length > 55 ? q.substring(0, 55) + '...' : q}
            </button>
          ))}
        </div>

        {/* Message Input Box */}
        <div className="p-4 border-t border-slate-200/80 bg-white">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder={`Ask about ${selectedProduct?.name || selectedProductId} (e.g. 'Will Size M fit 40" chest?')...`}
              disabled={isProcessing}
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200/90 text-xs bg-slate-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-slate-900 placeholder:text-slate-400 shadow-2xs"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || isProcessing}
              className="px-4 py-2.5 rounded-xl bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-medium text-xs shadow-sm flex items-center space-x-1.5 transition-all"
            >
              <span>Ask Agent</span>
              <Send size={13} />
            </button>
          </form>
          <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400 px-1">
            <span>Evidence-based decision synthesis &bull; Sizing over return penalties</span>
            <span>Zero customer return penalties</span>
          </div>
        </div>
      </div>
    </div>
  );
};
