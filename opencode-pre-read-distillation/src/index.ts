import type { Plugin } from "@opencode-ai/plugin";

import { DistillationCache } from "./cache.js";
import { loadPrdConfig } from "./config.js";
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

const PreReadDistillationPlugin: Plugin = async (ctx) => {
  const config = await loadPrdConfig(ctx.directory);
  const cache = new DistillationCache(config.cache);
  const telemetry = new TelemetryStore(config.telemetry);
  const taskContextBySession = new Map<string, TaskContext>();

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

      if (decision.mode === "metadata_only") {
        await telemetry.recordMetadataOnly(input.sessionID, estimatedTokens);

        output.output = formatMetadataOnlyOutput({
          filePath: parsed.filePath,
          fileBytes,
          estimatedTokens,
          fileClassification: decision.fileClassification,
          reason: decision.reason,
        });

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

          output.output = formatDistilledReadOutput(cached.result, "hit");
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

        const distilled = await distillFileContent(
          parsed.filePath,
          parsed.content,
          config,
          sessionTaskContext,
        );

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

        output.output = formatDistilledReadOutput(distilled, "miss");
        output.metadata = {
          ...priorMetadata,
          prd: {
            mode: "distill",
            cache: "miss",
            filePath: parsed.filePath,
            estimatedTokens,
            fileClassification: decision.fileClassification,
            distillTokens: distilled.usage?.totalTokens ?? null,
          },
        };
      } catch (error) {
        await telemetry.recordFallback(input.sessionID);

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
