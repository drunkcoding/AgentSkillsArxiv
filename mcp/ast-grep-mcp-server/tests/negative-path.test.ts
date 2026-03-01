/**
 * Negative-path protocol / error-shape tests for ast-grep MCP server.
 *
 * Covers all five required error categories per the MCP compliance baseline:
 *
 *   1. Invalid JSON parse           → protocol error { error.code: -32700 }
 *   2. Invalid JSON-RPC envelope    → protocol error { error.code: -32600 }
 *   3. Unknown method               → protocol error  { error.code: -32601 }
 *   4. Invalid params               → protocol error  { error.code: -32603 } (SDK schema rejection)
 *   5. Tool runtime failure         → tool-level error { result.isError: true, NO error.code }
 *
 * Critical distinction enforced by these tests
 * ─────────────────────────────────────────────
 *   PROTOCOL ERROR: JSON-RPC frame uses the `error` field:
 *       { "jsonrpc": "2.0", "id": X, "error": { "code": N, "message": "..." } }
 *
 *   TOOL-LEVEL ERROR: JSON-RPC frame uses the `result` field with isError flag:
 *       { "jsonrpc": "2.0", "id": X, "result": { "content": [...], "isError": true } }
 *
 * Strict transport notes
 * ──────────────────────
 *   - This server uses a strict stdio transport wrapper that emits JSON-RPC
 *     protocol errors for malformed JSON and invalid envelopes.
 *   - MCP schema-validation failures inside a recognised method handler yield
 *     -32603 (Internal Error), not -32602 (Invalid Params), because the SDK
 *     wraps Zod errors in its internal handler.
 *   - Tool argument schema failures are surfaced as tool-level errors
 *     (result.isError=true) rather than protocol errors.
 */

import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import type { ChildProcess } from 'node:child_process';
import path from 'node:path';
import { StdioServerHarness } from './harness';
import type { JSONRPCRequest, JSONRPCResponse } from './harness';
import { loadFixture } from '../../mcp-compliance/helpers/ts/fixtureLoader';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const SERVER_PATH = path.join(__dirname, '..', 'dist', 'index.js');

/** Standard initialize params used across tests. */
const INIT_PARAMS = {
  protocolVersion: '2024-11-05',
  capabilities: {},
  clientInfo: { name: 'neg-path-test-client', version: '1.0.0' },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Expose the private process handle via type cast (test-only). */
function getStdin(h: StdioServerHarness): NodeJS.WritableStream {
  const proc = (h as unknown as { process: ChildProcess | null }).process;
  if (!proc?.stdin) throw new Error('Server process or stdin not available');
  return proc.stdin;
}

/** Write raw bytes to stdin and wait `settleMs` for any message event. */
async function sendRawAndSettle(
  h: StdioServerHarness,
  rawText: string,
  settleMs = 250
): Promise<JSONRPCResponse[]> {
  const received: JSONRPCResponse[] = [];
  const listener = (msg: JSONRPCResponse): void => { received.push(msg); };

  h.on('message', listener);
  await new Promise<void>((resolve, reject) => {
    getStdin(h).write(rawText, (err) => (err ? reject(err) : resolve()));
  });
  await new Promise((resolve) => setTimeout(resolve, settleMs));
  h.off('message', listener);

  return received;
}

/** Send initialize and get the server ready (no afterEach teardown needed for read-only ops). */
async function initializeServer(h: StdioServerHarness): Promise<JSONRPCResponse> {
  return h.send({ jsonrpc: '2.0', method: 'initialize', params: INIT_PARAMS });
}

/** Require the response to carry a JSON-RPC protocol-level error, not a tool result. */
function requireProtocolError(
  res: JSONRPCResponse
): NonNullable<JSONRPCResponse['error']> {
  expect(res.jsonrpc).toBe('2.0');
  expect(res.result).toBeUndefined();
  expect(res.error).toBeDefined();
  const err = res.error!;
  expect(typeof err.code).toBe('number');
  expect(typeof err.message).toBe('string');
  return err;
}

/** Require the response to carry a tool-level isError result, NOT a protocol error. */
function requireToolError(
  res: JSONRPCResponse
): { content: unknown; isError: boolean } {
  expect(res.jsonrpc).toBe('2.0');
  // Protocol must NOT report a top-level error for tool failures.
  expect(res.error).toBeUndefined();
  expect(res.result).toBeDefined();
  const result = res.result as Record<string, unknown>;
  expect(result.isError).toBe(true);
  expect(Array.isArray(result.content)).toBe(true);
  return { content: result.content, isError: true };
}

// ---------------------------------------------------------------------------
// Category 1 – Invalid JSON (Parse Error)
// ─────────────────────────────────────────────────────────────────────────────
// ---------------------------------------------------------------------------

describe('Category 1 – invalid JSON parse: protocol error -32700', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('returns error.code -32700 for an unparseable stdin line', async () => {
    // Fixture wire_line: "this is not valid json at all"
    const fixture = loadFixture('malformed_json');
    const rawLine = fixture.input.wire_line + '\n';
    expect(fixture.input.parsed).toBeNull(); // fixture confirms unparseable

    const received = await sendRawAndSettle(harness, rawLine);
    expect(received.length).toBe(1);

    const err = requireProtocolError(received[0]);
    expect(err.code).toBe(-32700);
    expect(received[0].id).toBeUndefined();
  });

  it('remains alive and responsive after receiving malformed JSON', async () => {
    // Send the malformed line again; then confirm server answers a valid request.
    await sendRawAndSettle(harness, 'totally:::invalid{{json\n');

    // Follow-up: server must still process normal requests correctly.
    const res = await harness.send({ jsonrpc: '2.0', method: 'tools/list' });
    expect(res.jsonrpc).toBe('2.0');
    expect(res.error).toBeUndefined();
    expect(res.result).toBeDefined();
    const result = res.result as Record<string, unknown>;
    expect(Array.isArray(result.tools)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Category 2 – Invalid JSON-RPC Envelope (Invalid Request)
// ─────────────────────────────────────────────────────────────────────────────
// ---------------------------------------------------------------------------

describe('Category 2 – invalid JSON-RPC envelope: protocol error -32600', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('returns error.code -32600 for a JSON object missing the jsonrpc field', async () => {
    // Fixture wire_line: {"method":"foo","params":{}}  (no "jsonrpc":"2.0" field)
    const fixture = loadFixture('invalid_envelope');
    const rawLine = fixture.input.wire_line + '\n';

    // Confirm fixture intent: the parsed object lacks jsonrpc field.
    const parsed = fixture.input.parsed as Record<string, unknown>;
    expect(parsed['jsonrpc']).toBeUndefined();

    const received = await sendRawAndSettle(harness, rawLine);
    expect(received.length).toBe(1);

    const err = requireProtocolError(received[0]);
    expect(err.code).toBe(-32600);
    expect(received[0].id).toBeUndefined();
  });

  it('remains alive and responsive after receiving an invalid JSON-RPC envelope', async () => {
    // Send envelope missing both "jsonrpc" and "id" fields.
    await sendRawAndSettle(harness, '{"method":"ping","params":{}}\n');

    // Follow-up valid request must still be answered.
    const res = await harness.send({ jsonrpc: '2.0', method: 'tools/list' });
    expect(res.jsonrpc).toBe('2.0');
    expect(res.error).toBeUndefined();
    expect(res.result).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// Category 3 – Unknown Method (Method Not Found)
// ─────────────────────────────────────────────────────────────────────────────
// A well-formed JSON-RPC request whose method name does not exist on the server.
// Must yield error.code -32601 with the request id preserved in the response.
// ---------------------------------------------------------------------------

describe('Category 3 – unknown method: protocol error -32601', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('returns error.code -32601 for an unknown method (from shared fixture)', async () => {
    const fixture = loadFixture('unknown_method');
    const req = fixture.input.parsed as JSONRPCRequest;

    const res = await harness.send(req);

    // Must be a PROTOCOL error, not a tool-level error.
    const err = requireProtocolError(res);
    expect(err.code).toBe(-32601);
    expect(err.message.length).toBeGreaterThan(0);

    // id must be echoed back (fixture: must_match_input_id).
    expect(res.id).toBe(req.id);

    // result must be absent — protocol errors never carry both error and result.
    expect(res.result).toBeUndefined();
  });

  it('returns error.code -32601 for a second distinct unknown method (not server-specific)', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 777,
      method: 'completely/nonexistent',
      params: {},
    });

    const err = requireProtocolError(res);
    expect(err.code).toBe(-32601);
    expect(res.id).toBe(777);
    expect(res.result).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// Category 4 – Invalid Params at Protocol Boundary
// ─────────────────────────────────────────────────────────────────────────────
// A recognised method (tools/call) whose JSON-RPC-level `params` object omits
// the required `name` field.  The MCP SDK schema-validates the call handler's
// own input and returns a PROTOCOL-LEVEL error (-32603) — NOT a tool error.
//
// Error code: -32603 (Internal Error) is what the MCP TypeScript SDK emits
// when Zod validation fails inside the call handler.  The key compliance
// invariant is that this is a protocol-level error (uses the `error` field),
// distinct from tool-level errors (uses `result.isError`).
// ---------------------------------------------------------------------------

describe('Category 4 – invalid params at protocol boundary: protocol error', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('returns a protocol-level error when tools/call params omit the required name field', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 42,
      method: 'tools/call',
      params: {
        // intentionally omitting required "name" field
        arguments: { pattern: 'foo($$$)', language: 'javascript' },
      },
    });

    // Must be a PROTOCOL error — not a tool-level isError result.
    const err = requireProtocolError(res);

    // MCP SDK returns -32603 for schema-validation failures inside method handlers.
    expect(err.code).toBe(-32603);

    // The request id must be preserved in the response envelope.
    expect(res.id).toBe(42);

    // result must be absent from an error response.
    expect(res.result).toBeUndefined();
  });

  it('protocol error has a non-empty message string (actionable text)', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 43,
      method: 'tools/call',
      params: {},
    });

    const err = requireProtocolError(res);
    expect(typeof err.message).toBe('string');
    expect(err.message.trim().length).toBeGreaterThan(0);
    expect(res.result).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// Category 5 – Tool Runtime Failure
// ─────────────────────────────────────────────────────────────────────────────
// A structurally valid tools/call request where the tool handler itself fails
// at runtime.  The protocol frame must use `result` (not `error`), and the
// result must carry `isError: true` with actionable content.
//
// Baseline policy (tool_errors):
//   "must_not_be_reported_as_protocol_error": true
//   shape: MCP tool error result (isError=true with actionable text)
//
// In CI/dev environments where the ast-grep binary is absent (ENOENT), ANY
// structurally valid tools/call will trigger this path, making it a reliable
// test target regardless of runtime tooling availability.
// ---------------------------------------------------------------------------

describe('Category 5 – tool runtime failure: result.isError (NOT protocol error)', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    await harness.start('node', [SERVER_PATH]);
    await initializeServer(harness);
  });

  afterAll(() => harness.stop());

  it('returns result.isError=true and preserves protocol frame when tool execution fails', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 55,
      method: 'tools/call',
      params: {
        name: 'ast_grep_search',
        arguments: {
          pattern: 'console.log($$$)',
          language: 'javascript',
          paths: ['/dev/null'],
        },
      },
    });

    // CRITICAL: tool failures must NOT use the JSON-RPC `error` field.
    // They must stay inside `result` with isError=true.
    requireToolError(res);

    // Protocol envelope must still be valid JSON-RPC 2.0.
    expect(res.jsonrpc).toBe('2.0');
    expect(res.id).toBe(55);

    // Top-level error field must be ABSENT (not a protocol error).
    expect(res.error).toBeUndefined();
  });

  it('tool-level error result contains a non-empty actionable message in content', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 56,
      method: 'tools/call',
      params: {
        name: 'ast_grep_search',
        arguments: {
          pattern: 'foo($VAR)',
          language: 'python',
          paths: ['/nonexistent/path/that/cannot/exist'],
        },
      },
    });

    const { content } = requireToolError(res);
    const items = content as Array<{ type: string; text: string }>;
    expect(items.length).toBeGreaterThan(0);
    const textItem = items.find((i) => i.type === 'text');
    expect(textItem).toBeDefined();
    expect(textItem!.text.trim().length).toBeGreaterThan(0);
  });

  it('protocol error (from Category 3) is structurally distinct from tool error (from Category 5)', async () => {
    // Send an unknown method to get a protocol error.
    const protocolErrRes = await harness.send({
      jsonrpc: '2.0',
      id: 57,
      method: 'nonexistent/method',
      params: {},
    });

    // Send a valid tools/call that fails at runtime to get a tool error.
    const toolErrRes = await harness.send({
      jsonrpc: '2.0',
      id: 58,
      method: 'tools/call',
      params: {
        name: 'ast_grep_search',
        arguments: {
          pattern: 'x',
          language: 'javascript',
          paths: ['/dev/null'],
        },
      },
    });

    // Protocol error uses the `error` field at the top level.
    expect(protocolErrRes.error).toBeDefined();
    expect(protocolErrRes.result).toBeUndefined();
    expect(typeof protocolErrRes.error!.code).toBe('number');

    // Tool error uses the `result` field with isError flag — no top-level error.
    expect(toolErrRes.result).toBeDefined();
    expect(toolErrRes.error).toBeUndefined();
    const toolResult = toolErrRes.result as Record<string, unknown>;
    expect(toolResult.isError).toBe(true);

    // The two shapes are mutually exclusive.
    expect(protocolErrRes.error).not.toBeUndefined();
    expect(toolErrRes.error).toBeUndefined();
  });
});
