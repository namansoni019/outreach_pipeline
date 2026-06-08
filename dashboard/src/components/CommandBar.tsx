"use client";

import { useState } from "react";
import { Play, RotateCcw, ShieldAlert, Globe, Activity, CheckCircle2 } from "lucide-react";
import { Button, Input, Switch } from "./ui";
import { motion, AnimatePresence } from "framer-motion";
import { PipelineRun } from "@/lib/mock-data";

const DOMAIN_REGEX = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;

export function CommandBar({ pipeline }: { pipeline: any }) {
  const [domainInput, setDomainInput] = useState("");
  const [isDryRun, setIsDryRun] = useState(true);
  const [error, setError] = useState("");

  const handleRun = () => {
    if (!domainInput.trim()) {
      setError("Domain is required");
      return;
    }
    if (!DOMAIN_REGEX.test(domainInput)) {
      setError("Invalid domain format");
      return;
    }
    setError("");
    pipeline.startPipeline(domainInput.trim(), isDryRun);
    setDomainInput("");
  };

  const activeRun: PipelineRun | null = pipeline.activeRun;
  const isRunning = !!(activeRun && (activeRun.status === "running" || activeRun.status === "paused"));

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 z-10 sticky top-0 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        
        <div className="flex-1 max-w-2xl">
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Globe className="w-4 h-4 text-slate-400" />
              Target Acquisition
            </h2>
            {activeRun && (
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 ${
                activeRun.status === 'running' ? 'bg-blue-100 text-blue-700' :
                activeRun.status === 'paused' ? 'bg-amber-100 text-amber-700' :
                activeRun.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                'bg-slate-100 text-slate-500'
              }`}>
                {activeRun.status === 'running' && <Activity className="w-3 h-3 animate-pulse" />}
                {activeRun.status === 'completed' && <CheckCircle2 className="w-3 h-3" />}
                {activeRun.status}
              </span>
            )}
          </div>
          
          <div className="flex items-start gap-4">
            <div className="flex-1 relative">
              <Input
                placeholder="Enter seed domain (e.g. example.com)"
                value={domainInput}
                onChange={(e) => setDomainInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !isRunning && handleRun()}
                disabled={isRunning}
                className={`h-10 text-sm shadow-sm bg-slate-50 focus:bg-white border-slate-200 transition-all ${error ? "border-red-400 focus:ring-red-400" : ""}`}
              />
              <AnimatePresence>
                {error && (
                  <motion.p initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="absolute -bottom-5 left-1 text-[11px] text-red-500 font-medium">
                    {error}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>
            
            <div className="flex items-center gap-2 h-10 px-4 rounded-md border border-slate-200 bg-slate-50 shrink-0">
              <Switch checked={isDryRun} onChange={setIsDryRun} disabled={isRunning} />
              <span className="text-xs font-semibold text-slate-700 select-none">Dry Run</span>
            </div>
          </div>

          {activeRun && (
            <div className="mt-3 flex items-center gap-4 text-[11px] font-medium text-slate-500">
              <span>Target: <strong className="text-slate-700">{activeRun.seed_domain}</strong></span>
              <span className="w-1 h-1 rounded-full bg-slate-300"></span>
              <span>Mode: <strong className="text-slate-700">{activeRun.isDryRun ? "Dry Run" : "Live Send"}</strong></span>
              <span className="w-1 h-1 rounded-full bg-slate-300"></span>
              <span>Started: <strong className="text-slate-700 font-mono">{new Date(activeRun.timestamp).toLocaleTimeString()}</strong></span>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-3 pb-0.5">
          {activeRun && (
            <Button variant="outline" onClick={pipeline.reset} className="h-10 gap-2 text-slate-600 bg-white shadow-sm border-slate-200 hover:bg-slate-50" disabled={isRunning}>
              <RotateCcw className="w-4 h-4" />
              Reset Workspace
            </Button>
          )}
          
          <Button 
            onClick={handleRun} 
            disabled={isRunning}
            className={`h-10 px-6 gap-2 shadow-sm font-semibold transition-all ${
              isRunning ? "bg-slate-100 text-slate-400 border-slate-200" : "bg-slate-900 hover:bg-slate-800 text-white"
            }`}
          >
            {isRunning ? (
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }}>
                <ShieldAlert className="w-4 h-4" />
              </motion.div>
            ) : (
              <Play className="w-4 h-4" />
            )}
            {isRunning ? "Sequence Active..." : "Execute Pipeline"}
          </Button>
        </div>
      </div>
    </header>
  );
}
