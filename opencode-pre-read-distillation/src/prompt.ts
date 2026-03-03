import type {
  DistilledReadResult,
  IntentClassification,
  MetadataOnlyPayload,
  PrdConfig,
} from "./types.js";

export const SYSTEM_PROMPT_MARKER = "[PRD_SYSTEM_PROMPT_V1]";

export const READ_TOOL_DESCRIPTION_APPENDIX =
  "For large files (>1.5k tokens), output may be automatically distilled. Use `raw_read` for exact content.";

export function buildSystemPromptFragment(config: PrdConfig): string {
  if (!config.prompt.injectSystemPrompt) {
    return "";
  }

  return `${SYSTEM_PROMPT_MARKER}
Pre-read distillation is enabled.
- Large read outputs may be replaced with a distilled summary before they enter context.
- If exact lines are required for edits, call the custom tool \`raw_read\`.
- If you want explicit distill-first behavior, call \`distilled_read\`.
- For very large generated/minified files, metadata-only responses may be returned first.
When precision matters, escalate to raw content immediately.`;
}

export function buildDistillerPrompt(input: {
  filePath: string;
  clippedContent: string;
  fileBytes: number;
  estimatedInputTokens: number;
  intent: IntentClassification;
}): {
  system: string;
  user: string;
} {
  const system = `You distill large code/file reads for an AI coding agent.
Return ONLY valid JSON.
Do not wrap JSON in markdown.
Required schema fields:
{
  "summary": string,
  "key_points": string[],
  "symbols": [{"name": string, "kind": string, "line"?: number, "signature"?: string, "why_important": string}],
  "sections": [{"start_line": number, "end_line": number, "label": string, "why_important": string}],
  "warnings": string[],
  "escalation_hints": string[],
  "raw_read_recommended": boolean
}
Rules:
- Be concise but complete.
- Preserve facts only; never invent symbols or lines.
- Prefer escalation_hints that tell the caller exactly when to use raw_read.`;

  const user = `Task intent: ${input.intent}
File: ${input.filePath}
Bytes: ${input.fileBytes}
Estimated input tokens: ${input.estimatedInputTokens}

Content excerpt follows:
<file_content>
${input.clippedContent}
</file_content>`;

  return { system, user };
}

export function clipContentForPrompt(content: string, maxChars: number): string {
  if (content.length <= maxChars) {
    return content;
  }

  const headLength = Math.floor(maxChars * 0.7);
  const tailLength = maxChars - headLength;
  const head = content.slice(0, headLength);
  const tail = content.slice(content.length - tailLength);

  return `${head}\n\n[... clipped ${content.length - maxChars} chars ...]\n\n${tail}`;
}

export function formatDistilledReadOutput(
  result: DistilledReadResult,
  cacheStatus: "hit" | "miss",
): string {
  const keyPoints =
    result.key_points.length > 0
      ? result.key_points.map((point) => `- ${point}`).join("\n")
      : "- (none)";

  const symbols =
    result.symbols.length > 0
      ? result.symbols
          .map((symbol) => {
            const line = symbol.line ? `line ${symbol.line}` : "line ?";
            const signature = symbol.signature ? ` | ${symbol.signature}` : "";
            return `- ${line} | ${symbol.kind} ${symbol.name}${signature} — ${symbol.why_important}`;
          })
          .join("\n")
      : "- (none)";

  const sections =
    result.sections.length > 0
      ? result.sections
          .map(
            (section) =>
              `- lines ${section.start_line}-${section.end_line} | ${section.label} — ${section.why_important}`,
          )
          .join("\n")
      : "- (none)";

  const warnings =
    result.warnings.length > 0
      ? result.warnings.map((warning) => `- ${warning}`).join("\n")
      : "- (none)";

  const escalationHints =
    result.escalation_hints.length > 0
      ? result.escalation_hints.map((hint) => `- ${hint}`).join("\n")
      : "- (none)";

  const usageLine = result.usage
    ? `usage_tokens: input=${result.usage.inputTokens}, output=${result.usage.outputTokens}, total=${result.usage.totalTokens}`
    : "usage_tokens: unavailable";

  return [
    "[PRE_READ_DISTILL_V1]",
    `file: ${result.file_path}`,
    `sha256: ${result.sha256}`,
    `file_bytes: ${result.file_bytes}`,
    `estimated_input_tokens: ${result.estimated_input_tokens}`,
    `provider_model: ${result.provider}/${result.model}`,
    `cache: ${cacheStatus}`,
    usageLine,
    "",
    "summary:",
    result.summary,
    "",
    "key_points:",
    keyPoints,
    "",
    "symbols:",
    symbols,
    "",
    "sections:",
    sections,
    "",
    "warnings:",
    warnings,
    "",
    "escalation_hints:",
    escalationHints,
    "",
    `raw_read_recommended: ${String(result.raw_read_recommended)}`,
    "Use `raw_read` for exact file content when needed.",
    "[/PRE_READ_DISTILL_V1]",
  ].join("\n");
}

export function formatMetadataOnlyOutput(payload: MetadataOnlyPayload): string {
  return [
    "[PRE_READ_METADATA_ONLY_V1]",
    `file: ${payload.filePath}`,
    `file_bytes: ${payload.fileBytes}`,
    `estimated_input_tokens: ${payload.estimatedTokens}`,
    `classification: ${payload.fileClassification}`,
    `reason: ${payload.reason}`,
    "",
    "Use `raw_read` for exact content or `distilled_read` for a targeted summary.",
    "[/PRE_READ_METADATA_ONLY_V1]",
  ].join("\n");
}
