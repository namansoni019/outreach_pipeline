"use client";

import { motion } from "framer-motion";
import { AlertOctagon, Send, X, ShieldAlert, MailWarning } from "lucide-react";
import { Button, Card } from "./ui";

export function SafetyConfirmModal({ activeRun, confirmSend, cancelSend }: { activeRun: any, confirmSend: () => void, cancelSend: () => void }) {
  if (!activeRun || activeRun.status !== "paused") return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
      />
      
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 12 }}
        transition={{ type: "spring", damping: 25, stiffness: 350 }}
        className="relative w-full max-w-2xl z-10"
      >
        <Card className="shadow-2xl border-slate-200 overflow-hidden ring-1 ring-slate-900/5">
          <div className="p-6 border-b border-slate-100 bg-white flex items-start justify-between relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-amber-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 opacity-50 pointer-events-none" />
            <div className="flex gap-4 relative z-10">
              <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center shrink-0 border border-amber-100 shadow-sm">
                <ShieldAlert className="w-6 h-6 text-amber-500" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 tracking-tight">Deployment Authorization Required</h2>
                <p className="text-sm text-slate-500 mt-1.5 leading-relaxed max-w-md">
                  Safety checkpoint reached. The pipeline has successfully generated drafts but requires explicit authorization before executing live outreach.
                </p>
              </div>
            </div>
            <button onClick={cancelSend} className="text-slate-400 hover:text-slate-600 transition-colors relative z-10 p-1 hover:bg-slate-100 rounded-md">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="p-6 bg-[#FAFAFA]">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <MailWarning className="w-4 h-4 text-slate-400" />
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Target Payload Summary</span>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded border border-emerald-100 shadow-sm">
                {activeRun.drafts.length} emails queued
              </span>
            </div>
            
            <div className="bg-white rounded-lg border border-slate-200 max-h-64 overflow-y-auto shadow-sm">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-widest sticky top-0 border-b border-slate-200">
                  <tr>
                    <th className="px-5 py-3.5">Target Address</th>
                    <th className="px-5 py-3.5">Subject Line Preview</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {activeRun.drafts.map((d: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-3 font-semibold text-slate-900 font-mono">{d.to_email}</td>
                      <td className="px-5 py-3 text-slate-600 truncate max-w-[300px]">{d.subject}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-4 flex items-start gap-3 p-3 bg-red-50 border border-red-100 rounded-lg">
              <AlertOctagon className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <div className="text-[11px] text-red-800 leading-relaxed font-medium">
                <strong>WARNING:</strong> This is a destructive action. Confirming will immediately transmit payloads to the Brevo API and execute live email delivery to the targets listed above.
              </div>
            </div>
          </div>
          
          <div className="p-5 bg-white border-t border-slate-100 flex justify-end gap-3">
            <Button variant="outline" onClick={cancelSend} className="font-semibold px-5 border-slate-200 hover:bg-slate-50">
              Abort Sequence
            </Button>
            <Button className="bg-emerald-600 hover:bg-emerald-700 text-white gap-2 border-transparent shadow-sm px-6 font-semibold" onClick={confirmSend}>
              <Send className="w-4 h-4" />
              Authorize & Dispatch
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
