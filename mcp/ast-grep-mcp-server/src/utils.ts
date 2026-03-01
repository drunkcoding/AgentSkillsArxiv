import { execFile } from "node:child_process";
import type { AstGrepMatch, AstGrepScanResult, CliResult } from "./types.js";

const CLI_TIMEOUT_MS = 30_000;
const OUTPUT_CHAR_LIMIT = 25_000;
const AST_GREP_BIN = "ast-grep";

// ---------------------------------------------------------------------------
// CLI execution
// ---------------------------------------------------------------------------

/** Run ast-grep with the given arguments. Uses execFile (no shell) for safety. */
export function runAstGrep(args: string[]): Promise<CliResult> {
  return new Promise((resolve) => {
    execFile(
      AST_GREP_BIN,
      args,
      { timeout: CLI_TIMEOUT_MS, maxBuffer: 10 * 1024 * 1024 },
      (error, stdout, stderr) => {
        const exitCode =
          error && "code" in error ? (error.code as number) : error ? 1 : 0;
        resolve({ stdout, stderr, exitCode });
      }
    );
  });
}

// ---------------------------------------------------------------------------
// Arg builders
// ---------------------------------------------------------------------------

/** Build --globs args from an array of glob patterns. */
export function buildGlobArgs(globs?: string[]): string[] {
  if (!globs || globs.length === 0) return [];
  return globs.flatMap((g) => ["--globs", g]);
}

// ---------------------------------------------------------------------------
// Output truncation
// ---------------------------------------------------------------------------

export function truncateOutput(text: string): string {
  if (text.length <= OUTPUT_CHAR_LIMIT) return text;
  return (
    text.slice(0, OUTPUT_CHAR_LIMIT) +
    `\n\n--- Output truncated at ${OUTPUT_CHAR_LIMIT} characters ---`
  );
}

// ---------------------------------------------------------------------------
// Error parsing
// ---------------------------------------------------------------------------

/**
 * Interpret ast-grep exit codes and stderr.
 *  - exit 0: no matches (for run) or success
 *  - exit 1: matches found (for run) — NOT an error
 *  - exit 2+: usage error / real failure
 */
export function parseCliResult(result: CliResult): {
  isError: boolean;
  errorMessage?: string;
} {
  if (result.exitCode === 0 || result.exitCode === 1) {
    return { isError: false };
  }
  return {
    isError: true,
    errorMessage: result.stderr.trim() || `ast-grep exited with code ${result.exitCode}`,
  };
}

// ---------------------------------------------------------------------------
// Formatters
// ---------------------------------------------------------------------------

export function formatSearchResults(matches: AstGrepMatch[]): string {
  if (matches.length === 0) return "No matches found.";

  const lines: string[] = [`Found ${matches.length} match(es):\n`];
  for (const m of matches) {
    const loc = `${m.file}:${m.range.start.line + 1}:${m.range.start.column + 1}`;
    lines.push(`${loc}`);
    lines.push(`  ${m.lines.trimEnd()}`);
    lines.push("");
  }
  return truncateOutput(lines.join("\n"));
}

export function formatRewritePreview(matches: AstGrepMatch[]): string {
  if (matches.length === 0) return "No matches found — nothing to rewrite.";

  const lines: string[] = [
    `Found ${matches.length} match(es) to rewrite:\n`,
  ];
  for (const m of matches) {
    const loc = `${m.file}:${m.range.start.line + 1}:${m.range.start.column + 1}`;
    lines.push(`${loc}`);
    lines.push(`  - ${m.text}`);
    lines.push(`  + ${m.replacement ?? "(no replacement)"}`);
    lines.push("");
  }
  return truncateOutput(lines.join("\n"));
}

export function formatScanResults(results: AstGrepScanResult[]): string {
  if (results.length === 0) return "No diagnostics found.";

  const lines: string[] = [`Found ${results.length} diagnostic(s):\n`];
  for (const r of results) {
    const loc = `${r.file}:${r.range.start.line + 1}:${r.range.start.column + 1}`;
    const sev = r.severity.toUpperCase();
    lines.push(`[${sev}] ${r.ruleId} at ${loc}`);
    lines.push(`  ${r.message}`);
    if (r.note) lines.push(`  Note: ${r.note}`);
    lines.push(`  Code: ${r.lines.trimEnd()}`);
    lines.push("");
  }
  return truncateOutput(lines.join("\n"));
}
