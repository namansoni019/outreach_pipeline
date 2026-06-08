"use client";

import { Bell, HelpCircle, User } from "lucide-react";

export function CommandBar() {
  return (
    <header className="h-[72px] flex items-center justify-between px-8 bg-surface-card border-b border-surface-border">
      
      {/* Left nav */}
      <div className="flex items-center gap-6">
        <a href="#" className="text-[14px] font-medium text-ink-primary hover:text-brand transition-colors">
          Workspaces
        </a>
        <a href="#" className="text-[14px] font-medium text-ink-secondary hover:text-ink-primary transition-colors">
          Teams
        </a>
      </div>
      
      {/* Right actions */}
      <div className="flex items-center gap-5">
        <button className="px-4 py-2 rounded-md bg-brand text-white text-[13px] font-semibold hover:bg-brand-hover transition-colors shadow-sm">
          New Run
        </button>
        
        <div className="flex items-center gap-4 text-ink-secondary border-l border-surface-border pl-5">
          <button className="hover:text-ink-primary transition-colors">
            <Bell size={18} />
          </button>
          <button className="hover:text-ink-primary transition-colors">
            <HelpCircle size={18} />
          </button>
          <button className="w-8 h-8 rounded-full bg-surface-base border border-surface-border flex items-center justify-center hover:bg-surface-hover transition-colors">
            <User size={16} />
          </button>
        </div>
      </div>

    </header>
  );
}
