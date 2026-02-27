/**
 * Framing integrity tests for ast-grep MCP server.
 *
 * Verifies:
 *   1. Stdout contains exclusively parseable JSON-RPC frames during protocol exchange.
 *   2. Non-JSON stdout contamination is detectable using readChunkedLines + JSON.parse.
 *   3. Multi-message framing correctly correlates request and response ids.
 *   4. Newline-delimited framing is robust against partial frames and edge cases.
 *   5. Stderr output does not contaminate stdout (parseError count stays zero).
 *
 * Sections:
 *   A. Live server – stdout purity (positive tests against the real server process)
 *   B. Contamination detection – unit tests (negative path, synthetic buffers)
 *   C. Newline-delimited framing robustness – unit tests
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { StdioServerHarness } from './harness';
import { readChunkedLines } from '../../mcp-compliance/helpers/ts/fixtureLoader';
import path from 'path';

const SERVER_PATH = path.join(__dirname, '..', 'dist', 'index.js');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function tryParseJson(line: string): boolean {
  try {
    JSON.parse(line);
    return true;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// A. Live server – stdout purity
// ---------------------------------------------------------------------------

describe('A. stdout purity: zero parseError events during protocol exchange (live server)', () => {
  let harness: StdioServerHarness;
  const parseErrors: Array<{ line: string; error: unknown }> = [];

  beforeAll(async () => {
    harness = new StdioServerHarness();
    // Collect any non-JSON lines the harness encounters on stdout
    harness.on('parseError', (data: { line: string; error: unknown }) =>
      parseErrors.push(data),
    );
    await harness.start('node', [SERVER_PATH]);
  });

  afterAll(async () => {
    await harness.stop();
  });

  it('initialize exchange produces zero stdout parseError events', async () => {
    const before = parseErrors.length;
    await harness.send({
      jsonrpc: '2.0',
      id: 1001,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: { name: 'framing-integrity-test', version: '0.0.0' },
      },
    });
    expect(parseErrors.length).toBe(before);
  });

  it('tools/list exchange produces zero stdout parseError events', async () => {
    // Ensure initialized before tools/list
    await harness.send({
      jsonrpc: '2.0',
      id: 1010,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: { name: 'framing-integrity-test', version: '0.0.0' },
      },
    });
    const before = parseErrors.length;
    await harness.send({ jsonrpc: '2.0', id: 1002, method: 'tools/list' });
    expect(parseErrors.length).toBe(before);
  });

  it('each response envelope carries exactly result XOR error (not both, not neither)', async () => {
    const res = await harness.send({
      jsonrpc: '2.0',
      id: 1003,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: { name: 'framing-integrity-test', version: '0.0.0' },
      },
    });
    const hasResult = res.result !== undefined;
    const hasError = res.error !== undefined;
    expect(hasResult || hasError).toBe(true);   // at least one
    expect(hasResult && hasError).toBe(false);  // not both
  });

  it('response id matches request id across three consecutive exchanges (framing correlation)', async () => {
    const sentIds = [2001, 2002, 2003];
    for (const id of sentIds) {
      const res = await harness.send({
        jsonrpc: '2.0',
        id,
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: { name: 'framing-integrity-test', version: '0.0.0' },
        },
      });
      // Each response must echo the exact request id — no cross-frame id corruption
      expect(res.id).toBe(id);
    }
  });

  it('stdout parseError count remains zero after all protocol exchanges above', () => {
    // Cumulative assertion: all exchanges so far produced only valid JSON on stdout
    expect(parseErrors).toHaveLength(0);
  });

  it('stderr events do not cause stdout parseError (stdout/stderr channels remain separate)', async () => {
    const stderrLines: string[] = [];
    const stdErrListener = (data: string): void => {
      stderrLines.push(data);
    };
    harness.on('stderr', stdErrListener);

    const before = parseErrors.length;
    // Trigger a tools/list which may emit diagnostics on stderr in some servers
    await harness.send({ jsonrpc: '2.0', id: 3001, method: 'tools/list' });

    harness.off('stderr', stdErrListener);

    // Regardless of how much stderr output occurred, stdout must remain clean
    expect(parseErrors.length).toBe(before);
  });
});

// ---------------------------------------------------------------------------
// B. Contamination detection – unit tests (no live server needed)
// ---------------------------------------------------------------------------

describe('B. stdout contamination detection (unit — synthetic buffers)', () => {
  it('single non-JSON line in a multi-frame buffer is detectable', () => {
    const contaminated =
      '{"jsonrpc":"2.0","id":1,"result":{}}\n' +
      'WARNING: leaked debug output\n' +
      '{"jsonrpc":"2.0","id":2,"result":{}}\n';

    const lines = readChunkedLines(contaminated);
    expect(lines.length).toBe(3);

    const failures = lines.filter((l) => !tryParseJson(l));
    expect(failures.length).toBe(1);
    expect(failures[0]).toContain('WARNING');
  });

  it('clean stdout buffer produces zero parse failures (all frames are valid JSON)', () => {
    const clean =
      '{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05"}}\n' +
      '{"jsonrpc":"2.0","id":2,"result":{"tools":[]}}\n';

    const lines = readChunkedLines(clean);
    expect(lines.length).toBe(2);

    const failures = lines.filter((l) => !tryParseJson(l));
    expect(failures).toHaveLength(0);
  });

  it('buffer containing only non-JSON text: every line fails JSON.parse (all contaminated)', () => {
    const allBad = 'Server starting...\nInitializing tools...\n';
    const lines = readChunkedLines(allBad);

    expect(lines.length).toBeGreaterThan(0);
    const failures = lines.filter((l) => !tryParseJson(l));
    expect(failures.length).toBe(lines.length); // 100 % contamination rate
  });

  it('single contamination among 10 valid frames: exactly one detection', () => {
    const frames = Array.from(
      { length: 10 },
      (_, i) => `{"jsonrpc":"2.0","id":${i},"result":{}}\n`,
    );
    // Splice a non-JSON debug line at index 5
    frames.splice(5, 0, 'DEBUG: connection established\n');

    const buffer = frames.join('');
    const lines = readChunkedLines(buffer);

    const failures = lines.filter((l) => !tryParseJson(l));
    expect(failures.length).toBe(1);
    expect(failures[0]).toContain('DEBUG');
  });

  it('error response envelope is valid JSON (error path also produces parseable frames)', () => {
    const errorFrame =
      '{"jsonrpc":"2.0","id":42,"error":{"code":-32601,"message":"Method not found"}}\n';
    const lines = readChunkedLines(errorFrame);
    expect(lines.length).toBe(1);
    expect(() => JSON.parse(lines[0])).not.toThrow();
  });

  it('stderr content simulated as if leaked to stdout is detectable as contamination', () => {
    // Models the scenario where a server incorrectly writes log output to stdout.
    const stderrLeak = '[INFO] Server started\n';
    const protocolFrame = '{"jsonrpc":"2.0","id":1,"result":{}}\n';
    const mixedBuffer = protocolFrame + stderrLeak;

    const lines = readChunkedLines(mixedBuffer);
    const failures = lines.filter((l) => !tryParseJson(l));

    expect(failures.length).toBe(1);
    expect(failures[0]).toContain('[INFO]');
  });
});

// ---------------------------------------------------------------------------
// C. Newline-delimited framing robustness – unit tests
// ---------------------------------------------------------------------------

describe('C. newline-delimited framing robustness (unit)', () => {
  it('two complete frames in a single chunk produce exactly two lines in order', () => {
    const chunk = '{"jsonrpc":"2.0","id":10}\n{"jsonrpc":"2.0","id":11}\n';
    const lines = readChunkedLines(chunk);
    expect(lines.length).toBe(2);

    const parsed = lines.map((l) => JSON.parse(l) as { id: number });
    expect(parsed[0].id).toBe(10);
    expect(parsed[1].id).toBe(11);
  });

  it('partial trailing frame (no terminating newline) is discarded', () => {
    const partial = '{"jsonrpc":"2.0","id":20}\n{"incomplete":true';
    const lines = readChunkedLines(partial);
    expect(lines.length).toBe(1);
    expect((JSON.parse(lines[0]) as { id: number }).id).toBe(20);
  });

  it('three complete frames in a chunk produce three lines in order', () => {
    const chunk =
      '{"jsonrpc":"2.0","id":30}\n' +
      '{"jsonrpc":"2.0","id":31}\n' +
      '{"jsonrpc":"2.0","id":32}\n';

    const lines = readChunkedLines(chunk);
    expect(lines.length).toBe(3);

    const ids = lines.map((l) => (JSON.parse(l) as { id: number }).id);
    expect(ids).toEqual([30, 31, 32]);
  });

  it('empty string buffer yields no frames', () => {
    expect(readChunkedLines('')).toHaveLength(0);
  });

  it('buffer containing only a newline yields no frames (no phantom empty frame)', () => {
    expect(readChunkedLines('\n')).toHaveLength(0);
  });

  it('consecutive newlines between frames produce no spurious empty frames', () => {
    const buf = '{"jsonrpc":"2.0","id":40}\n\n{"jsonrpc":"2.0","id":41}\n';
    const lines = readChunkedLines(buf);
    expect(lines.length).toBe(2);
    expect(lines.every((l) => l.trim().length > 0)).toBe(true);
  });

  it('compact JSON frame (no spaces) parses correctly', () => {
    const compact =
      '{"jsonrpc":"2.0","id":50,"result":{"nested":{"a":1,"b":true}}}\n';
    const lines = readChunkedLines(compact);
    expect(lines.length).toBe(1);

    const parsed = JSON.parse(lines[0]) as Record<string, unknown>;
    expect(parsed['jsonrpc']).toBe('2.0');
    expect(parsed['id']).toBe(50);
  });

  it('frame containing only a newline terminator (after valid JSON) is included', () => {
    // Edge case: a valid JSON object followed immediately by its terminator newline
    const frame = '{"jsonrpc":"2.0","id":60}\n';
    const lines = readChunkedLines(frame);
    expect(lines.length).toBe(1);
    expect(tryParseJson(lines[0])).toBe(true);
  });

  it('a single frame without any newline is treated as incomplete and discarded', () => {
    // Simulates a partial write where the newline delimiter has not arrived yet
    const noTerminator = '{"jsonrpc":"2.0","id":70}';
    const lines = readChunkedLines(noTerminator);
    expect(lines).toHaveLength(0);
  });

  it('large batch of 20 frames all parse correctly and preserve insertion order', () => {
    const n = 20;
    const buffer = Array.from(
      { length: n },
      (_, i) => `{"jsonrpc":"2.0","id":${1000 + i}}\n`,
    ).join('');

    const lines = readChunkedLines(buffer);
    expect(lines.length).toBe(n);

    const ids = lines.map((l) => (JSON.parse(l) as { id: number }).id);
    const expected = Array.from({ length: n }, (_, i) => 1000 + i);
    expect(ids).toEqual(expected);
  });
});
