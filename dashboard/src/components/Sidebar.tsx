"use client";

import { Activity, Radio, GitBranch, ShieldCheck, Database, LayoutTemplate, Key, Server } from "lucide-react";
import { format } from "date-fns";
import { PipelineRun } from "@/lib/mock-data";

interface SidebarProps {
  runs: PipelineRun[];
  activeRunId: string | null;
  setActiveRunId: (id: string) => void;
}

export function Sidebar({ runs, activeRunId, setActiveRunId }: SidebarProps) {
  return (
    <aside className="w-64 border-r border-slate-200 bg-[#FAFAFA] flex flex-col hidden md:flex h-full">
      <div className="p-5 border-b border-slate-200 bg-white">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-md bg-slate-900 flex items-center justify-center shadow-sm">
            <Radio className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-900 leading-tight">RevOps Command</h1>
            <span className="text-[10px] font-semibold tracking-wider text-slate-500 uppercase">Automation Pipeline</span>
          </div>
        </div>
        <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-blue-50 border border-blue-100 w-full justify-center">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wide">Mock Environment Active</span>
        </div>
      </div>

      <div className="p-3 border-b border-slate-200 bg-[#FAFAFA]">
        <nav className="space-y-1">
          <button className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium rounded-md bg-white text-slate-900 shadow-sm border border-slate-200">
            <GitBranch className="w-4 h-4 text-slate-500" />
            Active Pipeline
          </button>
          <button className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium rounded-md text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors">
            <LayoutTemplate className="w-4 h-4 text-slate-400" />
            Templates
          </button>
          <button className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium rounded-md text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors">
            <Key className="w-4 h-4 text-slate-400" />
            Credentials
          </button>
        </nav>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <div className="px-5 py-3 sticky top-0 bg-[#FAFAFA] z-10 flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          Run History
        </div>
        <div className="px-3 pb-4 space-y-1">
          {runs.length === 0 ? (
            <div className="px-3 py-6 text-xs text-slate-400 text-center flex flex-col items-center gap-2">
              <Activity className="w-5 h-5 opacity-20" />
              No previous runs
            </div>
          ) : (
            runs.map((r) => (
              <button
                key={r.id}
                onClick={() => setActiveRunId(r.id)}
                className={`w-full text-left px-3 py-2.5 rounded-md transition-all text-sm group ${
                  activeRunId === r.id 
                    ? "bg-white shadow-sm border border-slate-200" 
                    : "border border-transparent hover:bg-slate-100"
                }`}
              >
                <div className={`font-medium truncate ${activeRunId === r.id ? "text-slate-900" : "text-slate-600 group-hover:text-slate-900"}`}>
                  {r.seed_domain}
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[10px] text-slate-400 font-medium font-mono">
                    {format(new Date(r.timestamp), "HH:mm:ss")}
                  </span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] uppercase font-bold tracking-wide ${
                    r.status === 'running' ? 'text-blue-600' :
                    r.status === 'paused' ? 'text-amber-600' :
                    r.status === 'completed' ? 'text-emerald-600' :
                    'text-slate-500'
                  }`}>
                    {r.status}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="p-4 border-t border-slate-200 bg-white space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 uppercase">
            <Server className="w-3 h-3" /> API Mode
          </div>
          <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">Mock</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 uppercase">
            <ShieldCheck className="w-3 h-3 text-emerald-500" /> Safety
          </div>
          <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100">Enabled</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 uppercase">
            <Database className="w-3 h-3" /> Storage
          </div>
          <span className="text-[10px] font-bold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">Local JSON</span>
        </div>
      </div>
    </aside>
  );
}
