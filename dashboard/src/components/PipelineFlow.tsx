"use client";

import { motion } from "framer-motion";
import { Search, Users, MailCheck, FileEdit, Send, CheckCircle2, Lock, Clock } from "lucide-react";
import { Card } from "./ui";

const STAGES = [
  { id: "ocean", name: "Ocean.io Engine", desc: "Lookalike Extraction", icon: Search, color: "bg-blue-500", text: "text-blue-500", border: "border-blue-500" },
  { id: "prospeo", name: "Prospeo Resolver", desc: "Decision Makers", icon: Users, color: "bg-indigo-500", text: "text-indigo-500", border: "border-indigo-500" },
  { id: "eazyreach", name: "Eazyreach Verifier", desc: "Email Validation", icon: MailCheck, color: "bg-amber-500", text: "text-amber-500", border: "border-amber-500" },
  { id: "draft", name: "AI Generator", desc: "Sequence Drafting", icon: FileEdit, color: "bg-slate-700", text: "text-slate-700", border: "border-slate-700" },
  { id: "brevo", name: "Brevo Dispatcher", desc: "Live Outreach", icon: Send, color: "bg-emerald-500", text: "text-emerald-500", border: "border-emerald-500" },
];

export function PipelineFlow({ activeRun }: { activeRun: any }) {
  const currentStageId = activeRun?.stage || "idle";
  const status = activeRun?.status || "idle";

  const getStageState = (stageId: string, idx: number) => {
    if (!activeRun) return "idle";
    const currentIndex = STAGES.findIndex(s => s.id === currentStageId);
    
    if (activeRun.stage === "done" || currentIndex > idx) return "completed";
    if (currentIndex === idx) {
      if (status === "paused") return "paused";
      return "running";
    }
    if (activeRun.isDryRun && stageId === "brevo") return "locked";
    return "pending";
  };

  const getProgressWidth = () => {
    if (!activeRun) return "0%";
    if (activeRun.stage === "done") return "100%";
    const currentIndex = STAGES.findIndex(s => s.id === currentStageId);
    if (currentIndex === -1) return "0%";
    const segmentWidth = 100 / (STAGES.length - 1);
    return `${(currentIndex * segmentWidth)}%`;
  };

  return (
    <Card className="p-6 mb-6 overflow-hidden">
      <div className="flex justify-between items-center mb-8">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest">Execution Topology</h3>
        <div className="flex items-center gap-2 text-[10px] text-slate-500 font-medium bg-slate-50 px-2 py-1 rounded">
          <Clock className="w-3 h-3" />
          Est. Duration: {activeRun ? (activeRun.isDryRun ? "00:08" : "00:10") : "00:00"}
        </div>
      </div>
      
      <div className="relative flex justify-between px-4 pb-2">
        {/* Background Track */}
        <div className="absolute top-6 left-12 right-12 h-1 bg-slate-100 rounded-full -z-10" />
        
        {/* Animated Progress Track */}
        <motion.div 
          className="absolute top-6 left-12 h-1 bg-slate-900 rounded-full -z-10"
          initial={{ width: "0%" }}
          animate={{ width: getProgressWidth() }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          style={{ maxWidth: "calc(100% - 6rem)" }}
        />

        {STAGES.map((stage, idx) => {
          const state = getStageState(stage.id, idx);
          const Icon = state === "completed" ? CheckCircle2 : state === "locked" ? Lock : stage.icon;
          
          let nodeClasses = "bg-white border-2 border-slate-200 text-slate-400";
          let iconClasses = "w-5 h-5";

          if (state === "completed") {
            nodeClasses = `${stage.color} border-transparent text-white shadow-sm`;
          } else if (state === "running") {
            nodeClasses = `bg-white border-2 ${stage.border} ${stage.text} shadow-md`;
          } else if (state === "paused") {
            nodeClasses = `bg-amber-50 border-2 border-amber-500 text-amber-600 shadow-md`;
          } else if (state === "locked") {
            nodeClasses = `bg-slate-50 border-2 border-slate-200 text-slate-300`;
          }

          return (
            <div key={stage.id} className="flex flex-col items-center gap-4 relative z-10 w-32">
              <motion.div 
                className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${nodeClasses}`}
                animate={state === "running" ? { scale: [1, 1.05, 1], boxShadow: ["0px 0px 0px 0px rgba(0,0,0,0)", "0px 0px 0px 8px rgba(0,0,0,0.04)", "0px 0px 0px 0px rgba(0,0,0,0)"] } : {}}
                transition={{ repeat: state === "running" ? Infinity : 0, duration: 2 }}
              >
                <Icon className={iconClasses} />
              </motion.div>
              
              <div className="text-center">
                <div className={`text-xs font-bold tracking-wide ${state !== 'pending' && state !== 'idle' && state !== 'locked' ? 'text-slate-900' : 'text-slate-400'}`}>
                  {stage.name}
                </div>
                <div className="text-[10px] font-medium text-slate-500 mt-1 uppercase tracking-wider">{stage.desc}</div>
                {state === "completed" && (
                  <div className="mt-2 text-[9px] font-mono font-bold text-emerald-600 bg-emerald-50 inline-block px-1.5 py-0.5 rounded border border-emerald-100">
                    84ms
                  </div>
                )}
                {state === "paused" && (
                  <div className="mt-2 text-[9px] font-mono font-bold text-amber-600 bg-amber-50 inline-block px-1.5 py-0.5 rounded border border-amber-100 animate-pulse">
                    AWAITING REVIEW
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
