import { existsSync } from "node:fs";
import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";

import type { Plugin } from "@opencode-ai/plugin";

import { DistillationCache } from "./cache.js";
import { loadPrdConfig } from "./config.js";
import {
  formatCacheClearedMessage,
  formatCommandHelp,
  formatContextView,
  formatDistillAnnotation,
  formatFallbackAnnotation,
  formatMetadataOnlyAnnotation,
  formatSessionBanner,
  formatStatsTable,
  prependPrdLine,
} from "./display.js";
import { distillFileContent } from "./distiller.js";
import { decideReadStrategy, estimateTokens } from "./policy.js";
import {
  buildSystemPromptFragment,
  formatDistilledReadOutput,
  formatMetadataOnlyOutput,
  READ_TOOL_DESCRIPTION_APPENDIX,
  SYSTEM_PROMPT_MARKER,
} from "./prompt.js";
import { parseReadToolOutput } from "./read-utils.js";
import { TelemetryStore } from "./telemetry.js";
import { createCustomTools } from "./tools.js";
import type { TaskContext } from "./types.js";

function asRecord(value: unknown): Record<string, unknown> {
  if (typeof value === "object" && value !== null) {
    return value as Record<string, unknown>;
  }
  return {};
}

function readFilePathFromArgs(args: unknown): string | undefined {
  const record = asRecord(args);
  const maybePath = record.filePath;
  if (typeof maybePath === "string" && maybePath.length > 0) {
    return maybePath;
  }
  return undefined;
}

function extractTextFromParts(parts: unknown[]): string {
  const textSegments: string[] = [];

  for (const part of parts) {
    const record = asRecord(part);
    if (record.type === "text" && typeof record.text === "string") {
      textSegments.push(record.text);
    }
  }

  return textSegments.join("\n").trim();
}

function parseCommandArguments(input: string): string[] {
  return input
    .trim()
    .split(/\s+/)
    .filter((entry) => entry.length > 0);
}

function createSyntheticTextPart(sessionID: string, text: string): {
  id: string;
  sessionID: string;
  messageID: string;
  type: "text";
  text: string;
  synthetic: boolean;
  ignored: boolean;
} {
  const stamp = `prd-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return {
    id: stamp,
    sessionID,
    messageID: stamp,
    type: "text",
    text,
    synthetic: true,
    ignored: true,
  };
}

function replaceCommandOutput(
  parts: unknown[],
  sessionID: string,
  text: string,
): void {
  parts.length = 0;
  parts.push(createSyntheticTextPart(sessionID, text));
}

async function readCacheDirectoryStats(directory: string | undefined): Promise<{ entries: number; bytes: number }> {
  if (!directory || !existsSync(directory)) {
    return { entries: 0, bytes: 0 };
  }

  const files = await readdir(directory);
  let entries = 0;
  let bytes = 0;

  for (const file of files) {
    if (!file.endsWith(".json")) {
      continue;
    }

    const absolute = join(directory, file);
    const fileStat = await stat(absolute);
    entries += 1;
    bytes += fileStat.size;
  }

  return { entries, bytes };
}

const PreReadDistillationPlugin: Plugin = async (ctx) => {
  const config = await loadPrdConfig(ctx.directory);
  const cache = new DistillationCache(config.cache);
  const telemetry = new TelemetryStore(config.telemetry);
  const taskContextBySession = new Map<string, TaskContext>();
  const seenReadCallIDsBySession = new Map<string, Set<string>>();
  const bannerInjectedCallIDsBySession = new Map<string, Set<string>>();
  const readOperationCountBySession = new Map<string, number>();

  await cache.init();
  await telemetry.init();

  const systemPromptFragment = buildSystemPromptFragment(config);

  const customTools = createCustomTools({
    config,
    cache,
    telemetry,
    getTaskContext: (sessionID: string) => taskContextBySession.get(sessionID) ?? { sessionID },
  });

  return {
    tool: customTools,

    config: async (opencodeConfig) => {
      if (!config.enabled || !config.display.slashCommands) {
        return;
      }

      opencodeConfig.command ??= {};
      opencodeConfig.command.prd = {
        template: "",
        description: "Show PRD plugin commands",
      };
    },

    "chat.message": async (input, output) => {
      if (!config.enabled || !config.hooks.chatMessageTracking) {
        return;
      }

      const userText = extractTextFromParts(output.parts);
      if (!userText) {
        return;
      }

      const previous = taskContextBySession.get(input.sessionID);
      taskContextBySession.set(input.sessionID, {
        ...previous,
        sessionID: input.sessionID,
        lastUserMessage: userText,
      });
    },

    event: async ({ event }) => {
      if (event.type !== "session.deleted") {
        return;
      }

      const properties = asRecord(event.properties);
      const info = asRecord(properties.info);
      const sessionID = typeof info.id === "string" ? info.id : undefined;
      if (!sessionID) {
        return;
      }

      taskContextBySession.delete(sessionID);
      seenReadCallIDsBySession.delete(sessionID);
      bannerInjectedCallIDsBySession.delete(sessionID);
      readOperationCountBySession.delete(sessionID);
    },

    "tool.execute.after": async (input, output) => {
      if (!config.enabled || !config.hooks.interceptReadTool) {
        return;
      }

      if (input.tool !== "read") {
        return;
      }

      const fallbackPath = readFilePathFromArgs(input.args);
      const parsed = parseReadToolOutput(output.output, fallbackPath);
      if (!parsed || parsed.fileType !== "file") {
        return;
      }

      const estimatedTokens = estimateTokens(parsed.content);
      const fileBytes = Buffer.byteLength(parsed.content, "utf8");

      const sessionTaskContext = taskContextBySession.get(input.sessionID) ?? {
        sessionID: input.sessionID,
      };

      const decision = decideReadStrategy(
        parsed.filePath,
        fileBytes,
        estimatedTokens,
        sessionTaskContext,
        config,
        parsed.content,
      );

      if (decision.mode === "pass_through") {
        return;
      }

      const priorMetadata = asRecord(output.metadata);
      const displayPath = parsed.filePath;

      if (decision.mode === "metadata_only") {
        await telemetry.recordMetadataOnly(input.sessionID, estimatedTokens);

        const metadataOnlyOutput = formatMetadataOnlyOutput({
          filePath: parsed.filePath,
          fileBytes,
          estimatedTokens,
          fileClassification: decision.fileClassification,
          reason: decision.reason,
        });

        const metadataAnnotation = config.display.operationAnnotations
          ? formatMetadataOnlyAnnotation({
              filePath: displayPath,
              worktree: ctx.worktree,
              rawTokens: estimatedTokens,
              classification: decision.fileClassification,
            })
          : null;

        output.output = metadataAnnotation
          ? prependPrdLine(metadataOnlyOutput, metadataAnnotation)
          : metadataOnlyOutput;
        output.title = "Read (metadata only)";

        output.metadata = {
          ...priorMetadata,
          prd: {
            mode: "metadata_only",
            reason: decision.reason,
            estimatedTokens,
            filePath: parsed.filePath,
            fileClassification: decision.fileClassification,
          },
        };
        return;
      }

      const fileHash = cache.hashContent(parsed.content);
      const key = cache.buildCacheKey(
        fileHash,
        config.llm.model,
        config.policy.policyVersion,
      );

      try {
        const cached = await cache.get(key);
        if (cached) {
          await telemetry.recordCacheHit(input.sessionID);
          await telemetry.recordDistillation(input.sessionID, {
            rawTokensAvoided: Math.max(estimatedTokens - (cached.result.usage?.totalTokens ?? 0), 0),
            distillTokensSpent: 0,
            escalated: cached.result.raw_read_recommended,
          });

          const distilledOutput = formatDistilledReadOutput(cached.result, "hit");
          const distilledTokens = estimateTokens(distilledOutput);
          const distillAnnotation = config.display.operationAnnotations
            ? formatDistillAnnotation({
                filePath: displayPath,
                worktree: ctx.worktree,
                rawTokens: estimatedTokens,
                distilledTokens,
                cache: "hit",
              })
            : null;

          output.output = distillAnnotation
            ? prependPrdLine(distilledOutput, distillAnnotation)
            : distilledOutput;
          output.title = "Read (distilled)";
          output.metadata = {
            ...priorMetadata,
            prd: {
              mode: "distill",
              cache: "hit",
              filePath: parsed.filePath,
              estimatedTokens,
              fileClassification: decision.fileClassification,
            },
          };
          return;
        }

        await telemetry.recordCacheMiss(input.sessionID);

        const distillStart = Date.now();
        const distilled = await distillFileContent(
          parsed.filePath,
          parsed.content,
          config,
          sessionTaskContext,
        );
        const distillLatencyMs = Date.now() - distillStart;

        await cache.set({
          key,
          model: config.llm.model,
          policyVersion: config.policy.policyVersion,
          filePath: parsed.filePath,
          fileHash,
          result: distilled,
        });

        await telemetry.recordDistillation(input.sessionID, {
          rawTokensAvoided: Math.max(estimatedTokens - (distilled.usage?.totalTokens ?? 0), 0),
          distillTokensSpent: distilled.usage?.totalTokens ?? 0,
          escalated: distilled.raw_read_recommended,
        });

        const distilledOutput = formatDistilledReadOutput(distilled, "miss");
        const distilledTokens = estimateTokens(distilledOutput);
        const distillAnnotation = config.display.operationAnnotations
          ? formatDistillAnnotation({
              filePath: displayPath,
              worktree: ctx.worktree,
              rawTokens: estimatedTokens,
              distilledTokens,
              cache: "miss",
              latencyMs: distillLatencyMs,
            })
          : null;

        output.output = distillAnnotation
          ? prependPrdLine(distilledOutput, distillAnnotation)
          : distilledOutput;
        output.title = "Read (distilled)";
        output.metadata = {
          ...priorMetadata,
          prd: {
            mode: "distill",
            cache: "miss",
            filePath: parsed.filePath,
            estimatedTokens,
            fileClassification: decision.fileClassification,
            distillTokens: distilled.usage?.totalTokens ?? null,
            latencyMs: distillLatencyMs,
          },
        };
      } catch (error) {
        await telemetry.recordFallback(input.sessionID);

        if (config.display.operationAnnotations) {
          output.output = prependPrdLine(
            output.output,
            formatFallbackAnnotation(displayPath, ctx.worktree),
          );
        }

        output.metadata = {
          ...priorMetadata,
          prd: {
            mode: "fallback",
            reason: "distillation_failed",
            filePath: parsed.filePath,
            estimatedTokens,
            fileClassification: decision.fileClassification,
          },
        };

        if (config.debug) {
          const message = error instanceof Error ? error.message : String(error);
          await ctx.client.app.log({
            body: {
              service: "opencode-pre-read-distillation",
              level: "warn",
              message: "Falling back to raw read output after distillation failure",
              extra: {
                sessionID: input.sessionID,
                callID: input.callID,
                filePath: parsed.filePath,
                error: message,
              },
            },
          });
        }
      }
    },

    "command.execute.before": async (input, output) => {
      if (!config.enabled || !config.display.slashCommands) {
        return;
      }

      if (input.command !== "prd") {
        return;
      }

      const args = parseCommandArguments(input.arguments ?? "");
      const subcommand = args[0]?.toLowerCase() ?? "";
      const nested = args[1]?.toLowerCase() ?? "";

      if (subcommand === "stats") {
        const stats = await telemetry.getSessionStats(input.sessionID);
        replaceCommandOutput(output.parts, input.sessionID, formatStatsTable(input.sessionID, stats));
        throw new Error("__PRD_STATS_HANDLED__");
      }

      if (subcommand === "context") {
        const stats = await telemetry.getSessionStats(input.sessionID);
        const cacheStats = await readCacheDirectoryStats(config.cache.directory);
        replaceCommandOutput(
          output.parts,
          input.sessionID,
          formatContextView({
            sessionID: input.sessionID,
            config,
            stats,
            cacheEntries: cacheStats.entries,
            cacheBytes: cacheStats.bytes,
          }),
        );
        throw new Error("__PRD_CONTEXT_HANDLED__");
      }

      if (subcommand === "cache" && nested === "clear") {
        await cache.clear();
        replaceCommandOutput(output.parts, input.sessionID, formatCacheClearedMessage(input.sessionID));
        throw new Error("__PRD_CACHE_CLEAR_HANDLED__");
      }

      replaceCommandOutput(output.parts, input.sessionID, formatCommandHelp());
      throw new Error("__PRD_HELP_HANDLED__");
    },

    "experimental.chat.messages.transform": async (_input, output) => {
      if (!config.enabled || !config.display.sessionSummaryBanner) {
        return;
      }

      const frequency = config.display.bannerEveryToolResults;

      for (const message of output.messages) {
        for (const part of message.parts) {
          const partRecord = asRecord(part);
          if (partRecord.type !== "tool" || partRecord.tool !== "read") {
            continue;
          }

          const sessionID = typeof partRecord.sessionID === "string" ? partRecord.sessionID : undefined;
          const callID = typeof partRecord.callID === "string" ? partRecord.callID : undefined;
          if (!sessionID || !callID) {
            continue;
          }

          const state = asRecord(partRecord.state);
          if (state.status !== "completed" || typeof state.output !== "string") {
            continue;
          }

          const stateMetadata = asRecord(state.metadata);
          const partMetadata = asRecord(partRecord.metadata);
          const statePrd = asRecord(stateMetadata.prd);
          const partPrd = asRecord(partMetadata.prd);
          const mode =
            typeof statePrd.mode === "string"
              ? statePrd.mode
              : typeof partPrd.mode === "string"
                ? partPrd.mode
                : undefined;

          if (mode !== "distill" && mode !== "metadata_only") {
            continue;
          }

          const seenCallIDs = seenReadCallIDsBySession.get(sessionID) ?? new Set<string>();
          if (!seenReadCallIDsBySession.has(sessionID)) {
            seenReadCallIDsBySession.set(sessionID, seenCallIDs);
          }

          if (!seenCallIDs.has(callID)) {
            seenCallIDs.add(callID);
            readOperationCountBySession.set(sessionID, (readOperationCountBySession.get(sessionID) ?? 0) + 1);
          }

          const operationCount = readOperationCountBySession.get(sessionID) ?? 0;
          if (operationCount < 1 || operationCount % frequency !== 0) {
            continue;
          }

          const bannerInjectedCallIDs = bannerInjectedCallIDsBySession.get(sessionID) ?? new Set<string>();
          if (!bannerInjectedCallIDsBySession.has(sessionID)) {
            bannerInjectedCallIDsBySession.set(sessionID, bannerInjectedCallIDs);
          }

          if (bannerInjectedCallIDs.has(callID)) {
            continue;
          }

          const stats = await telemetry.getSessionStats(sessionID);
          const banner = formatSessionBanner(stats, sessionID);
          if (!banner) {
            continue;
          }

          state.output = prependPrdLine(state.output, banner);
          bannerInjectedCallIDs.add(callID);
        }
      }
    },

    "tool.definition": async (input, output) => {
      if (!config.enabled || !config.hooks.toolDefinition || !config.prompt.appendReadToolDefinition) {
        return;
      }

      if (input.toolID !== "read") {
        return;
      }

      if (output.description.includes(READ_TOOL_DESCRIPTION_APPENDIX)) {
        return;
      }

      output.description = `${output.description}\n\n${READ_TOOL_DESCRIPTION_APPENDIX}`;
    },

    "experimental.chat.system.transform": async (_input, output) => {
      if (!config.enabled || !config.hooks.systemPrompt || !systemPromptFragment) {
        return;
      }

      const alreadyInjected = output.system.some((entry) => entry.includes(SYSTEM_PROMPT_MARKER));
      if (!alreadyInjected) {
        output.system.push(systemPromptFragment);
      }
    },
  };
};

export default PreReadDistillationPlugin;
