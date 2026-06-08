"use client";

import { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { CommandBar } from "./CommandBar";
import { usePipeline } from "@/lib/usePipeline";

export function AppShell({ children }: { children: ReactNode }) {
  const pipeline = usePipeline();

  return (
    <div className="flex h-screen bg-[#F0F2F5] text-slate-900 font-sans overflow-hidden">
      <Sidebar runs={pipeline.runs} activeRunId={pipeline.activeRun?.id || null} setActiveRunId={pipeline.setActiveRunId} />
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <CommandBar pipeline={pipeline} />
        <main className="flex-1 overflow-y-auto scroll-smooth">
          <div className="p-6 pb-12 max-w-[1400px] mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
