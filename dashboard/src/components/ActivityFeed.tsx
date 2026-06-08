"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Info, CheckCircle2, AlertTriangle, XCircle, Activity, Terminal } from "lucide-react";
import { Card } from "./ui";
import { useEffect, useRef } from "react";

export function ActivityFeed({ activity }: { activity: any[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activity]);

  const getIcon = (type: string) => {
    switch (type) {
      case "success": return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />;
      case "warning": return <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />;
      case "error": return <XCircle className="w-3.5 h-3.5 text-red-500" />;
      default: return <Info className="w-3.5 h-3.5 text-blue-500" />;
    }
  };

  return (
    <Card className="flex flex-col h-full min-h-[400px] border-slate-200 shadow-sm overflow-hidden bg-white">
      <div className="p-4 border-b border-slate-200 bg-[#FAFAFA] flex justify-between items-center">
        <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest flex items-center gap-2">
          <Terminal className="w-4 h-4 text-slate-500" />
          Event Stream
        </h3>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Live</span>
        </div>
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 bg-slate-900 text-slate-300 font-mono text-[11px] leading-relaxed scroll-smooth">
        <div className="space-y-3">
          <AnimatePresence initial={false}>
            {activity.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex gap-3 group"
              >
                <div className="mt-0.5 shrink-0 opacity-80">{getIcon(log.type)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-slate-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    {log.stage && (
                      <span className={`px-1.5 py-0.5 rounded text-[9px] uppercase font-bold tracking-wider ${
                        log.stage === 'ocean' ? 'bg-blue-500/20 text-blue-300' :
                        log.stage === 'prospeo' ? 'bg-indigo-500/20 text-indigo-300' :
                        log.stage === 'eazyreach' ? 'bg-amber-500/20 text-amber-300' :
                        log.stage === 'brevo' ? 'bg-emerald-500/20 text-emerald-300' :
                        'bg-slate-700 text-slate-300'
                      }`}>
                        {log.stage}
                      </span>
                    )}
                  </div>
                  <span className={`${
                    log.type === 'success' ? 'text-emerald-300' :
                    log.type === 'warning' ? 'text-amber-300' :
                    log.type === 'error' ? 'text-red-400' :
                    'text-slate-200'
                  }`}>{log.message}</span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </Card>
  );
}
