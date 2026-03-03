import { relative } from "node:path";

import type { FileClassification, PrdConfig, TelemetrySessionStats } from "./types.js";

export const PRD_PREFIX = "▣ PRD |";

export interface DistillAnnotationPayload {
  filePath: string;
  worktree?: string;
  rawTokens: number;
  distilledTokens: number;
  cache: "hit" | "miss";
  latencyMs?: number;
}

export interface MetadataOnlyAnnotationPayload {
  filePath: string;
  worktree?: string;
  rawTokens: number;
  classification: FileClassification;
}

export interface PrdContextViewPayload {
  sessionID: string;
  config: PrdConfig;
  stats: TelemetrySessionStats;
  cacheEntries: number;
  cacheBytes: number;
}

function clampNonNegativeInteger(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(Math.round(value), 0);
}

function formatInteger(value: number): string {
  return clampNonNegativeInteger(value).toLocaleString("en-US");
}

function formatPercent(value: number): string {
  if (!Number.isFinite(value)) {
    return "0";
  }
  return String(Math.max(0, Math.min(100, Math.round(value))));
}

export function formatApproxK(value: number): string {
  const normalized = Math.max(Number.isFinite(value) ? value : 0, 0) / 1_000;
  return `${normalized.toFixed(1).replace(/\.0$/, "")}K`;
}

export function formatBytes(value: number): string {
  const bytes = Math.max(Number.isFinite(value) ? value : 0, 0);
  if (bytes >= 1_000_000_000) {
    return `${(bytes / 1_000_000_000).toFixed(1).replace(/\.0$/, "")} GB`;
  }
  if (bytes >= 1_000_000) {
    return `${(bytes / 1_000_000).toFixed(1).replace(/\.0$/, "")} MB`;
  }
  if (bytes >= 1_000) {
    return `${(bytes / 1_000).toFixed(1).replace(/\.0$/, "")} KB`;
  }
  return `${formatInteger(bytes)} B`;
}

export function toDisplayFilePath(filePath: string, worktree?: string): string {
  if (worktree) {
    const rel = relative(worktree, filePath);
    if (rel && !rel.startsWith("../") && rel !== "..") {
      return rel;
    }
  }
  return filePath;
}

export function prependPrdLine(content: string, line: string): string {
  if (!line) {
    return content;
  }
  if (content.startsWith(`${line}\n`) || content === line) {
    return content;
  }
  return `${line}\n${content}`;
}

export function formatDistillAnnotation(payload: DistillAnnotationPayload): string {
  const displayPath = toDisplayFilePath(payload.filePath, payload.worktree);
  const rawTokens = formatInteger(payload.rawTokens);
  const distilledTokens = formatInteger(payload.distilledTokens);

  if (payload.cache === "hit") {
    return `${PRD_PREFIX} distilled ${displayPath} (${rawTokens}→${distilledTokens} tokens, cache hit)`;
  }

  const latencyMs = formatInteger(payload.latencyMs ?? 0);
  return `${PRD_PREFIX} distilled ${displayPath} (${rawTokens}→${distilledTokens} tokens, ${latencyMs}ms)`;
}

export function formatMetadataOnlyAnnotation(payload: MetadataOnlyAnnotationPayload): string {
  const displayPath = toDisplayFilePath(payload.filePath, payload.worktree);
  const rawTokens = formatInteger(payload.rawTokens);
  return `${PRD_PREFIX} metadata-only ${displayPath} (${rawTokens} tokens skipped, ${payload.classification})`;
}

export function formatFallbackAnnotation(filePath: string, worktree?: string): string {
  const displayPath = toDisplayFilePath(filePath, worktree);
  return `${PRD_PREFIX} fallback to raw ${displayPath} (distillation failed)`;
}

export function formatSessionBanner(stats: TelemetrySessionStats, sessionID: string): string | null {
  const operations = stats.distill_operations + stats.metadata_only_operations;
  if (operations < 1) {
    return null;
  }

  const cacheTotal = stats.cache_hits + stats.cache_misses;
  const hitRate = cacheTotal > 0 ? (stats.cache_hits / cacheTotal) * 100 : 0;

  return `${PRD_PREFIX} ~${formatApproxK(stats.raw_tokens_avoided)} tokens saved | ${stats.distill_operations} distilled, ${stats.metadata_only_operations} metadata-only | cache ${formatPercent(hitRate)}% | session ${sessionID}`;
}

function formatBoolean(value: boolean): string {
  return value ? "on" : "off";
}

export function formatStatsTable(sessionID: string, stats: TelemetrySessionStats): string {
  const cacheTotal = stats.cache_hits + stats.cache_misses;
  const hitRate = cacheTotal > 0 ? (stats.cache_hits / cacheTotal) * 100 : 0;

  return [
    `${PRD_PREFIX} session stats`,
    `→ session ${sessionID}`,
    `→ raw tokens avoided: ~${formatApproxK(stats.raw_tokens_avoided)} tokens`,
    `→ distill tokens spent: ${formatInteger(stats.distill_tokens_spent)} tokens`,
    `→ operations: ${stats.distill_operations} distilled, ${stats.metadata_only_operations} metadata-only`,
    `→ cache: ${stats.cache_hits} hit, ${stats.cache_misses} miss (${formatPercent(hitRate)}%)`,
    `→ escalation rate: ${formatPercent(stats.escalation_rate * 100)}%`,
    `→ fallback rate: ${formatPercent(stats.fallback_rate * 100)}%`,
    `→ updated: ${stats.updated_at}`,
  ].join("\n");
}

export function formatContextView(payload: PrdContextViewPayload): string {
  const { config, stats } = payload;

  return [
    `${PRD_PREFIX} context`,
    `→ session ${payload.sessionID}`,
    `→ model ${config.llm.provider}/${config.llm.model}`,
    `→ policy ${config.policy.policyVersion} (pass≤${formatInteger(config.policy.passThroughMaxTokens)}t, distill≥${formatInteger(config.policy.distillMinTokens)}t, metadata≥${formatInteger(config.policy.metadataOnlyMinTokens)}t)`,
    `→ cache ${formatBoolean(config.cache.enabled)} (${formatInteger(payload.cacheEntries)} entries, ${formatBytes(payload.cacheBytes)})`,
    `→ display annotations ${formatBoolean(config.display.operationAnnotations)}, banner ${formatBoolean(config.display.sessionSummaryBanner)} every ${config.display.bannerEveryToolResults} tool results, slash ${formatBoolean(config.display.slashCommands)}`,
    `→ session activity ${stats.distill_operations} distilled, ${stats.metadata_only_operations} metadata-only, ${stats.fallback_count} fallback`,
    `→ session savings ~${formatApproxK(stats.raw_tokens_avoided)} tokens`,
  ].join("\n");
}

export function formatCommandHelp(): string {
  return [
    `${PRD_PREFIX} commands`,
    "→ /prd stats",
    "→ /prd context",
    "→ /prd cache clear",
  ].join("\n");
}

export function formatCacheClearedMessage(sessionID: string): string {
  return `${PRD_PREFIX} cache cleared (session ${sessionID})`;
}
