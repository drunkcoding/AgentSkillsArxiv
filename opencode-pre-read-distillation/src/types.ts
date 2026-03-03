import { z } from "zod";

export type DecisionMode = "pass_through" | "distill" | "metadata_only";

export type FileClassification =
  | "normal"
  | "generated"
  | "minified"
  | "binary"
  | "documentation"
  | "unknown";

export type IntentClassification = "edit" | "debug" | "analysis" | "unknown";

export interface TaskContext {
  sessionID?: string;
  lastUserMessage?: string;
  intentHint?: IntentClassification;
  forceRaw?: boolean;
  forceMetadataOnly?: boolean;
}

export interface LlmConfig {
  provider: "anthropic" | "openai-compatible";
  model: string;
  apiKeyEnv: string;
  baseURL?: string | undefined;
  timeoutMs: number;
  temperature: number;
  maxOutputTokens: number;
}

export interface PolicyConfig {
  policyVersion: string;
  passThroughMaxTokens: number;
  passThroughMaxBytes: number;
  editIntentPassThroughMaxTokens: number;
  distillMinTokens: number;
  distillMinBytes: number;
  metadataOnlyMinTokens: number;
  metadataOnlyMinBytes: number;
  maxDistillInputChars: number;
  generatedPathGlobs: string[];
  generatedContentMarkers: string[];
  minifiedLineLength: number;
  minifiedLongLineCount: number;
  minifiedNonWhitespaceRatio: number;
  binaryExtensions: string[];
  documentationExtensions: string[];
  alwaysPassThroughGlobs: string[];
  alwaysMetadataOnlyGlobs: string[];
}

export interface CacheConfig {
  enabled: boolean;
  ttlSec: number;
  maxEntries: number;
  maxBytes: number;
  directory?: string | undefined;
}

export interface TelemetryConfig {
  enabled: boolean;
  directory?: string | undefined;
}

export interface HooksConfig {
  interceptReadTool: boolean;
  systemPrompt: boolean;
  toolDefinition: boolean;
  chatMessageTracking: boolean;
}

export interface CustomToolsConfig {
  distilledRead: boolean;
  rawRead: boolean;
  fileOutline: boolean;
}

export interface PromptConfig {
  injectSystemPrompt: boolean;
  appendReadToolDefinition: boolean;
}

export interface PrdConfig {
  $schema?: string | undefined;
  enabled: boolean;
  debug: boolean;
  llm: LlmConfig;
  policy: PolicyConfig;
  cache: CacheConfig;
  telemetry: TelemetryConfig;
  hooks: HooksConfig;
  customTools: CustomToolsConfig;
  prompt: PromptConfig;
}

export interface DecisionResult {
  mode: DecisionMode;
  reason: string;
  fileClassification: FileClassification;
  intentClassification: IntentClassification;
}

export const DistilledSymbolSchema = z.object({
  name: z.string().min(1),
  kind: z.string().min(1),
  line: z.number().int().positive().optional(),
  signature: z.string().optional(),
  why_important: z.string().min(1),
});

export const DistilledSectionSchema = z.object({
  start_line: z.number().int().positive(),
  end_line: z.number().int().positive(),
  label: z.string().min(1),
  why_important: z.string().min(1),
});

export const DistilledReadModelPayloadSchema = z.object({
  summary: z.string().min(1),
  key_points: z.array(z.string().min(1)).default([]),
  symbols: z.array(DistilledSymbolSchema).default([]),
  sections: z.array(DistilledSectionSchema).default([]),
  warnings: z.array(z.string().min(1)).default([]),
  escalation_hints: z.array(z.string().min(1)).default([]),
  raw_read_recommended: z.boolean().default(false),
});

export type DistilledReadModelPayload = z.infer<
  typeof DistilledReadModelPayloadSchema
>;

export interface DistillerUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

export const DistilledReadResultSchema = z.object({
  schema_version: z.literal("prd.distilled_read.v1"),
  file_path: z.string().min(1),
  sha256: z.string().min(64),
  file_bytes: z.number().int().nonnegative(),
  estimated_input_tokens: z.number().int().nonnegative(),
  summary: z.string().min(1),
  key_points: z.array(z.string().min(1)),
  symbols: z.array(DistilledSymbolSchema),
  sections: z.array(DistilledSectionSchema),
  warnings: z.array(z.string().min(1)),
  escalation_hints: z.array(z.string().min(1)),
  raw_read_recommended: z.boolean(),
  provider: z.string().min(1),
  model: z.string().min(1),
  usage: z
    .object({
      inputTokens: z.number().int().nonnegative(),
      outputTokens: z.number().int().nonnegative(),
      totalTokens: z.number().int().nonnegative(),
    })
    .optional(),
});

export type DistilledReadResult = z.infer<typeof DistilledReadResultSchema>;

export interface CacheRecord {
  key: string;
  createdAt: number;
  expiresAt: number;
  model: string;
  policyVersion: string;
  filePath: string;
  fileHash: string;
  result: DistilledReadResult;
}

export interface ParsedReadToolOutput {
  filePath: string;
  fileType: "file" | "directory" | "unknown";
  content: string;
  lineCount: number;
  charCount: number;
}

export interface MetadataOnlyPayload {
  filePath: string;
  fileBytes: number;
  estimatedTokens: number;
  fileClassification: FileClassification;
  reason: string;
}

export interface TelemetrySessionStats {
  session_id: string;
  raw_tokens_avoided: number;
  distill_tokens_spent: number;
  cache_hits: number;
  cache_misses: number;
  distill_operations: number;
  metadata_only_operations: number;
  escalation_count: number;
  fallback_count: number;
  escalation_rate: number;
  fallback_rate: number;
  updated_at: string;
}
