import { extname } from "node:path";

import picomatch from "picomatch";

import type {
  DecisionResult,
  FileClassification,
  IntentClassification,
  PrdConfig,
  TaskContext,
} from "./types.js";

export function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

function normalizePathForGlob(filePath: string): string {
  return filePath.replaceAll("\\", "/");
}

function matchesGlobList(filePath: string, globs: string[]): boolean {
  if (globs.length === 0) {
    return false;
  }

  const normalized = normalizePathForGlob(filePath);
  return globs.some((glob) => picomatch(glob, { dot: true })(normalized));
}

export function classifyIntent(taskContext: TaskContext): IntentClassification {
  if (taskContext.intentHint) {
    return taskContext.intentHint;
  }

  const text = taskContext.lastUserMessage?.toLowerCase() ?? "";
  if (!text) {
    return "unknown";
  }

  const editPattern =
    /\b(edit|modify|change|refactor|rename|rewrite|implement|update|fix|patch|add|remove)\b/;
  if (editPattern.test(text)) {
    return "edit";
  }

  const debugPattern = /\b(error|bug|failing|failure|trace|exception|broken|regression)\b/;
  if (debugPattern.test(text)) {
    return "debug";
  }

  const analysisPattern = /\b(explain|summari[sz]e|analy[sz]e|review|understand|inspect)\b/;
  if (analysisPattern.test(text)) {
    return "analysis";
  }

  return "unknown";
}

function detectMinifiedContent(content: string, config: PrdConfig): boolean {
  const lines = content.split(/\r?\n/);
  if (lines.length === 0) {
    return false;
  }

  const longLines = lines.filter((line) => line.length >= config.policy.minifiedLineLength).length;
  const compactLength = content.replaceAll(/\s+/g, "").length;
  const density = compactLength / Math.max(content.length, 1);
  const averageLineLength = content.length / Math.max(lines.length, 1);

  if (longLines >= config.policy.minifiedLongLineCount) {
    return true;
  }

  if (
    longLines >= 1 &&
    density >= config.policy.minifiedNonWhitespaceRatio &&
    averageLineLength >= config.policy.minifiedLineLength * 0.75
  ) {
    return true;
  }

  return false;
}

export function classifyFile(
  filePath: string,
  content: string,
  config: PrdConfig,
): FileClassification {
  const extension = extname(filePath).toLowerCase();

  if (config.policy.binaryExtensions.includes(extension)) {
    return "binary";
  }

  if (config.policy.documentationExtensions.includes(extension)) {
    return "documentation";
  }

  if (matchesGlobList(filePath, config.policy.generatedPathGlobs)) {
    return "generated";
  }

  const lowerContent = content.toLowerCase();
  if (
    config.policy.generatedContentMarkers.some((marker) =>
      lowerContent.includes(marker.toLowerCase()),
    )
  ) {
    return "generated";
  }

  if (detectMinifiedContent(content, config)) {
    return "minified";
  }

  return "normal";
}

export function decideReadStrategy(
  filePath: string,
  fileSize: number,
  estTokens: number,
  taskContext: TaskContext,
  config: PrdConfig,
  content = "",
): DecisionResult {
  if (taskContext.forceRaw) {
    return {
      mode: "pass_through",
      reason: "Forced raw mode by task context.",
      fileClassification: "unknown",
      intentClassification: classifyIntent(taskContext),
    };
  }

  if (taskContext.forceMetadataOnly) {
    return {
      mode: "metadata_only",
      reason: "Forced metadata-only mode by task context.",
      fileClassification: "unknown",
      intentClassification: classifyIntent(taskContext),
    };
  }

  if (matchesGlobList(filePath, config.policy.alwaysPassThroughGlobs)) {
    return {
      mode: "pass_through",
      reason: "Path matched always-pass-through policy.",
      fileClassification: "unknown",
      intentClassification: classifyIntent(taskContext),
    };
  }

  if (matchesGlobList(filePath, config.policy.alwaysMetadataOnlyGlobs)) {
    return {
      mode: "metadata_only",
      reason: "Path matched always-metadata-only policy.",
      fileClassification: "unknown",
      intentClassification: classifyIntent(taskContext),
    };
  }

  const intent = classifyIntent(taskContext);
  const classification = classifyFile(filePath, content, config);

  if (classification === "binary") {
    return {
      mode: "metadata_only",
      reason: "Binary-like file extension detected.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  if (
    estTokens <= config.policy.passThroughMaxTokens &&
    fileSize <= config.policy.passThroughMaxBytes
  ) {
    return {
      mode: "pass_through",
      reason: "File is below pass-through thresholds.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  if (
    intent === "edit" &&
    estTokens <= config.policy.editIntentPassThroughMaxTokens &&
    classification === "normal"
  ) {
    return {
      mode: "pass_through",
      reason: "Edit intent detected and file is still reasonably sized.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  if (
    classification === "generated" &&
    estTokens >= Math.min(config.policy.metadataOnlyMinTokens, config.policy.distillMinTokens)
  ) {
    return {
      mode: "metadata_only",
      reason: "Generated file is large; metadata-only mode selected.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  if (
    classification === "minified" &&
    estTokens >= Math.min(config.policy.metadataOnlyMinTokens, config.policy.distillMinTokens)
  ) {
    return {
      mode: "metadata_only",
      reason: "Minified file detected; metadata-only mode selected.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  if (
    estTokens >= config.policy.metadataOnlyMinTokens ||
    fileSize >= config.policy.metadataOnlyMinBytes
  ) {
    return {
      mode: "metadata_only",
      reason: "File exceeds metadata-only threshold.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  if (estTokens >= config.policy.distillMinTokens || fileSize >= config.policy.distillMinBytes) {
    return {
      mode: "distill",
      reason: "File exceeds distillation threshold.",
      fileClassification: classification,
      intentClassification: intent,
    };
  }

  return {
    mode: "pass_through",
    reason: "No threshold reached; pass-through mode selected.",
    fileClassification: classification,
    intentClassification: intent,
  };
}
