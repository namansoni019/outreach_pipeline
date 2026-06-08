"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { CommandBar } from "@/components/layout/CommandBar";
import { ResultsTabs } from "@/components/ResultsTabs";
import { ArrowUp, ArrowDown, Minus, Play, Check, RefreshCw, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePipeline } from "@/lib/usePipeline";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const pipeline = usePipeline();
  const [domainInput, setDomainInput] = useState("");
  const [useBackend, setUseBackend] = useState(true);
  const [limitInput, setLimitInput] = useState(5);
  const [isDryRun, setIsDryRun] = useState(true);

  // Determine what results to show. 
  // If there's an active run, show its contacts. Otherwise show latest run's contacts or empty array.
  const displayRun = pipeline.activeRun || pipeline.runs[0];
  const contacts = displayRun?.contacts || [];

  return (
    <div className="flex h-screen bg-surface-base text-ink-primary font-sans overflow-hidden selection:bg-brand-muted selection:text-brand">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <CommandBar />
        <main className="flex-1 overflow-y-auto p-8">
          
          {activeTab === "Dashboard" && (
            <div className="max-w-[1200px] mx-auto space-y-6">
              {/* Header */}
              <div>
                <h2 className="text-[28px] font-bold text-ink-primary tracking-tight">Dashboard</h2>
                <p className="text-[15px] text-ink-secondary mt-1">Overview of your active pipeline and recent outreach performance.</p>
              </div>

            {/* Metrics Row */}
            <div className="grid grid-cols-4 gap-4">
              <MetricCard 
                title="COMPANIES FOUND" 
                value={(displayRun?.companies?.length || 0).toString()} 
                trend="neutral" 
              />
              <MetricCard 
                title="DECISION MAKERS" 
                value={(displayRun?.decisionMakers?.length || 0).toString()} 
                trend="neutral" 
              />
              <MetricCard 
                title="EMAILS RESOLVED" 
                value={(displayRun?.contacts?.length || 0).toString()} 
                trend="neutral" 
              />
              <MetricCard 
                title="EMAILS SENT" 
                value={(displayRun?.sendResults?.length || 0).toString()} 
                trend="neutral" 
              />
            </div>

            {/* Bottom Grid */}
            <div className="grid grid-cols-12 gap-6">
              
              {/* Left Column: New Pipeline Run */}
              <div className="col-span-5 bg-surface-card rounded-xl p-6 shadow-card border border-surface-border h-fit">
                <h3 className="text-[15px] font-bold text-ink-primary">New Pipeline Run</h3>
                <p className="text-[13px] text-ink-secondary mb-5 mt-0.5">Initialize a new targeted domain search.</p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-[13px] font-semibold text-ink-primary mb-1.5">Target Domain</label>
                    <input 
                      type="text" 
                      placeholder="e.g., acme-corp.com"
                      value={domainInput}
                      onChange={(e) => setDomainInput(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-md border border-surface-border text-[14px] text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-all bg-white"
                    />
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-1">
                      <label className="block text-[13px] font-semibold text-ink-primary mb-1.5">Company Limit</label>
                      <input 
                        type="number" 
                        value={limitInput}
                        onChange={(e) => setLimitInput(parseInt(e.target.value) || 5)}
                        className="w-full px-4 py-2.5 rounded-md border border-surface-border text-[14px] text-ink-primary focus:outline-none focus:ring-2 focus:ring-brand/30 focus:border-brand transition-all bg-white"
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 mt-2 pt-2 border-t border-surface-border">
                    <label className="text-[13px] font-medium text-ink-primary flex items-center gap-2 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={isDryRun}
                        onChange={(e) => setIsDryRun(e.target.checked)}
                        className="rounded border-surface-border text-brand focus:ring-brand"
                      />
                      Dry Run (Generate Drafts Only)
                    </label>
                  </div>
                  
                  <button 
                    onClick={() => {
                      if (!domainInput.trim()) setDomainInput("acme-corp.com");
                      pipeline.startPipeline(domainInput.trim() || "acme-corp.com", isDryRun, true, limitInput);
                    }}
                    disabled={pipeline.activeRun?.status === 'running'}
                    className="w-full flex items-center justify-center gap-2 bg-brand hover:bg-brand-hover text-white py-2.5 rounded-md text-[14px] font-semibold transition-colors mt-4 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
                    <Play size={16} className="fill-current" />
                    {pipeline.activeRun?.status === 'running' ? 'Running Pipeline...' : 'Run Pipeline'}
                  </button>
                </div>
              </div>

              {/* Right Column: Recent Results */}
              <div className="col-span-7 bg-surface-card rounded-xl p-0 shadow-card border border-surface-border overflow-hidden">
                <div className="flex items-center justify-between p-5 border-b border-surface-border">
                  <h3 className="text-[15px] font-bold text-ink-primary">Recent Results</h3>
                  <a href="#" className="text-[13px] font-medium text-ink-secondary hover:text-ink-primary transition-colors flex items-center gap-1">
                    View All <span>&rarr;</span>
                  </a>
                </div>
                
                <table className="w-full">
                  <thead className="bg-surface-hover/50 border-b border-surface-border">
                    <tr>
                      <th className="text-left text-[11px] font-semibold text-ink-secondary uppercase tracking-wider py-3 px-5">Company Name</th>
                      <th className="text-left text-[11px] font-semibold text-ink-secondary uppercase tracking-wider py-3 px-5">Status</th>
                      <th className="text-left text-[11px] font-semibold text-ink-secondary uppercase tracking-wider py-3 px-5">Contact Name</th>
                      <th className="text-left text-[11px] font-semibold text-ink-secondary uppercase tracking-wider py-3 px-5">Resolution Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surface-border">
                    {contacts.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-[13px] text-ink-secondary">
                          No recent results. Run a pipeline to see data here.
                        </td>
                      </tr>
                    ) : (
                      contacts.map((contact, i) => (
                        <TableRow 
                          key={i}
                          company={contact.company_domain} 
                          status="Found" 
                          contact={contact.full_name} 
                          type={contact.verification_status} 
                        />
                      ))
                    )}
                  </tbody>
                </table>
              </div>

            </div>

            </div>
          )}

          {activeTab === "Results" && (
            <div className="max-w-[1200px] mx-auto space-y-6 h-full flex flex-col">
              <div>
                <h2 className="text-[28px] font-bold text-ink-primary tracking-tight">Results</h2>
                <p className="text-[15px] text-ink-secondary mt-1">Detailed breakdown of pipeline execution data.</p>
              </div>
              <div className="flex-1 min-h-0">
                <ResultsTabs activeRun={displayRun} />
              </div>
            </div>
          )}

          {activeTab !== "Dashboard" && activeTab !== "Results" && (
            <div className="max-w-[1200px] mx-auto space-y-6">
              <h2 className="text-[28px] font-bold text-ink-primary tracking-tight">{activeTab}</h2>
              <p className="text-[15px] text-ink-secondary mt-1">This section is currently under construction.</p>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

// --- Helper Components ---

function MetricCard({ title, value, trend }: { title: string, value: string, trend: 'up' | 'down' | 'neutral' }) {
  return (
    <div className="bg-surface-card rounded-xl p-5 shadow-card border border-surface-border flex flex-col justify-between h-[100px]">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold text-ink-secondary uppercase tracking-wider">{title}</span>
        {trend === 'up' && <ArrowUp size={16} className="text-status-success" />}
        {trend === 'down' && <ArrowDown size={16} className="text-status-danger" />}
        {trend === 'neutral' && <Minus size={16} className="text-ink-muted" />}
      </div>
      <div className="text-[28px] font-bold text-ink-primary tracking-tight leading-none">{value}</div>
    </div>
  );
}

function PipelineStep({ title, subtitle, status, progress }: { title: string, subtitle: string, status: 'completed' | 'active' | 'pending', progress: string }) {
  return (
    <div className="flex flex-col items-center gap-3 relative z-10 w-32 bg-surface-card">
      <div className={cn(
        "w-10 h-10 rounded-full flex items-center justify-center shadow-sm z-10",
        status === 'completed' ? "bg-brand text-white" :
        status === 'active' ? "bg-brand-muted border-2 border-brand text-brand" :
        "bg-surface-base border border-surface-border text-ink-muted"
      )}>
        {status === 'completed' && <Check size={18} strokeWidth={3} />}
        {status === 'active' && <RefreshCw size={18} className="animate-spin" />}
        {status === 'pending' && <Clock size={18} />}
      </div>
      <div className="text-center">
        <div className={cn(
          "text-[13px] font-bold",
          status === 'pending' ? "text-ink-secondary" : "text-ink-primary"
        )}>{title}</div>
        <div className="text-[11px] font-medium text-ink-muted mt-0.5">{subtitle}</div>
      </div>
      
      {/* Progress Bar Override for Completed/Active */}
      {status !== 'pending' && (
        <div 
          className="absolute top-5 h-[2px] bg-brand -z-10 transition-all duration-500" 
          style={{ right: '50%', width: status === 'completed' ? '200%' : '50%' }} 
        />
      )}
    </div>
  );
}

function TableRow({ company, status, contact, type }: { company: string, status: 'Found' | 'Pending' | 'Failed', contact: string, type: string }) {
  return (
    <tr className="hover:bg-surface-hover/50 transition-colors">
      <td className="py-3 px-5 text-[14px] font-medium text-ink-primary">{company}</td>
      <td className="py-3 px-5">
        <span className={cn(
          "px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider",
          status === 'Found' ? "bg-status-successbg text-status-success" :
          status === 'Pending' ? "bg-status-pendingbg text-status-pending" :
          "bg-status-dangerbg text-status-danger"
        )}>
          {status}
        </span>
      </td>
      <td className="py-3 px-5 text-[14px] text-ink-secondary">{contact}</td>
      <td className="py-3 px-5 text-[14px] text-ink-secondary">{type}</td>
    </tr>
  );
}
