import { isAbsolute, resolve } from "node:path";

import type { ParsedReadToolOutput } from "./types.js";

export function resolveAbsolutePath(filePath: string, directory: string): string {
  if (isAbsolute(filePath)) {
    return filePath;
  }
  return resolve(directory, filePath);
}

export function lineNumberContent(content: string, offset = 1, limit = 2_000): {
  numbered: string[];
  totalLines: number;
  hasMore: boolean;
  startLine: number;
  endLine: number;
  nextOffset: number;
} {
  const lines = content.split(/\r?\n/);
  const totalLines = lines.length;

  const startIndex = Math.max(offset - 1, 0);
  const sliced = lines.slice(startIndex, startIndex + limit);
  const numbered = sliced.map((line, index) => `${startIndex + index + 1}: ${line}`);

  const hasMore = startIndex + sliced.length < totalLines;
  const startLine = sliced.length > 0 ? startIndex + 1 : offset;
  const endLine = sliced.length > 0 ? startIndex + sliced.length : offset;
  const nextOffset = endLine + 1;

  return {
    numbered,
    totalLines,
    hasMore,
    startLine,
    endLine,
    nextOffset,
  };
}

export function formatRawReadOutput(
  absolutePath: string,
  content: string,
  offset = 1,
  limit = 2_000,
): string {
  const numbered = lineNumberContent(content, offset, limit);

  const footer = numbered.hasMore
    ? `(Showing lines ${numbered.startLine}-${numbered.endLine} of ${numbered.totalLines}. Use offset=${numbered.nextOffset} to continue.)`
    : `(End of file - total ${numbered.totalLines} lines)`;

  return [
    `<path>${absolutePath}</path>`,
    "<type>file</type>",
    "<content>",
    numbered.numbered.join("\n"),
    "",
    footer,
    "</content>",
  ].join("\n");
}

function detectFileType(output: string): ParsedReadToolOutput["fileType"] {
  const typeMatch = output.match(/<type>([^<]+)<\/type>/i);
  if (!typeMatch || !typeMatch[1]) {
    return "unknown";
  }

  const raw = typeMatch[1].trim().toLowerCase();
  if (raw === "file") {
    return "file";
  }
  if (raw === "directory") {
    return "directory";
  }
  return "unknown";
}

function stripLineNumbers(content: string): string {
  return content
    .split(/\r?\n/)
    .map((line) => line.replace(/^\d+:\s?/, ""))
    .join("\n");
}

export function parseReadToolOutput(output: string, fallbackPath?: string): ParsedReadToolOutput | null {
  const pathMatch = output.match(/<path>([\s\S]*?)<\/path>/i);
  const filePath = pathMatch?.[1]?.trim() || fallbackPath;
  if (!filePath) {
    return null;
  }

  const fileType = detectFileType(output);
  if (fileType !== "file") {
    return {
      filePath,
      fileType,
      content: "",
      lineCount: 0,
      charCount: 0,
    };
  }

  const contentMatch = output.match(/<content>([\s\S]*?)<\/content>/i);
  if (!contentMatch || contentMatch[1] === undefined) {
    return {
      filePath,
      fileType,
      content: "",
      lineCount: 0,
      charCount: 0,
    };
  }

  const rawContent = contentMatch[1].trim();
  const cleanedContent = stripLineNumbers(rawContent);
  const lineCount = cleanedContent.length === 0 ? 0 : cleanedContent.split(/\r?\n/).length;

  return {
    filePath,
    fileType,
    content: cleanedContent,
    lineCount,
    charCount: cleanedContent.length,
  };
}
