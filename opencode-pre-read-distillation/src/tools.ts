import { stat, readFile } from "node:fs/promises";
import { extname, relative } from "node:path";

import { tool, type ToolDefinition, type ToolContext } from "@opencode-ai/plugin/tool";

import type { DistillationCache } from "./cache.js";
import { distillFileContent } from "./distiller.js";
import { decideReadStrategy, estimateTokens } from "./policy.js";
import {
  formatDistilledReadOutput,
  formatMetadataOnlyOutput,
} from "./prompt.js";
import { formatRawReadOutput, resolveAbsolutePath } from "./read-utils.js";
import type { TelemetryStore } from "./telemetry.js";
import type { PrdConfig, TaskContext } from "./types.js";

interface CustomToolDependencies {
  config: PrdConfig;
  cache: DistillationCache;
  telemetry: TelemetryStore;
  getTaskContext: (sessionID: string) => TaskContext;
}

async function readTextFile(absolutePath: string): Promise<{ content: string; bytes: number }> {
  const fileStat = await stat(absolutePath);
  if (!fileStat.isFile()) {
    throw new Error(`Expected a file path, got non-file: ${absolutePath}`);
  }

  const content = await readFile(absolutePath, "utf8");
  return {
    content,
    bytes: fileStat.size,
  };
}

function toSafeTitle(context: ToolContext, absolutePath: string): string {
  try {
    return relative(context.worktree, absolutePath) || absolutePath;
  } catch {
    return absolutePath;
  }
}

function parseOutline(content: string, extension: string, maxSymbols: number): string[] {
  const lines = content.split(/\r?\n/);
  const results: string[] = [];

  const isTsLike = [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"].includes(extension);
  const isPython = extension === ".py";
  const isGo = extension === ".go";
  const isRust = extension === ".rs";

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line) {
      continue;
    }

    let entry: string | null = null;

    if (isTsLike) {
      const functionMatch =
        line.match(/^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(/) ??
        line.match(/^\s*(?:export\s+)?const\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>/);
      const classMatch = line.match(/^\s*(?:export\s+)?class\s+([A-Za-z0-9_$]+)/);
      const interfaceMatch = line.match(/^\s*(?:export\s+)?interface\s+([A-Za-z0-9_$]+)/);
      const typeMatch = line.match(/^\s*(?:export\s+)?type\s+([A-Za-z0-9_$]+)/);

      if (functionMatch?.[1]) {
        entry = `line ${i + 1}: function ${functionMatch[1]}`;
      } else if (classMatch?.[1]) {
        entry = `line ${i + 1}: class ${classMatch[1]}`;
      } else if (interfaceMatch?.[1]) {
        entry = `line ${i + 1}: interface ${interfaceMatch[1]}`;
      } else if (typeMatch?.[1]) {
        entry = `line ${i + 1}: type ${typeMatch[1]}`;
      }
    } else if (isPython) {
      const defMatch = line.match(/^\s*def\s+([A-Za-z0-9_]+)\s*\(/);
      const classMatch = line.match(/^\s*class\s+([A-Za-z0-9_]+)/);
      if (defMatch?.[1]) {
        entry = `line ${i + 1}: def ${defMatch[1]}`;
      } else if (classMatch?.[1]) {
        entry = `line ${i + 1}: class ${classMatch[1]}`;
      }
    } else if (isGo) {
      const funcMatch = line.match(/^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z0-9_]+)\s*\(/);
      const typeMatch = line.match(/^\s*type\s+([A-Za-z0-9_]+)/);
      if (funcMatch?.[1]) {
        entry = `line ${i + 1}: func ${funcMatch[1]}`;
      } else if (typeMatch?.[1]) {
        entry = `line ${i + 1}: type ${typeMatch[1]}`;
      }
    } else if (isRust) {
      const fnMatch = line.match(/^\s*(?:pub\s+)?fn\s+([A-Za-z0-9_]+)\s*\(/);
      const structMatch = line.match(/^\s*(?:pub\s+)?struct\s+([A-Za-z0-9_]+)/);
      const enumMatch = line.match(/^\s*(?:pub\s+)?enum\s+([A-Za-z0-9_]+)/);
      if (fnMatch?.[1]) {
        entry = `line ${i + 1}: fn ${fnMatch[1]}`;
      } else if (structMatch?.[1]) {
        entry = `line ${i + 1}: struct ${structMatch[1]}`;
      } else if (enumMatch?.[1]) {
        entry = `line ${i + 1}: enum ${enumMatch[1]}`;
      }
    }

    if (entry) {
      results.push(entry);
      if (results.length >= maxSymbols) {
        break;
      }
    }
  }

  return results;
}

async function checkReadPermission(context: ToolContext, absolutePath: string, permission: string) {
  await context.ask({
    permission,
    patterns: [absolutePath],
    always: ["*"],
    metadata: { absolutePath },
  });
}

function createRawReadTool(): ToolDefinition {
  return tool({
    description: "Read exact file content without distillation.",
    args: {
      filePath: tool.schema
        .string()
        .describe("Absolute or relative path to the file to read"),
      offset: tool.schema
        .number()
        .int()
        .positive()
        .optional()
        .describe("Line number to start reading from (1-indexed)"),
      limit: tool.schema
        .number()
        .int()
        .positive()
        .optional()
        .describe("Maximum number of lines to return"),
    },
    async execute(args, context) {
      const absolutePath = resolveAbsolutePath(args.filePath, context.directory);
      await checkReadPermission(context, absolutePath, "read");

      const { content } = await readTextFile(absolutePath);
      const rendered = formatRawReadOutput(absolutePath, content, args.offset ?? 1, args.limit ?? 2_000);

      context.metadata({
        title: toSafeTitle(context, absolutePath),
        metadata: {
          mode: "raw_read",
          filePath: absolutePath,
        },
      });

      return rendered;
    },
  });
}

function createFileOutlineTool(): ToolDefinition {
  return tool({
    description:
      "Extract a lightweight symbol outline (functions/classes/types) for a source file.",
    args: {
      filePath: tool.schema
        .string()
        .describe("Absolute or relative path to the file to inspect"),
      maxSymbols: tool.schema
        .number()
        .int()
        .positive()
        .max(500)
        .optional()
        .describe("Maximum number of symbols to return (default: 150)"),
    },
    async execute(args, context) {
      const absolutePath = resolveAbsolutePath(args.filePath, context.directory);
      await checkReadPermission(context, absolutePath, "read");

      const { content } = await readTextFile(absolutePath);
      const extension = extname(absolutePath).toLowerCase();
      const maxSymbols = args.maxSymbols ?? 150;
      const outline = parseOutline(content, extension, maxSymbols);

      context.metadata({
        title: `outline:${toSafeTitle(context, absolutePath)}`,
        metadata: {
          mode: "file_outline",
          filePath: absolutePath,
          symbolCount: outline.length,
        },
      });

      return [
        "[FILE_OUTLINE_V1]",
        `file: ${absolutePath}`,
        `symbols_found: ${outline.length}`,
        "",
        outline.length > 0 ? outline.map((entry) => `- ${entry}`).join("\n") : "- (none)",
        "[/FILE_OUTLINE_V1]",
      ].join("\n");
    },
  });
}

function createDistilledReadTool(deps: CustomToolDependencies): ToolDefinition {
  return tool({
    description:
      "Read file content with policy-based pre-read distillation. Returns raw, distilled, or metadata-only output.",
    args: {
      filePath: tool.schema
        .string()
        .describe("Absolute or relative path to the file to read"),
      mode: tool.schema
        .enum(["auto", "force_distill", "force_metadata", "force_raw"])
        .optional()
        .describe("Override strategy selection for this call"),
      offset: tool.schema
        .number()
        .int()
        .positive()
        .optional()
        .describe("When returning raw content, line offset (1-indexed)"),
      limit: tool.schema
        .number()
        .int()
        .positive()
        .optional()
        .describe("When returning raw content, max lines to return"),
    },
    async execute(args, context) {
      const absolutePath = resolveAbsolutePath(args.filePath, context.directory);
      await checkReadPermission(context, absolutePath, "read");

      const { content, bytes } = await readTextFile(absolutePath);
      const estimatedTokens = estimateTokens(content);
      const baseContext = deps.getTaskContext(context.sessionID);

      const taskContext: TaskContext = {
        ...baseContext,
        forceMetadataOnly: args.mode === "force_metadata",
        forceRaw: args.mode === "force_raw",
      };

      let decision = decideReadStrategy(
        absolutePath,
        bytes,
        estimatedTokens,
        taskContext,
        deps.config,
        content,
      );

      if (args.mode === "force_distill") {
        decision = {
          ...decision,
          mode: "distill",
          reason: "Forced distill mode by tool argument.",
        };
      }

      if (decision.mode === "pass_through") {
        context.metadata({
          title: toSafeTitle(context, absolutePath),
          metadata: {
            mode: "raw",
            reason: decision.reason,
            filePath: absolutePath,
            estimatedTokens,
          },
        });
        return formatRawReadOutput(absolutePath, content, args.offset ?? 1, args.limit ?? 2_000);
      }

      if (decision.mode === "metadata_only") {
        await deps.telemetry.recordMetadataOnly(context.sessionID, estimatedTokens);
        context.metadata({
          title: `metadata:${toSafeTitle(context, absolutePath)}`,
          metadata: {
            mode: "metadata_only",
            reason: decision.reason,
            filePath: absolutePath,
            estimatedTokens,
          },
        });
        return formatMetadataOnlyOutput({
          filePath: absolutePath,
          fileBytes: bytes,
          estimatedTokens,
          fileClassification: decision.fileClassification,
          reason: decision.reason,
        });
      }

      const fileHash = deps.cache.hashContent(content);
      const key = deps.cache.buildCacheKey(
        fileHash,
        deps.config.llm.model,
        deps.config.policy.policyVersion,
      );

      const cached = await deps.cache.get(key);
      if (cached) {
        await deps.telemetry.recordCacheHit(context.sessionID);
        await deps.telemetry.recordDistillation(context.sessionID, {
          rawTokensAvoided: Math.max(estimatedTokens - (cached.result.usage?.totalTokens ?? 0), 0),
          distillTokensSpent: 0,
          escalated: cached.result.raw_read_recommended,
        });

        context.metadata({
          title: `distilled:${toSafeTitle(context, absolutePath)}`,
          metadata: {
            mode: "distill",
            cache: "hit",
            filePath: absolutePath,
            estimatedTokens,
          },
        });

        return formatDistilledReadOutput(cached.result, "hit");
      }

      await deps.telemetry.recordCacheMiss(context.sessionID);
      const result = await distillFileContent(absolutePath, content, deps.config, taskContext);

      await deps.cache.set({
        key,
        model: deps.config.llm.model,
        policyVersion: deps.config.policy.policyVersion,
        filePath: absolutePath,
        fileHash,
        result,
      });

      await deps.telemetry.recordDistillation(context.sessionID, {
        rawTokensAvoided: Math.max(estimatedTokens - (result.usage?.totalTokens ?? 0), 0),
        distillTokensSpent: result.usage?.totalTokens ?? 0,
        escalated: result.raw_read_recommended,
      });

      context.metadata({
        title: `distilled:${toSafeTitle(context, absolutePath)}`,
        metadata: {
          mode: "distill",
          cache: "miss",
          filePath: absolutePath,
          estimatedTokens,
          distillTokens: result.usage?.totalTokens ?? null,
        },
      });

      return formatDistilledReadOutput(result, "miss");
    },
  });
}

export function createCustomTools(deps: CustomToolDependencies): Record<string, ToolDefinition> {
  const tools: Record<string, ToolDefinition> = {};

  if (deps.config.customTools.distilledRead) {
    tools.distilled_read = createDistilledReadTool(deps);
  }

  if (deps.config.customTools.rawRead) {
    tools.raw_read = createRawReadTool();
  }

  if (deps.config.customTools.fileOutline) {
    tools.file_outline = createFileOutlineTool();
  }

  return tools;
}
