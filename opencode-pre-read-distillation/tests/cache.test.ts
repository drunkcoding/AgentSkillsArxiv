import { afterEach, describe, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { DistillationCache } from "../src/cache";
import { type DistilledReadResult } from "../src/types";

const tempDirs: string[] = [];

async function makeTempDir() {
  const directory = await mkdtemp(join(tmpdir(), "prd-cache-test-"));
  tempDirs.push(directory);
  return directory;
}

function sampleResult(filePath: string): DistilledReadResult {
  return {
    schema_version: "prd.distilled_read.v1",
    file_path: filePath,
    sha256: "a".repeat(64),
    file_bytes: 100,
    estimated_input_tokens: 25,
    summary: "summary",
    key_points: ["point"],
    symbols: [],
    sections: [],
    warnings: [],
    escalation_hints: [],
    raw_read_recommended: false,
    provider: "openai-compatible",
    model: "gpt-4o-mini",
    usage: {
      inputTokens: 10,
      outputTokens: 5,
      totalTokens: 15,
    },
  };
}

afterEach(async () => {
  await Promise.all(tempDirs.map((directory) => rm(directory, { recursive: true, force: true })));
  tempDirs.length = 0;
});

describe("DistillationCache", () => {
  test("set/get roundtrip", async () => {
    const directory = await makeTempDir();
    let now = 1_000;

    const cache = new DistillationCache(
      {
        enabled: true,
        ttlSec: 60,
        maxEntries: 10,
        maxBytes: 1_000_000,
        directory,
      },
      { now: () => now },
    );

    await cache.init();

    const key = cache.buildCacheKey("hash", "model", "policy-v1");
    await cache.set({
      key,
      model: "model",
      policyVersion: "policy-v1",
      filePath: "/tmp/file.ts",
      fileHash: "b".repeat(64),
      result: sampleResult("/tmp/file.ts"),
    });

    const hit = await cache.get(key);
    expect(hit).not.toBeNull();
    expect(hit?.result.summary).toBe("summary");

    now += 61_000;
    const expired = await cache.get(key);
    expect(expired).toBeNull();
  });

  test("enforces max entries", async () => {
    const directory = await makeTempDir();
    let now = 1_000;

    const cache = new DistillationCache(
      {
        enabled: true,
        ttlSec: 60,
        maxEntries: 2,
        maxBytes: 1_000_000,
        directory,
      },
      { now: () => now },
    );

    await cache.init();

    for (let i = 0; i < 3; i += 1) {
      const key = cache.buildCacheKey(`hash-${i}`, "model", "policy-v1");
      await cache.set({
        key,
        model: "model",
        policyVersion: "policy-v1",
        filePath: `/tmp/file-${i}.ts`,
        fileHash: `${i}`.repeat(64),
        result: sampleResult(`/tmp/file-${i}.ts`),
      });
      now += 1_000;
    }

    const key0 = cache.buildCacheKey("hash-0", "model", "policy-v1");
    const key1 = cache.buildCacheKey("hash-1", "model", "policy-v1");
    const key2 = cache.buildCacheKey("hash-2", "model", "policy-v1");

    const entry0 = await cache.get(key0);
    const entry1 = await cache.get(key1);
    const entry2 = await cache.get(key2);

    const remaining = [entry0, entry1, entry2].filter((entry) => entry !== null);
    expect(remaining.length).toBeLessThanOrEqual(2);
    expect(entry2).not.toBeNull();
  });
});
