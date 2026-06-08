export interface Company {
  domain: string;
  name: string;
  source: string;
  confidence?: number;
}

export interface DecisionMaker {
  company_domain: string;
  full_name: string;
  title: string;
  linkedin_url: string;
  source: string;
}

export interface ResolvedContact {
  company_domain: string;
  full_name: string;
  title: string;
  linkedin_url: string;
  email: string;
  verification_status: string;
  confidence?: number;
}

export interface EmailDraft {
  to_email: string;
  subject: string;
  body: string;
  contact_name: string;
  company_domain: string;
}

export interface EmailSendResult {
  to_email: string;
  status: string;
  provider_message_id?: string;
  error?: string;
}

export interface StageFailure {
  stage: string;
  item: string;
  error: string;
}

export interface ActivityLogItem {
  id: string;
  timestamp: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  stage?: "ocean" | "prospeo" | "eazyreach" | "draft" | "brevo" | "done";
}

export interface PipelineRun {
  id: string;
  seed_domain: string;
  timestamp: string;
  mode: "mock" | "real";
  isDryRun: boolean;
  status: "idle" | "running" | "paused" | "completed" | "failed";
  stage: "ocean" | "prospeo" | "eazyreach" | "draft" | "brevo" | "done";
  companies: Company[];
  decisionMakers: DecisionMaker[];
  contacts: ResolvedContact[];
  drafts: EmailDraft[];
  sendResults: EmailSendResult[];
  failures: StageFailure[];
  activity: ActivityLogItem[];
}

