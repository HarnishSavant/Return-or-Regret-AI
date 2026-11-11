import React from 'react';
import { CheckCircle2, AlertTriangle, Info, ShieldAlert } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  // Parse message into lines and structured blocks
  const lines = content.split('\n');

  return (
    <div className="space-y-2 text-xs leading-relaxed text-slate-800">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (!trimmed) {
          return <div key={idx} className="h-1.5" />;
        }

        // H3 Header
        if (trimmed.startsWith('### ')) {
          return (
            <h3 key={idx} className="text-sm font-bold text-slate-900 pt-1 pb-0.5 border-b border-slate-200/70 flex items-center space-x-1.5">
              <span>{trimmed.replace('### ', '')}</span>
            </h3>
          );
        }

        // H4 Header
        if (trimmed.startsWith('#### ')) {
          return (
            <h4 key={idx} className="text-xs font-semibold text-slate-800 pt-2 pb-0.5 text-orange-950 flex items-center space-x-1">
              <span>{trimmed.replace('#### ', '')}</span>
            </h4>
          );
        }

        // Callout Warnings / Assessments
        if (trimmed.startsWith('⚠️ ')) {
          return (
            <div key={idx} className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 flex items-start space-x-2 my-1.5">
              <AlertTriangle size={15} className="text-amber-600 shrink-0 mt-0.5" />
              <div className="font-semibold text-xs leading-snug">
                {renderFormattedInline(trimmed.replace('⚠️ ', ''))}
              </div>
            </div>
          );
        }

        if (trimmed.startsWith('✅ ')) {
          return (
            <div key={idx} className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-start space-x-2 my-1.5">
              <CheckCircle2 size={15} className="text-emerald-600 shrink-0 mt-0.5" />
              <div className="font-semibold text-xs leading-snug">
                {renderFormattedInline(trimmed.replace('✅ ', ''))}
              </div>
            </div>
          );
        }

        // Bullet points
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          const itemText = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start space-x-2 ml-1">
              <span className="text-orange-500 font-bold shrink-0 text-sm leading-none mt-0.5">&bull;</span>
              <span className="text-slate-700 leading-relaxed">
                {renderFormattedInline(itemText)}
              </span>
            </div>
          );
        }

        // Standard paragraph
        return (
          <p key={idx} className="leading-relaxed">
            {renderFormattedInline(trimmed)}
          </p>
        );
      })}
    </div>
  );
};

// Simple inline parser for **bold**, *italic*, and `code`
function renderFormattedInline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/g);

  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-bold text-slate-900">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return (
        <em key={i} className="italic text-slate-600">
          {part.slice(1, -1)}
        </em>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="px-1.5 py-0.5 rounded bg-slate-200/80 font-mono text-[11px] text-orange-800">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
