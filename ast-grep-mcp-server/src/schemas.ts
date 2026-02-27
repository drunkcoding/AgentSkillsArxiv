import { z } from "zod";

/**
 * Supported ast-grep languages.
 * One canonical name per language (no aliases) to keep the enum small.
 */
export const LanguageEnum = z.enum([
  "bash",
  "c",
  "cpp",
  "csharp",
  "css",
  "elixir",
  "go",
  "haskell",
  "hcl",
  "html",
  "java",
  "javascript",
  "json",
  "kotlin",
  "lua",
  "nix",
  "php",
  "python",
  "ruby",
  "rust",
  "scala",
  "solidity",
  "swift",
  "tsx",
  "typescript",
  "yml",
]);

export type Language = z.infer<typeof LanguageEnum>;

// ---------------------------------------------------------------------------
// Tool input schemas
// ---------------------------------------------------------------------------

export const SearchInputSchema = z.object({
  pattern: z
    .string()
    .describe(
      "Structural search pattern with optional meta-variables like $VAR or $$$. Example: console.log($$$)"
    ),
  language: LanguageEnum.describe("Language of the source code to search"),
  paths: z
    .array(z.string())
    .optional()
    .describe("Paths to search. Defaults to current directory if omitted"),
  globs: z
    .array(z.string())
    .optional()
    .describe(
      "Glob patterns to include/exclude files, e.g. ['*.ts', '!node_modules/**']"
    ),
});

export const RewritePreviewInputSchema = z.object({
  pattern: z.string().describe("Structural pattern to match"),
  rewrite: z
    .string()
    .describe(
      "Replacement pattern. Use meta-variables from the search pattern. Example: logger.info($A)"
    ),
  language: LanguageEnum.describe("Language of the source code"),
  paths: z
    .array(z.string())
    .optional()
    .describe("Paths to search. Defaults to current directory if omitted"),
  globs: z
    .array(z.string())
    .optional()
    .describe("Glob patterns to include/exclude files"),
});

export const RewriteApplyInputSchema = z.object({
  pattern: z.string().describe("Structural pattern to match"),
  rewrite: z
    .string()
    .describe("Replacement pattern with meta-variables from the search pattern"),
  language: LanguageEnum.describe("Language of the source code"),
  paths: z
    .array(z.string())
    .optional()
    .describe("Paths to rewrite. Defaults to current directory if omitted"),
  globs: z
    .array(z.string())
    .optional()
    .describe("Glob patterns to include/exclude files"),
});

export const ScanInputSchema = z.object({
  rule: z
    .string()
    .describe(
      "YAML rule text for ast-grep scan --inline-rules. Must include id, language, rule, and message fields"
    ),
  paths: z
    .array(z.string())
    .optional()
    .describe("Paths to scan. Defaults to current directory if omitted"),
});

export const DebugPatternInputSchema = z.object({
  pattern: z
    .string()
    .describe("Pattern whose parsed AST tree you want to inspect"),
  language: LanguageEnum.describe("Language to parse the pattern as"),
  paths: z
    .array(z.string())
    .optional()
    .describe("Paths to run against. Defaults to current directory if omitted"),
});
