import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { z } from "zod";

import type { TelemetryConfig, TelemetrySessionStats } from "./types.js";

const TelemetrySessionStatsSchema = z.object({
  session_id: z.string().min(1),
  raw_tokens_avoided: z.number().nonnegative(),
  distill_tokens_spent: z.number().nonnegative(),
  cache_hits: z.number().int().nonnegative(),
  cache_misses: z.number().int().nonnegative(),
  distill_operations: z.number().int().nonnegative(),
  metadata_only_operations: z.number().int().nonnegative(),
  escalation_count: z.number().int().nonnegative(),
  fallback_count: z.number().int().nonnegative(),
  escalation_rate: z.number().min(0).max(1),
  fallback_rate: z.number().min(0).max(1),
  updated_at: z.string().min(1),
});

function initialSessionStats(sessionID: string): TelemetrySessionStats {
  return {
    session_id: sessionID,
    raw_tokens_avoided: 0,
    distill_tokens_spent: 0,
    cache_hits: 0,
    cache_misses: 0,
    distill_operations: 0,
    metadata_only_operations: 0,
    escalation_count: 0,
    fallback_count: 0,
    escalation_rate: 0,
    fallback_rate: 0,
    updated_at: new Date().toISOString(),
  };
}

function computeRates(stats: TelemetrySessionStats): TelemetrySessionStats {
  const totalOperations = Math.max(
    stats.distill_operations + stats.metadata_only_operations,
    1,
  );

  return {
    ...stats,
    escalation_rate: stats.escalation_count / totalOperations,
    fallback_rate: stats.fallback_count / totalOperations,
    updated_at: new Date().toISOString(),
  };
}

export class TelemetryStore {
  private readonly config: TelemetryConfig;

  constructor(config: TelemetryConfig) {
    this.config = config;
  }

  async init(): Promise<void> {
    if (!this.config.enabled || !this.config.directory) {
      return;
    }

    await mkdir(this.config.directory, { recursive: true });
  }

  private sessionPath(sessionID: string): string {
    if (!this.config.directory) {
      throw new Error("Telemetry directory is not configured.");
    }
    return join(this.config.directory, `${sessionID}.json`);
  }

  private async readSessionStats(sessionID: string): Promise<TelemetrySessionStats> {
    if (!this.config.enabled || !this.config.directory) {
      return initialSessionStats(sessionID);
    }

    const filePath = this.sessionPath(sessionID);
    if (!existsSync(filePath)) {
      return initialSessionStats(sessionID);
    }

    try {
      const raw = await readFile(filePath, "utf8");
      return TelemetrySessionStatsSchema.parse(JSON.parse(raw));
    } catch {
      return initialSessionStats(sessionID);
    }
  }

  private async writeSessionStats(stats: TelemetrySessionStats): Promise<void> {
    if (!this.config.enabled || !this.config.directory) {
      return;
    }

    const filePath = this.sessionPath(stats.session_id);
    const normalized = computeRates(stats);
    await writeFile(filePath, JSON.stringify(normalized, null, 2), "utf8");
  }

  async recordCacheHit(sessionID: string): Promise<void> {
    const stats = await this.readSessionStats(sessionID);
    stats.cache_hits += 1;
    await this.writeSessionStats(stats);
  }

  async recordCacheMiss(sessionID: string): Promise<void> {
    const stats = await this.readSessionStats(sessionID);
    stats.cache_misses += 1;
    await this.writeSessionStats(stats);
  }

  async recordDistillation(
    sessionID: string,
    payload: {
      rawTokensAvoided: number;
      distillTokensSpent: number;
      escalated: boolean;
    },
  ): Promise<void> {
    const stats = await this.readSessionStats(sessionID);
    stats.distill_operations += 1;
    stats.raw_tokens_avoided += Math.max(payload.rawTokensAvoided, 0);
    stats.distill_tokens_spent += Math.max(payload.distillTokensSpent, 0);
    if (payload.escalated) {
      stats.escalation_count += 1;
    }
    await this.writeSessionStats(stats);
  }

  async recordMetadataOnly(sessionID: string, rawTokensAvoided: number): Promise<void> {
    const stats = await this.readSessionStats(sessionID);
    stats.metadata_only_operations += 1;
    stats.raw_tokens_avoided += Math.max(rawTokensAvoided, 0);
    await this.writeSessionStats(stats);
  }

  async recordFallback(sessionID: string): Promise<void> {
    const stats = await this.readSessionStats(sessionID);
    stats.fallback_count += 1;
    await this.writeSessionStats(stats);
  }

  async getSessionStats(sessionID: string): Promise<TelemetrySessionStats> {
    const stats = await this.readSessionStats(sessionID);
    return computeRates(stats);
  }
}
