"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "./ui";
import { ExternalLink, DatabaseBackup } from "lucide-react";

export function ResultsTabs({ activeRun }: { activeRun: any }) {
  const [activeTab, setActiveTab] = useState<"companies" | "decisionMakers" | "contacts" | "drafts" | "sendResults" | "failures">("companies");

  const tabs = [
    { id: "companies", label: "Companies", data: activeRun?.companies || [] },
    { id: "decisionMakers", label: "Decision Makers", data: activeRun?.decisionMakers || [] },
    { id: "contacts", label: "Contacts", data: activeRun?.contacts || [] },
    { id: "drafts", label: "Drafts", data: activeRun?.drafts || [] },
    { id: "sendResults", label: "Dispatched", data: activeRun?.sendResults || [] },
    { id: "failures", label: "Failures", data: activeRun?.failures || [] },
  ];

  const currentData = tabs.find(t => t.id === activeTab)?.data || [];

  return (
    <Card className="flex flex-col h-full min-h-[400px] border-slate-200 shadow-sm overflow-hidden bg-white">
      <div className="flex border-b border-slate-200 bg-[#FAFAFA] overflow-x-auto scrollbar-hide px-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-3 text-[11px] font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? "border-slate-800 text-slate-900 bg-white"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-100"
            }`}
          >
            {tab.label}
            <span className={`px-1.5 py-0.5 rounded font-mono text-[9px] ${
              activeTab === tab.id ? "bg-slate-200 text-slate-800" : "bg-slate-200/50 text-slate-400"
            }`}>
              {tab.data.length}
            </span>
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto relative">
        <table className="w-full text-xs text-left whitespace-nowrap">
          <thead className="bg-[#FAFAFA] text-slate-500 font-bold uppercase tracking-widest sticky top-0 border-b border-slate-200 z-10 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
            <tr>
              {activeTab === "companies" && (
                <><th className="px-5 py-3">Domain</th><th className="px-5 py-3">Company Name</th><th className="px-5 py-3 text-right">Confidence Score</th></>
              )}
              {activeTab === "decisionMakers" && (
                <><th className="px-5 py-3">Full Name</th><th className="px-5 py-3">Job Title</th><th className="px-5 py-3">Target Account</th><th className="px-5 py-3">Profile Link</th></>
              )}
              {activeTab === "contacts" && (
                <><th className="px-5 py-3">Prospect Name</th><th className="px-5 py-3">Verified Email</th><th className="px-5 py-3">Resolution Status</th><th className="px-5 py-3 text-right">Confidence</th></>
              )}
              {activeTab === "drafts" && (
                <><th className="px-5 py-3">Recipient Address</th><th className="px-5 py-3">Subject Line</th><th className="px-5 py-3 w-full">Content Preview</th></>
              )}
              {activeTab === "sendResults" && (
                <><th className="px-5 py-3">Recipient Address</th><th className="px-5 py-3">Delivery Status</th><th className="px-5 py-3 font-mono">Provider Message ID</th></>
              )}
              {activeTab === "failures" && (
                <><th className="px-5 py-3">Pipeline Stage</th><th className="px-5 py-3">Failed Item / Target</th><th className="px-5 py-3 w-full">Error Message / Reason</th></>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {currentData.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-5 py-16 text-center">
                  <div className="flex flex-col items-center justify-center gap-2 text-slate-400">
                    <DatabaseBackup className="w-6 h-6 opacity-20 mb-1" />
                    <span className="font-medium text-sm">No records populated</span>
                    <span className="text-[11px] max-w-xs text-center leading-relaxed">This table is currently empty. Run the pipeline to process data for this stage.</span>
                  </div>
                </td>
              </tr>
            ) : (
              <AnimatePresence>
                {currentData.map((row: any, i: number) => (
                  <motion.tr 
                    key={i}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.15, delay: i * 0.02 }}
                    className="hover:bg-slate-50 transition-colors group"
                  >
                    {activeTab === "companies" && (
                      <><td className="px-5 py-2.5 font-semibold text-slate-900">{row.domain}</td><td className="px-5 py-2.5 text-slate-600">{row.name}</td><td className="px-5 py-2.5 text-right font-mono text-slate-500">{row.confidence}</td></>
                    )}
                    {activeTab === "decisionMakers" && (
                      <><td className="px-5 py-2.5 font-semibold text-slate-900">{row.full_name}</td><td className="px-5 py-2.5 text-slate-600">{row.title}</td><td className="px-5 py-2.5 text-slate-500">{row.company_domain}</td><td className="px-5 py-2.5"><a href={row.linkedin_url} className="text-blue-600 hover:text-blue-700 hover:underline flex items-center gap-1 font-medium">View Profile <ExternalLink className="w-3 h-3"/></a></td></>
                    )}
                    {activeTab === "contacts" && (
                      <><td className="px-5 py-2.5 font-semibold text-slate-900">{row.full_name}</td><td className="px-5 py-2.5 text-slate-600 font-mono">{row.email}</td><td className="px-5 py-2.5"><span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-200">{row.verification_status}</span></td><td className="px-5 py-2.5 text-right font-mono text-slate-500">{row.confidence}</td></>
                    )}
                    {activeTab === "drafts" && (
                      <><td className="px-5 py-2.5 font-semibold text-slate-900 font-mono">{row.to_email}</td><td className="px-5 py-2.5 text-slate-800 font-medium max-w-[200px] truncate">{row.subject}</td><td className="px-5 py-2.5 text-slate-500 truncate max-w-sm">{row.body.substring(0, 80)}...</td></>
                    )}
                    {activeTab === "sendResults" && (
                      <><td className="px-5 py-2.5 font-semibold text-slate-900 font-mono">{row.to_email}</td><td className="px-5 py-2.5"><span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-200">{row.status}</span></td><td className="px-5 py-2.5 text-slate-400 font-mono">{row.provider_message_id}</td></>
                    )}
                    {activeTab === "failures" && (
                      <><td className="px-5 py-2.5"><span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200">{row.stage}</span></td><td className="px-5 py-2.5 text-slate-900 font-mono">{row.item}</td><td className="px-5 py-2.5 text-red-600 truncate max-w-sm">{row.error}</td></>
                    )}
                  </motion.tr>
                ))}
              </AnimatePresence>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
