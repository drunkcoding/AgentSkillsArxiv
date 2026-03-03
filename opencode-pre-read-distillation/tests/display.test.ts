import { describe, expect, test } from "bun:test";

import { DEFAULT_PRD_CONFIG } from "../src/config";
import {
  formatContextView,
  formatDistillAnnotation,
  formatFallbackAnnotation,
  formatMetadataOnlyAnnotation,
  formatSessionBanner,
  formatStatsTable,
  prependPrdLine,
} from "../src/display";
import type { TelemetrySessionStats } from "../src/types";

function sampleStats(overrides: Partial<TelemetrySessionStats> = {}): TelemetrySessionStats {
  return {
    session_id: "session-1",
    raw_tokens_avoided: 3_420,
    distill_tokens_spent: 418,
    cache_hits: 2,
    cache_misses: 1,
    distill_operations: 2,
    metadata_only_operations: 1,
    escalation_count: 0,
    fallback_count: 0,
    escalation_rate: 0,
    fallback_rate: 0,
    updated_at: "2026-03-03T12:00:00.000Z",
    ...overrides,
  };
}

describe("display formatting", () => {
  test("formats distill annotation for cache hit", () => {
    const text = formatDistillAnnotation({
      filePath: "/repo/src/api/auth.ts",
      worktree: "/repo",
      rawTokens: 3_420,
      distilledTokens: 418,
      cache: "hit",
    });

    expect(text).toBe("▣ PRD | distilled src/api/auth.ts (3,420→418 tokens, cache hit)");
  });

  test("formats distill annotation for cache miss with latency", () => {
    const text = formatDistillAnnotation({
      filePath: "/repo/src/api/auth.ts",
      worktree: "/repo",
      rawTokens: 3_420,
      distilledTokens: 418,
      cache: "miss",
      latencyMs: 127,
    });

    expect(text).toBe("▣ PRD | distilled src/api/auth.ts (3,420→418 tokens, 127ms)");
  });

  test("formats metadata-only and fallback annotations", () => {
    const metadata = formatMetadataOnlyAnnotation({
      filePath: "/repo/src/generated/client.ts",
      worktree: "/repo",
      rawTokens: 12_000,
      classification: "generated",
    });
    const fallback = formatFallbackAnnotation("/repo/src/api/auth.ts", "/repo");

    expect(metadata).toBe(
      "▣ PRD | metadata-only src/generated/client.ts (12,000 tokens skipped, generated)",
    );
    expect(fallback).toBe("▣ PRD | fallback to raw src/api/auth.ts (distillation failed)");
  });

  test("prepends annotations without duplication", () => {
    const base = "[PRE_READ_DISTILL_V1]\n...";
    const line = "▣ PRD | distilled src/api/auth.ts (3,420→418 tokens, cache hit)";

    const once = prependPrdLine(base, line);
    const twice = prependPrdLine(once, line);

    expect(once.startsWith(line)).toBe(true);
    expect(twice).toBe(once);
  });

  test("formats session banner only when activity exists", () => {
    const active = formatSessionBanner(sampleStats(), "session-1");
    const idle = formatSessionBanner(
      sampleStats({ distill_operations: 0, metadata_only_operations: 0 }),
      "session-1",
    );

    expect(active).toContain("▣ PRD | ~3.4K tokens saved");
    expect(active).toContain("cache 67%");
    expect(active).toContain("session session-1");
    expect(idle).toBeNull();
  });

  test("formats stats and context command output", () => {
    const stats = sampleStats();
    const statsText = formatStatsTable("session-1", stats);
    const contextText = formatContextView({
      sessionID: "session-1",
      config: DEFAULT_PRD_CONFIG,
      stats,
      cacheEntries: 12,
      cacheBytes: 45_000,
    });

    expect(statsText).toContain("▣ PRD | session stats");
    expect(statsText).toContain("→ operations: 2 distilled, 1 metadata-only");
    expect(contextText).toContain("▣ PRD | context");
    expect(contextText).toContain("→ cache on (12 entries");
    expect(contextText).toContain("→ display annotations on, banner on every 5 tool results, slash on");
  });
});
