/**
 * Schema strictness tests for ast-grep MCP server.
 *
 * Validates the strict-reject policy from mcp-compliance/baseline-policy.json:
 *
 *   unknown_fields.policy:  "strict-reject"
 *   invalid_params.policy:  "strict-reject"
 *
 * Test layers
 * ──────────
 *   Unit (Zod): Direct schema validation — schemas carry .strict() and reject
 *               unknown/missing/wrongly-typed fields before a server is involved.
 *
 *   Integration – descriptor: tools/list response includes "additionalProperties": false
 *                             in each tool's inputSchema, reflecting the strict policy.
 *
 *   Integration – server call: Unknown or missing required tool arguments are REJECTED
 *                              by the server (strict validation fires). Because the MCP
 *                              TypeScript SDK's tools/call handler converts all internal
 *                              McpError exceptions to tool-level results (isError=true),
 *                              the server surfaces argument validation failures as
 *                              result.isError=true — not as protocol-level error.code.
 *                              This is consistent with the MCP spec's error_boundary rule
 *                              that tool handler failures stay in the result layer.
 *
 * Behavioral note on ast-grep vs fdep
 * ──────────────────────────────────
 *   fdep (custom dispatcher)  → invalid tool args → protocol error -32602
 *   ast-grep (MCP SDK)        → invalid tool args → result.isError=true
 *
 *   Both are strict-reject. Only the error-shape layer differs because the MCP
 *   TypeScript SDK's catch-all wraps all internal McpErrors as tool results.
 *   This gap is documented in issues.md (Task 13).
 */

import { describe, expect, it, beforeAll, afterAll } from 'vitest';
import path from 'node:path';
import {
  SearchInputSchema,
  RewritePreviewInputSchema,
  RewriteApplyInputSchema,
  ScanInputSchema,
  DebugPatternInputSchema,
} from '../src/schemas';
import { StdioServerHarness } from './harness';
import type { JSONRPCResponse } from './harness';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER_PATH = path.join(__dirname, '..', 'dist', 'index.js');

const INIT_PARAMS = {
  protocolVersion: '2024-11-05',
  capabilities: {},
  clientInfo: { name: 'schema-strict-test', version: '1.0.0' },
};


// ---------------------------------------------------------------------------
// Unit: Zod schema strictness (no live server)
// ---------------------------------------------------------------------------

describe('Unit – SearchInputSchema strict rejects unknown fields', () => {
  it('accepts a valid minimal input', () => {
    const result = SearchInputSchema.safeParse({
      pattern: 'console.log($$$)',
      language: 'javascript',
    });
    expect(result.success).toBe(true);
  });

  it('rejects an unknown field alongside valid fields', () => {
    const result = SearchInputSchema.safeParse({
      pattern: 'x',
      language: 'python',
      UNKNOWN_FIELD: 'value',
    });
    expect(result.success).toBe(false);
  });

  it('rejects missing required field: pattern', () => {
    const result = SearchInputSchema.safeParse({ language: 'javascript' });
    expect(result.success).toBe(false);
  });

  it('rejects missing required field: language', () => {
    const result = SearchInputSchema.safeParse({ pattern: 'x' });
    expect(result.success).toBe(false);
  });

  it('rejects an invalid enum value for language', () => {
    const result = SearchInputSchema.safeParse({
      pattern: 'x',
      language: 'cobol', // not in LanguageEnum
    });
    expect(result.success).toBe(false);
  });
});

describe('Unit – RewritePreviewInputSchema strict rejects unknown fields', () => {
  it('accepts valid input', () => {
    const result = RewritePreviewInputSchema.safeParse({
      pattern: 'console.log($MSG)',
      rewrite: 'logger.info($MSG)',
      language: 'javascript',
    });
    expect(result.success).toBe(true);
  });

  it('rejects unknown field', () => {
    const result = RewritePreviewInputSchema.safeParse({
      pattern: 'x',
      rewrite: 'y',
      language: 'typescript',
      extra: 'should-not-be-here',
    });
    expect(result.success).toBe(false);
  });

  it('rejects missing required field: rewrite', () => {
    const result = RewritePreviewInputSchema.safeParse({
      pattern: 'x',
      language: 'typescript',
    });
    expect(result.success).toBe(false);
  });
});

describe('Unit – RewriteApplyInputSchema strict rejects unknown fields', () => {
  it('accepts valid input', () => {
    const result = RewriteApplyInputSchema.safeParse({
      pattern: 'foo($A)',
      rewrite: 'bar($A)',
      language: 'rust',
    });
    expect(result.success).toBe(true);
  });

  it('rejects unknown field', () => {
    const result = RewriteApplyInputSchema.safeParse({
      pattern: 'foo($A)',
      rewrite: 'bar($A)',
      language: 'rust',
      dryRun: true, // not in schema
    });
    expect(result.success).toBe(false);
  });
});

describe('Unit – ScanInputSchema strict rejects unknown fields', () => {
  it('accepts valid input', () => {
    const result = ScanInputSchema.safeParse({
      rule: 'id: test\nlanguage: js\nrule:\n  pattern: x\nmessage: m',
    });
    expect(result.success).toBe(true);
  });

  it('rejects unknown field', () => {
    const result = ScanInputSchema.safeParse({
      rule: 'id: test',
      unknown: 'value',
    });
    expect(result.success).toBe(false);
  });
});

describe('Unit – DebugPatternInputSchema strict rejects unknown fields', () => {
  it('accepts valid input', () => {
    const result = DebugPatternInputSchema.safeParse({
      pattern: '$A + $B',
      language: 'python',
    });
    expect(result.success).toBe(true);
  });

  it('rejects unknown field', () => {
    const result = DebugPatternInputSchema.safeParse({
      pattern: 'x',
      language: 'python',
      verbose: true, // not in schema
    });
    expect(result.success).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Helpers for integration tests
// ---------------------------------------------------------------------------

/** Require a tool-level error result (isError=true, NOT a protocol error). */
function requireToolError(res: JSONRPCResponse): string {
  expect(res.jsonrpc).toBe('2.0');
  // Tool errors must NOT use the top-level `error` field.
  expect(res.error).toBeUndefined();
  expect(res.result).toBeDefined();
  const result = res.result as Record<string, unknown>;
  expect(result.isError).toBe(true);
  const content = result.content as Array<{ type: string; text: string }>;
  expect(Array.isArray(content)).toBe(true);
  const textItem = content.find((c) => c.type === 'text');
  expect(textItem).toBeDefined();
  return textItem!.text;
}

async function initializeServer(h: StdioServerHarness): Promise<void> {
  await h.send({ jsonrpc: '2.0', method: 'initialize', params: INIT_PARAMS });
}

// ---------------------------------------------------------------------------
// Integration – server: unknown tool arguments are REJECTED (strict-reject)
//
// The MCP SDK wraps McpError(InvalidParams) from validateToolInput into a
// tool-level error result (result.isError=true). The strict validation fires
// correctly — the error message confirms "Unrecognized key(s)" — but the
// error shape is tool-level per the SDK's catch-all handler design.
// ---------------------------------------------------------------------------

describe('Integration \u2013 unknown tool arguments rejected (strict-reject, tool-error shape)', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('ast_grep_search: unknown argument is rejected (isError=true, not silently stripped)', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 101,
      method: 'tools/call',
      params: {
        name: 'ast_grep_search',
        arguments: {
          pattern: 'console.log($$$)',
          language: 'javascript',
          UNKNOWN_FIELD: 'not-allowed',
        },
      },
    });
    const msg = requireToolError(res);
    expect(msg.toLowerCase()).toMatch(/unrecognized|unknown|invalid/);
    expect(res.id).toBe(101);
    expect((res.result as Record<string, unknown>).isError).toBe(true);
  });

  it('ast_grep_scan: unknown argument is rejected (isError=true)', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 102,
      method: 'tools/call',
      params: {
        name: 'ast_grep_scan',
        arguments: {
          rule: 'id: t\nlanguage: js\nrule:\n  pattern: x\nmessage: m',
          extra_key: 'forbidden',
        },
      },
    });
    const msg = requireToolError(res);
    expect(msg.toLowerCase()).toMatch(/unrecognized|unknown|invalid/);
    expect(res.id).toBe(102);
  });

  it('ast_grep_debug_pattern: unknown argument is rejected (isError=true)', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 103,
      method: 'tools/call',
      params: {
        name: 'ast_grep_debug_pattern',
        arguments: { pattern: 'x', language: 'python', verbose: true },
      },
    });
    const msg = requireToolError(res);
    expect(msg.toLowerCase()).toMatch(/unrecognized|unknown|invalid/);
    expect(res.id).toBe(103);
  });

  it('protocol framing is valid even for rejected unknown-field calls', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 999,
      method: 'tools/call',
      params: {
        name: 'ast_grep_search',
        arguments: { pattern: 'x', language: 'javascript', bogus_field: 42 },
      },
    });
    // isError=true in result, NOT a top-level protocol error
    expect(res.error).toBeUndefined();
    expect((res.result as Record<string, unknown>).isError).toBe(true);
    expect(res.id).toBe(999);
    expect(res.jsonrpc).toBe('2.0');
  });
});

// ---------------------------------------------------------------------------
// Integration – server: missing required tool arguments are REJECTED
// ---------------------------------------------------------------------------

describe('Integration \u2013 missing required tool arguments rejected (tool-error shape)', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('ast_grep_search: missing required pattern \u2192 isError=true', async () => {
    const res = await harness.send({
      jsonrpc: '2.0', id: 201, method: 'tools/call',
      params: { name: 'ast_grep_search', arguments: { language: 'javascript' } },
    });
    requireToolError(res);
    expect(res.id).toBe(201);
  });

  it('ast_grep_search: missing required language \u2192 isError=true', async () => {
    const res = await harness.send({
      jsonrpc: '2.0', id: 202, method: 'tools/call',
      params: { name: 'ast_grep_search', arguments: { pattern: 'console.log($$$)' } },
    });
    requireToolError(res);
    expect(res.id).toBe(202);
  });

  it('ast_grep_search: empty arguments object \u2192 isError=true', async () => {
    const res = await harness.send({
      jsonrpc: '2.0', id: 203, method: 'tools/call',
      params: { name: 'ast_grep_search', arguments: {} },
    });
    requireToolError(res);
    expect(res.id).toBe(203);
  });

  it('ast_grep_search: invalid enum value for language \u2192 isError=true', async () => {
    const res = await harness.send({
      jsonrpc: '2.0', id: 204, method: 'tools/call',
      params: { name: 'ast_grep_search', arguments: { pattern: 'x', language: 'cobol' } },
    });
    requireToolError(res);
    expect(res.id).toBe(204);
  });
});


// ---------------------------------------------------------------------------
// Integration: tools/list inputSchema descriptors include additionalProperties: false
// ---------------------------------------------------------------------------

describe('Integration – tools/list inputSchema reflects strict policy', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('tools/list response includes inputSchema for each tool', async () => {
    const res = await harness.send({ jsonrpc: '2.0', method: 'tools/list' });
    expect(res.error).toBeUndefined();
    const result = res.result as Record<string, unknown>;
    const tools = result.tools as Array<Record<string, unknown>>;
    expect(Array.isArray(tools)).toBe(true);
    expect(tools.length).toBeGreaterThan(0);

    for (const tool of tools) {
      expect(tool.inputSchema).toBeDefined();
    }
  });

  it('each tool inputSchema has additionalProperties: false (strict-reject policy)', async () => {
    const res = await harness.send({ jsonrpc: '2.0', method: 'tools/list' });
    const result = res.result as Record<string, unknown>;
    const tools = result.tools as Array<Record<string, unknown>>;

    for (const tool of tools) {
      const inputSchema = tool.inputSchema as Record<string, unknown>;
      expect(inputSchema.additionalProperties).toBe(false);
    }
  });

  it('ast_grep_search inputSchema lists required fields: pattern and language', async () => {
    const res = await harness.send({ jsonrpc: '2.0', method: 'tools/list' });
    const result = res.result as Record<string, unknown>;
    const tools = result.tools as Array<Record<string, unknown>>;
    const searchTool = tools.find((t) => t.name === 'ast_grep_search');
    expect(searchTool).toBeDefined();

    const schema = searchTool!.inputSchema as Record<string, unknown>;
    const required = schema.required as string[];
    expect(Array.isArray(required)).toBe(true);
    expect(required).toContain('pattern');
    expect(required).toContain('language');
    // paths and globs are optional — must NOT be in required
    expect(required).not.toContain('paths');
    expect(required).not.toContain('globs');
  });
});
