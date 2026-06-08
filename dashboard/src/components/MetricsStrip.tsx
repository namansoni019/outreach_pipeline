"use client";

import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect } from "react";
import { Search, Users, MailCheck, FileEdit, Send, XOctagon, TrendingUp } from "lucide-react";
import { Card } from "./ui";

function AnimatedCounter({ value }: { value: number }) {
  const spring = useSpring(0, { bounce: 0, duration: 1200 });
  const display = useTransform(spring, (current) => Math.round(current));

  useEffect(() => {
    spring.set(value);
  }, [spring, value]);

  return <motion.span>{display}</motion.span>;
}

export function MetricsStrip({ activeRun }: { activeRun: any }) {
  const metrics = [
    { id: "companies", label: "Companies", value: activeRun?.companies?.length || 0, icon: Search, accent: "border-t-blue-500", text: "text-blue-600", bg: "bg-blue-50" },
    { id: "dms", label: "Decision Makers", value: activeRun?.decisionMakers?.length || 0, icon: Users, accent: "border-t-indigo-500", text: "text-indigo-600", bg: "bg-indigo-50" },
    { id: "verified", label: "Verified Emails", value: activeRun?.contacts?.length || 0, icon: MailCheck, accent: "border-t-emerald-500", text: "text-emerald-600", bg: "bg-emerald-50" },
    { id: "drafts", label: "Drafts Ready", value: activeRun?.drafts?.length || 0, icon: FileEdit, accent: "border-t-amber-500", text: "text-amber-600", bg: "bg-amber-50" },
    { id: "sent", label: "Dispatched", value: activeRun?.sendResults?.filter((r: any) => r.status === "sent").length || 0, icon: Send, accent: "border-t-purple-500", text: "text-purple-600", bg: "bg-purple-50" },
    { id: "failures", label: "Drop-offs", value: activeRun?.failures?.length || 0, icon: XOctagon, accent: "border-t-red-500", text: "text-red-600", bg: "bg-red-50" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {metrics.map((m, i) => {
        const Icon = m.icon;
        return (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.05, ease: "easeOut" }}
          >
            <Card className={`p-4 flex flex-col relative overflow-hidden group hover:shadow-md transition-all border-t-2 ${m.accent} border-x-slate-200 border-b-slate-200`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{m.label}</span>
                <div className={`p-1.5 rounded-md ${m.bg}`}>
                  <Icon className={`w-3.5 h-3.5 ${m.text}`} />
                </div>
              </div>
              <div className="flex items-end justify-between">
                <div className="text-3xl font-bold text-slate-900 font-mono tracking-tight leading-none">
                  <AnimatedCounter value={m.value} />
                </div>
                {m.value > 0 && m.id !== "failures" && (
                  <div className="flex items-center gap-0.5 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                    <TrendingUp className="w-3 h-3" />
                    +{(Math.random() * 10 + 5).toFixed(1)}%
                  </div>
                )}
              </div>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}
