import { createHash } from "node:crypto";

import { z } from "zod";

import { loadPrdConfig } from "./config.js";
import { estimateTokens } from "./policy.js";
import { buildDistillerPrompt, clipContentForPrompt } from "./prompt.js";
import {
  DistilledReadModelPayloadSchema,
  DistilledReadResultSchema,
  type DistilledReadResult,
  type DistillerUsage,
  type PrdConfig,
  type TaskContext,
} from "./types.js";

const OpenAiResponseSchema = z.object({
  choices: z.array(
    z.object({
      message: z.object({
        content: z.string().nullable().optional(),
      }),
    }),
  ),
  usage: z
    .object({
      prompt_tokens: z.number().int().nonnegative().optional(),
      completion_tokens: z.number().int().nonnegative().optional(),
      total_tokens: z.number().int().nonnegative().optional(),
    })
    .optional(),
});

const AnthropicResponseSchema = z.object({
  content: z.array(
    z.object({
      type: z.string(),
      text: z.string().optional(),
    }),
  ),
  usage: z
    .object({
      input_tokens: z.number().int().nonnegative().optional(),
      output_tokens: z.number().int().nonnegative().optional(),
    })
    .optional(),
});

export interface DistillerDependencies {
  fetchImpl?: typeof fetch;
}

function sha256Hex(input: string): string {
  return createHash("sha256").update(input).digest("hex");
}

function normalizeBaseUrl(provider: PrdConfig["llm"]["provider"], baseURL?: string): string {
  if (baseURL) {
    return baseURL.replace(/\/$/, "");
  }

  if (provider === "anthropic") {
    return "https://api.anthropic.com";
  }

  return "https://api.openai.com/v1";
}

function extractJsonString(raw: string): string {
  const fencedMatch = raw.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fencedMatch?.[1]) {
    return fencedMatch[1].trim();
  }

  const firstBrace = raw.indexOf("{");
  const lastBrace = raw.lastIndexOf("}");
  if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
    return raw.slice(firstBrace, lastBrace + 1).trim();
  }

  return raw.trim();
}

async function fetchWithTimeout(
  fetchImpl: typeof fetch,
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetchImpl(url, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
}

async function callOpenAiCompatibleModel(
  config: PrdConfig,
  apiKey: string,
  prompt: { system: string; user: string },
  fetchImpl: typeof fetch,
): Promise<{ text: string; usage?: DistillerUsage }> {
  const baseUrl = normalizeBaseUrl(config.llm.provider, config.llm.baseURL);
  const endpoint = `${baseUrl}/chat/completions`;

  const response = await fetchWithTimeout(
    fetchImpl,
    endpoint,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: config.llm.model,
        temperature: config.llm.temperature,
        max_tokens: config.llm.maxOutputTokens,
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: prompt.system },
          { role: "user", content: prompt.user },
        ],
      }),
    },
    config.llm.timeoutMs,
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`OpenAI-compatible request failed (${response.status}): ${errorBody}`);
  }

  const parsedResponse = OpenAiResponseSchema.parse(await response.json());
  const messageText = parsedResponse.choices[0]?.message.content;
  if (!messageText) {
    throw new Error("OpenAI-compatible response did not include message content.");
  }

  const usage = parsedResponse.usage
    ? {
        inputTokens: parsedResponse.usage.prompt_tokens ?? 0,
        outputTokens: parsedResponse.usage.completion_tokens ?? 0,
        totalTokens:
          parsedResponse.usage.total_tokens ??
          (parsedResponse.usage.prompt_tokens ?? 0) + (parsedResponse.usage.completion_tokens ?? 0),
      }
    : undefined;

  if (usage) {
    return {
      text: messageText,
      usage,
    };
  }

  return {
    text: messageText,
  };
}

async function callAnthropicModel(
  config: PrdConfig,
  apiKey: string,
  prompt: { system: string; user: string },
  fetchImpl: typeof fetch,
): Promise<{ text: string; usage?: DistillerUsage }> {
  const baseUrl = normalizeBaseUrl(config.llm.provider, config.llm.baseURL);
  const endpoint = `${baseUrl}/v1/messages`;

  const response = await fetchWithTimeout(
    fetchImpl,
    endpoint,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: config.llm.model,
        temperature: config.llm.temperature,
        max_tokens: config.llm.maxOutputTokens,
        system: prompt.system,
        messages: [{ role: "user", content: prompt.user }],
      }),
    },
    config.llm.timeoutMs,
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Anthropic request failed (${response.status}): ${errorBody}`);
  }

  const parsedResponse = AnthropicResponseSchema.parse(await response.json());
  const textBlocks = parsedResponse.content
    .filter((block) => block.type === "text" && typeof block.text === "string")
    .map((block) => block.text ?? "");
  const messageText = textBlocks.join("\n").trim();

  if (!messageText) {
    throw new Error("Anthropic response did not include text content.");
  }

  const usage = parsedResponse.usage
    ? {
        inputTokens: parsedResponse.usage.input_tokens ?? 0,
        outputTokens: parsedResponse.usage.output_tokens ?? 0,
        totalTokens:
          (parsedResponse.usage.input_tokens ?? 0) + (parsedResponse.usage.output_tokens ?? 0),
      }
    : undefined;

  if (usage) {
    return {
      text: messageText,
      usage,
    };
  }

  return {
    text: messageText,
  };
}

function parseDistillerPayload(rawText: string) {
  const jsonText = extractJsonString(rawText);
  const rawObject = JSON.parse(jsonText) as unknown;
  return DistilledReadModelPayloadSchema.parse(rawObject);
}

export async function distillFileContent(
  filePath: string,
  content: string,
  config: PrdConfig,
  taskContext: TaskContext,
  dependencies: DistillerDependencies = {},
): Promise<DistilledReadResult> {
  const fetchImpl = dependencies.fetchImpl ?? fetch;
  const apiKey = process.env[config.llm.apiKeyEnv];
  if (!apiKey) {
    throw new Error(`Missing API key in environment variable ${config.llm.apiKeyEnv}`);
  }

  const estimatedInputTokens = estimateTokens(content);
  const clipped = clipContentForPrompt(content, config.policy.maxDistillInputChars);

  const intent = taskContext.intentHint ?? "unknown";
  const prompt = buildDistillerPrompt({
    filePath,
    clippedContent: clipped,
    fileBytes: Buffer.byteLength(content, "utf8"),
    estimatedInputTokens,
    intent,
  });

  const providerCallResult =
    config.llm.provider === "anthropic"
      ? await callAnthropicModel(config, apiKey, prompt, fetchImpl)
      : await callOpenAiCompatibleModel(config, apiKey, prompt, fetchImpl);

  const payload = parseDistillerPayload(providerCallResult.text);

  const result = DistilledReadResultSchema.parse({
    schema_version: "prd.distilled_read.v1",
    file_path: filePath,
    sha256: sha256Hex(content),
    file_bytes: Buffer.byteLength(content, "utf8"),
    estimated_input_tokens: estimatedInputTokens,
    summary: payload.summary,
    key_points: payload.key_points,
    symbols: payload.symbols,
    sections: payload.sections,
    warnings: payload.warnings,
    escalation_hints: payload.escalation_hints,
    raw_read_recommended: payload.raw_read_recommended,
    provider: config.llm.provider,
    model: config.llm.model,
    usage: providerCallResult.usage,
  });

  return result;
}

export async function distillFileWithConfigLoad(
  directory: string,
  filePath: string,
  content: string,
  taskContext: TaskContext,
  dependencies: DistillerDependencies = {},
): Promise<DistilledReadResult> {
  const config = await loadPrdConfig(directory);
  return distillFileContent(filePath, content, config, taskContext, dependencies);
}
