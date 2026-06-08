"use client";

import { Brain, Layers, BarChart3, Database } from "lucide-react";

export function SystemReady() {
  return (
    <div className="flex-1 flex items-center justify-center bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.06)_0%,transparent_65%)] animate-fade-up">
      <div className="max-w-[440px] w-full mx-auto bg-surface-card border border-surface-border rounded-2xl p-12 text-center shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_8px_40px_rgba(0,0,0,0.5)]">
        
        {/* Icon block */}
        <div className="relative w-16 h-16 mx-auto mb-6">
          <div className="w-16 h-16 rounded-full border border-brand/20 flex items-center justify-center">
            <Database className="w-6 h-6 text-brand" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-[18px] font-semibold text-ink-primary mb-2">
          System Ready
        </h2>

        {/* Description */}
        <p className="text-[13px] text-ink-secondary leading-relaxed mb-8">
          Revenue Operations Pipeline initialized. Enter a target seed domain in the command bar above to commence data extraction and outreach.
        </p>

        {/* Feature pills row */}
        <div className="flex justify-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-raised border border-surface-border text-[12px] text-ink-secondary">
            <Brain size={12} className="text-brand" />
            AI Enrichment
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-raised border border-surface-border text-[12px] text-ink-secondary">
            <Layers size={12} className="text-brand" />
            Multi-channel Outreach
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-raised border border-surface-border text-[12px] text-ink-secondary">
            <BarChart3 size={12} className="text-brand" />
            Analytics Ready
          </div>
        </div>

      </div>
    </div>
  );
}
