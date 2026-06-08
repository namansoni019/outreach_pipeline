"use client";

import { useState } from "react";
import {
  PipelineRun,
  ActivityLogItem,
} from "./types";

const SYSTEM_LOGS: ActivityLogItem[] = [
  { id: "sys-1", timestamp: new Date().toISOString(), message: "System initialized: Revenue Operations Pipeline", type: "info" },
  { id: "sys-2", timestamp: new Date().toISOString(), message: "Mock data engine loaded and ready", type: "success" },
  { id: "sys-3", timestamp: new Date().toISOString(), message: "Safety checkpoint protocol enabled", type: "info" }
];

export function usePipeline() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  const activeRun = runs.find((r) => r.id === activeRunId) || null;

  const updateActiveRun = (updates: Partial<PipelineRun> | ((prev: PipelineRun) => Partial<PipelineRun>)) => {
    setRuns((prev) =>
      prev.map((r) => {
        if (r.id === activeRunId) {
          const newValues = typeof updates === 'function' ? updates(r) : updates;
          return { ...r, ...newValues };
        }
        return r;
      })
    );
  };

  const addLog = (runId: string, message: string, type: ActivityLogItem["type"] = "info", stage?: ActivityLogItem["stage"]) => {
    setRuns((prev) =>
      prev.map((r) => {
        if (r.id === runId) {
          return {
            ...r,
            activity: [
              ...r.activity,
              {
                id: `log_${Date.now()}_${Math.random()}`,
                timestamp: new Date().toISOString(),
                message,
                type,
                stage,
              },
            ],
          };
        }
        return r;
      })
    );
  };

  const startPipeline = async (domain: string, isDryRun: boolean, useBackend: boolean = true, limit: number = 5) => {

    const newRun: PipelineRun = {
      id: `run_${Date.now()}`,
      seed_domain: domain,
      timestamp: new Date().toISOString(),
      mode: "real",
      isDryRun,
      status: "running",
      stage: "ocean",
      companies: [],
      decisionMakers: [],
      contacts: [],
      drafts: [],
      sendResults: [],
      failures: [],
      activity: [{ id: `log_${Date.now()}`, timestamp: new Date().toISOString(), message: `Executing real pipeline via FastAPI backend...`, type: "info" }],
    };
    setRuns((prev) => [newRun, ...prev]);
    setActiveRunId(newRun.id);

    try {
      // 1. Start the run on the backend
      const res = await fetch("http://127.0.0.1:8000/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain,
          mode: "mock", // We use mock backend mode for now so it doesn't need real API keys, but it goes through the real Python backend
          limit: limit,
          dry_run: isDryRun,
          auto_confirm: true
        })
      });

      if (!res.ok) throw new Error("Backend API request failed");
      const data = await res.json();
      const runId = data.run_id;

      // 2. Fetch the full run details
      const detailRes = await fetch(`http://127.0.0.1:8000/api/runs/${runId}`);
      if (!detailRes.ok) throw new Error("Failed to fetch run details");
      const details = await detailRes.json();

      // 3. Update state with real data
      setRuns((prev) =>
        prev.map((r) =>
          r.id === newRun.id
            ? {
                ...r,
                id: runId,
                status: "completed",
                stage: "done",
                companies: details.companies,
                decisionMakers: details.decisionMakers,
                contacts: details.resolvedContacts,
                drafts: details.emailDrafts,
                sendResults: details.sendResults,
                failures: details.failures,
                activity: [
                  ...r.activity,
                  { id: `log_${Date.now()}_success`, timestamp: new Date().toISOString(), message: `Pipeline execution complete.`, type: "success" }
                ],
              }
            : r
        )
      );
      setActiveRunId(runId);
    } catch (err) {
      console.error(err);
      updateActiveRun({ status: "failed" });
      addLog(newRun.id, `Pipeline execution failed: ${err}`, "error");
    }
  };

  const confirmSend = () => {
    // Left empty for now. Safety checkpoint via API not implemented.
    console.warn("confirmSend not implemented for backend mode");
  };

  const cancelSend = () => {
    // Left empty for now.
    console.warn("cancelSend not implemented for backend mode");
  };

  const reset = () => {
    setActiveRunId(null);
  };

  return {
    runs,
    activeRun,
    setActiveRunId,
    startPipeline,
    confirmSend,
    cancelSend,
    reset,
    SYSTEM_LOGS
  };
}
