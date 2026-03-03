#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StrictStdioServerTransport } from "./strictStdioTransport.js";
import type { AstGrepMatch, AstGrepScanResult } from "./types.js";
import {
  SearchInputSchema,
  RewritePreviewInputSchema,
  RewriteApplyInputSchema,
  ScanInputSchema,
  DebugPatternInputSchema,
} from "./schemas.js";
import {
  runAstGrep,
  buildGlobArgs,
  truncateOutput,
  parseCliResult,
  formatSearchResults,
  formatRewritePreview,
  formatScanResults,
} from "./utils.js";

// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "ast-grep",
  version: "1.0.0",
});

// ---------------------------------------------------------------------------
// 1. ast_grep_search
// ---------------------------------------------------------------------------

server.registerTool(
  "ast_grep_search",
  {
    description:
      "Search code using structural AST patterns with meta-variables ($VAR, $$$). Returns matching locations and code.",
    inputSchema: SearchInputSchema,
  },
  async ({ pattern, language, paths, globs }) => {
    const args = [
      "run",
      "-p",
      pattern,
      "-l",
      language,
      "--json=compact",
      ...buildGlobArgs(globs),
      ...(paths ?? ["."]),
    ];
    const result = await runAstGrep(args);
    const check = parseCliResult(result);
    if (check.isError) {
      return { content: [{ type: "text", text: check.errorMessage! }], isError: true };
    }
    const matches: AstGrepMatch[] = result.stdout.trim()
      ? JSON.parse(result.stdout)
      : [];
    return { content: [{ type: "text", text: formatSearchResults(matches) }] };
  }
);

// ---------------------------------------------------------------------------
// 2. ast_grep_rewrite_preview
// ---------------------------------------------------------------------------

server.registerTool(
  "ast_grep_rewrite_preview",
  {
    description:
      "Preview structural rewrites without applying them. Shows before/after for each match.",
    inputSchema: RewritePreviewInputSchema,
  },
  async ({ pattern, rewrite, language, paths, globs }) => {
    const args = [
      "run",
      "-p",
      pattern,
      "-r",
      rewrite,
      "-l",
      language,
      "--json=compact",
      ...buildGlobArgs(globs),
      ...(paths ?? ["."]),
    ];
    const result = await runAstGrep(args);
    const check = parseCliResult(result);
    if (check.isError) {
      return { content: [{ type: "text", text: check.errorMessage! }], isError: true };
    }
    const matches: AstGrepMatch[] = result.stdout.trim()
      ? JSON.parse(result.stdout)
      : [];
    return { content: [{ type: "text", text: formatRewritePreview(matches) }] };
  }
);

// ---------------------------------------------------------------------------
// 3. ast_grep_rewrite_apply
// ---------------------------------------------------------------------------

server.registerTool(
  "ast_grep_rewrite_apply",
  {
    description:
      "Apply structural rewrites to files on disk. Modifies files in place. Preview first with ast_grep_rewrite_preview.",
    inputSchema: RewriteApplyInputSchema,
  },
  async ({ pattern, rewrite, language, paths, globs }) => {
    // Phase 1: preview to count matches
    const previewArgs = [
      "run",
      "-p",
      pattern,
      "-r",
      rewrite,
      "-l",
      language,
      "--json=compact",
      ...buildGlobArgs(globs),
      ...(paths ?? ["."]),
    ];
    const preview = await runAstGrep(previewArgs);
    const previewCheck = parseCliResult(preview);
    if (previewCheck.isError) {
      return {
        content: [{ type: "text", text: previewCheck.errorMessage! }],
        isError: true,
      };
    }
    const matches: AstGrepMatch[] = preview.stdout.trim()
      ? JSON.parse(preview.stdout)
      : [];
    if (matches.length === 0) {
      return {
        content: [{ type: "text", text: "No matches found — nothing to rewrite." }],
      };
    }

    // Phase 2: apply
    const applyArgs = [
      "run",
      "-p",
      pattern,
      "-r",
      rewrite,
      "-l",
      language,
      "--update-all",
      ...buildGlobArgs(globs),
      ...(paths ?? ["."]),
    ];
    const apply = await runAstGrep(applyArgs);
    const applyCheck = parseCliResult(apply);
    if (applyCheck.isError) {
      return {
        content: [{ type: "text", text: applyCheck.errorMessage! }],
        isError: true,
      };
    }

    // Summarize affected files
    const files = [...new Set(matches.map((m) => m.file))];
    const summary = [
      `Applied ${matches.length} rewrite(s) across ${files.length} file(s):`,
      ...files.map((f) => `  ${f}`),
    ].join("\n");
    return { content: [{ type: "text", text: summary }] };
  }
);

// ---------------------------------------------------------------------------
// 4. ast_grep_scan
// ---------------------------------------------------------------------------

server.registerTool(
  "ast_grep_scan",
  {
    description:
      "Run custom YAML lint rules against code. Returns diagnostics with severity, message, and location.",
    inputSchema: ScanInputSchema,
  },
  async ({ rule, paths }) => {
    const args = [
      "scan",
      "--inline-rules",
      rule,
      "--json=compact",
      ...(paths ?? ["."]),
    ];
    const result = await runAstGrep(args);
    const check = parseCliResult(result);
    if (check.isError) {
      return { content: [{ type: "text", text: check.errorMessage! }], isError: true };
    }
    const diagnostics: AstGrepScanResult[] = result.stdout.trim()
      ? JSON.parse(result.stdout)
      : [];
    return { content: [{ type: "text", text: formatScanResults(diagnostics) }] };
  }
);

// ---------------------------------------------------------------------------
// 5. ast_grep_debug_pattern
// ---------------------------------------------------------------------------

server.registerTool(
  "ast_grep_debug_pattern",
  {
    description:
      "Show the parsed AST of a pattern. Useful for debugging why a pattern does or does not match.",
    inputSchema: DebugPatternInputSchema,
  },
  async ({ pattern, language, paths }) => {
    const args = [
      "run",
      "--debug-query=pattern",
      "-p",
      pattern,
      "-l",
      language,
      ...(paths ?? ["."]),
    ];
    const result = await runAstGrep(args);
    const check = parseCliResult(result);
    if (check.isError) {
      return { content: [{ type: "text", text: check.errorMessage! }], isError: true };
    }
    // debug-query output goes to stdout as plain text
    const output = (result.stdout + "\n" + result.stderr).trim();
    return { content: [{ type: "text", text: truncateOutput(output) }] };
  }
);

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StrictStdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
