"use client";

import { LayoutDashboard, GitBranch, BarChart3, History, Settings, HelpCircle, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar({ activeTab, setActiveTab }: { activeTab: string, setActiveTab: (t: string) => void }) {
  return (
    <aside className="w-[260px] h-screen flex flex-col bg-surface-sidebar shadow-sidebar relative z-20">
      
      {/* Logo area */}
      <div className="h-[72px] flex items-center px-6 shrink-0">
        <h1 className="text-[22px] font-bold text-ink-primary tracking-tight">OutreachFlow</h1>
      </div>

      {/* User Plan area */}
      <div className="px-6 py-4 flex items-center gap-3 border-b border-surface-border">
        <div className="w-10 h-10 rounded-md bg-brand text-white flex items-center justify-center font-bold text-lg">
          P
        </div>
        <div className="flex flex-col justify-center">
          <span className="text-[14px] font-semibold text-ink-primary leading-tight">Premium Outreach</span>
          <span className="text-[10px] text-ink-muted uppercase tracking-wider mt-0.5">Enterprise Plan</span>
        </div>
      </div>

      {/* Nav section */}
      <nav className="flex-1 px-4 pt-6 space-y-1 overflow-y-auto">
        <NavItem icon={<LayoutDashboard size={18} />} label="Dashboard" active={activeTab === "Dashboard"} onClick={() => setActiveTab("Dashboard")} />
        <NavItem icon={<GitBranch size={18} />} label="Pipeline" active={activeTab === "Pipeline"} onClick={() => setActiveTab("Pipeline")} />
        <NavItem icon={<BarChart3 size={18} />} label="Results" active={activeTab === "Results"} onClick={() => setActiveTab("Results")} />
        <NavItem icon={<History size={18} />} label="History" active={activeTab === "History"} onClick={() => setActiveTab("History")} />
        <NavItem icon={<Settings size={18} />} label="Settings" active={activeTab === "Settings"} onClick={() => setActiveTab("Settings")} />
      </nav>

      {/* Bottom footer */}
      <div className="p-6 shrink-0 space-y-4">
        <button className="w-full py-2.5 rounded-md border border-surface-border text-[13px] font-semibold text-ink-primary hover:bg-surface-hover transition-colors shadow-sm">
          Upgrade Plan
        </button>
        <div className="space-y-3 pt-2">
          <a href="#" className="flex items-center gap-2 text-ink-secondary hover:text-ink-primary transition-colors text-[13px]">
            <HelpCircle size={16} />
            Support
          </a>
          <a href="#" className="flex items-center gap-2 text-ink-secondary hover:text-ink-primary transition-colors text-[13px]">
            <BookOpen size={16} />
            Documentation
          </a>
        </div>
      </div>
    </aside>
  );
}

function NavItem({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick: () => void }) {
  return (
    <div onClick={onClick} className={cn(
      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] font-medium transition-all duration-150 cursor-pointer group",
      active 
        ? "bg-brand-muted text-brand" 
        : "text-ink-secondary hover:bg-surface-hover hover:text-ink-primary"
    )}>
      <span className={cn(
        "flex items-center justify-center",
        active ? "text-brand" : "text-ink-muted group-hover:text-ink-primary"
      )}>
        {icon}
      </span>
      {label}
    </div>
  );
}
