import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { z } from "zod";

import type { CacheConfig, CacheRecord, DistilledReadResult } from "./types.js";

const CacheRecordSchema = z.object({
  key: z.string().min(1),
  createdAt: z.number().int().nonnegative(),
  expiresAt: z.number().int().nonnegative(),
  model: z.string().min(1),
  policyVersion: z.string().min(1),
  filePath: z.string().min(1),
  fileHash: z.string().min(64),
  result: z.unknown(),
});

export interface DistillationCacheOptions {
  now?: () => number;
}

function toUtf8ByteLength(input: string): number {
  return Buffer.byteLength(input, "utf8");
}

export function sha256Hex(input: string): string {
  return createHash("sha256").update(input).digest("hex");
}

export class DistillationCache {
  private readonly config: CacheConfig;

  private readonly now: () => number;

  constructor(config: CacheConfig, options: DistillationCacheOptions = {}) {
    this.config = config;
    this.now = options.now ?? (() => Date.now());
  }

  async init(): Promise<void> {
    if (!this.config.enabled || !this.config.directory) {
      return;
    }

    await mkdir(this.config.directory, { recursive: true });
    await this.cleanupExpired();
    await this.enforceLimits();
  }

  buildCacheKey(fileHash: string, model: string, policyVersion: string): string {
    return sha256Hex(`${fileHash}:${model}:${policyVersion}`);
  }

  hashContent(content: string): string {
    return sha256Hex(content);
  }

  private entryPath(key: string): string {
    if (!this.config.directory) {
      throw new Error("Cache directory is not configured.");
    }
    return join(this.config.directory, `${key}.json`);
  }

  async get(key: string): Promise<CacheRecord | null> {
    if (!this.config.enabled || !this.config.directory) {
      return null;
    }

    const path = this.entryPath(key);
    if (!existsSync(path)) {
      return null;
    }

    try {
      const raw = await readFile(path, "utf8");
      const parsed = CacheRecordSchema.parse(JSON.parse(raw));
      if (parsed.expiresAt <= this.now()) {
        await rm(path, { force: true });
        return null;
      }

      return {
        key: parsed.key,
        createdAt: parsed.createdAt,
        expiresAt: parsed.expiresAt,
        model: parsed.model,
        policyVersion: parsed.policyVersion,
        filePath: parsed.filePath,
        fileHash: parsed.fileHash,
        result: parsed.result as DistilledReadResult,
      };
    } catch {
      await rm(path, { force: true });
      return null;
    }
  }

  async set(record: {
    key: string;
    model: string;
    policyVersion: string;
    filePath: string;
    fileHash: string;
    result: DistilledReadResult;
  }): Promise<void> {
    if (!this.config.enabled || !this.config.directory) {
      return;
    }

    const now = this.now();
    const cacheRecord: CacheRecord = {
      key: record.key,
      createdAt: now,
      expiresAt: now + this.config.ttlSec * 1000,
      model: record.model,
      policyVersion: record.policyVersion,
      filePath: record.filePath,
      fileHash: record.fileHash,
      result: record.result,
    };

    const serialized = JSON.stringify(cacheRecord);
    await writeFile(this.entryPath(record.key), serialized, "utf8");

    await this.cleanupExpired();
    await this.enforceLimits();
  }

  private async cleanupExpired(): Promise<void> {
    if (!this.config.enabled || !this.config.directory || !existsSync(this.config.directory)) {
      return;
    }

    const files = await readdir(this.config.directory);
    for (const file of files) {
      if (!file.endsWith(".json")) {
        continue;
      }

      const absolute = join(this.config.directory, file);
      try {
        const raw = await readFile(absolute, "utf8");
        const parsed = CacheRecordSchema.parse(JSON.parse(raw));
        if (parsed.expiresAt <= this.now()) {
          await rm(absolute, { force: true });
        }
      } catch {
        await rm(absolute, { force: true });
      }
    }
  }

  private async enforceLimits(): Promise<void> {
    if (!this.config.enabled || !this.config.directory || !existsSync(this.config.directory)) {
      return;
    }

    const files = (await readdir(this.config.directory))
      .filter((name) => name.endsWith(".json"))
      .map((name) => join(this.config.directory as string, name));

    const metadata = await Promise.all(
      files.map(async (filePath) => {
        const fileStat = await stat(filePath);
        let createdAt = fileStat.mtimeMs;

        try {
          const raw = await readFile(filePath, "utf8");
          const parsed = CacheRecordSchema.parse(JSON.parse(raw));
          createdAt = parsed.createdAt;
        } catch {
          createdAt = fileStat.mtimeMs;
        }

        return {
          filePath,
          size: fileStat.size,
          createdAt,
        };
      }),
    );

    let totalBytes = metadata.reduce((sum, item) => sum + item.size, 0);
    const sorted = metadata.sort((a, b) => a.createdAt - b.createdAt);

    while (sorted.length > this.config.maxEntries || totalBytes > this.config.maxBytes) {
      const oldest = sorted.shift();
      if (!oldest) {
        break;
      }

      await rm(oldest.filePath, { force: true });
      totalBytes -= oldest.size;
    }
  }

  async clear(): Promise<void> {
    if (!this.config.enabled || !this.config.directory || !existsSync(this.config.directory)) {
      return;
    }

    const files = await readdir(this.config.directory);
    await Promise.all(
      files
        .filter((name) => name.endsWith(".json"))
        .map((name) => rm(join(this.config.directory as string, name), { force: true })),
    );
  }

  estimateRecordSize(record: CacheRecord): number {
    return toUtf8ByteLength(JSON.stringify(record));
  }
}
