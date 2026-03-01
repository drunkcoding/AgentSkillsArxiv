/**
 * Smoke tests: shared stdio fixture consumption (TypeScript side).
 *
 * Verifies that:
 *   1. All fixture scenario files in mcp-compliance/fixtures/ can be loaded.
 *   2. Each scenario conforms to the StdioFixtureScenario shape.
 *   3. The stdio framing helpers (buildStdioLine, parseStdioLine,
 *      readChunkedLines) round-trip correctly.
 *   4. The ID correlation helper works for matched and mismatched ids.
 *   5. The assertion evaluator correctly judges eq, exists, not_exists,
 *      typeof, length_gte, and eq_input_id operators.
 *
 * These tests do NOT start a live server — they prove shared-fixture
 * readability and helper correctness only.
 */

import { describe, it, expect } from "vitest";
import path from "path";
import {
  loadFixture,
  loadFixtureIndex,
  loadAllFixtures,
  buildStdioLine,
  parseStdioLine,
  readChunkedLines,
  correlateId,
  evaluateAssertions,
  assertAll,
  type StdioFixtureScenario,
} from "../../mcp-compliance/helpers/ts/fixtureLoader";

// ---------------------------------------------------------------------------
// Index loading
// ---------------------------------------------------------------------------

describe("Fixture index", () => {
  it("loads index.json and reports the expected scenario count", () => {
    const index = loadFixtureIndex();
    expect(index.version).toBe("1.0.0");
    expect(Array.isArray(index.scenarios)).toBe(true);
    expect(index.scenarios.length).toBe(7);
  });

  it("index entries each have id, file, and scenario_type", () => {
    const index = loadFixtureIndex();
    for (const entry of index.scenarios) {
      expect(typeof entry.id).toBe("string");
      expect(typeof entry.file).toBe("string");
      expect(typeof entry.scenario_type).toBe("string");
    }
  });
});

// ---------------------------------------------------------------------------
// Individual fixture loading
// ---------------------------------------------------------------------------

describe("Individual fixture loading", () => {
  const EXPECTED_IDS = [
    "initialize_happy",
    "initialized_notification",
    "tools_list",
    "tools_call_valid",
    "malformed_json",
    "invalid_envelope",
    "unknown_method",
  ];

  for (const fixtureId of EXPECTED_IDS) {
    it(`loads fixture "${fixtureId}" without error`, () => {
      const scenario = loadFixture(fixtureId);
      expect(scenario.id).toBe(fixtureId);
      expect(scenario.transport).toBe("stdio");
      expect(scenario.framing).toBe("newline_delimited_json");
      expect(typeof scenario.description).toBe("string");
      expect(scenario.description.length).toBeGreaterThan(0);
    });
  }

  it("loadAllFixtures returns all 7 scenarios in index order", () => {
    const all = loadAllFixtures();
    expect(all.length).toBe(7);
    const ids = all.map((s) => s.id);
    expect(ids).toContain("initialize_happy");
    expect(ids).toContain("initialized_notification");
    expect(ids).toContain("tools_list");
    expect(ids).toContain("tools_call_valid");
    expect(ids).toContain("malformed_json");
    expect(ids).toContain("invalid_envelope");
    expect(ids).toContain("unknown_method");
  });
});

// ---------------------------------------------------------------------------
// Scenario structure — request_response fixtures
// ---------------------------------------------------------------------------

describe("request_response fixture structure", () => {
  it("initialize_happy has correct input and non-null expected_output", () => {
    const f = loadFixture("initialize_happy");
    expect(f.scenario_type).toBe("request_response");
    expect(typeof f.input.wire_line).toBe("string");
    expect(f.input.wire_line.length).toBeGreaterThan(0);
    expect(f.input.parsed).not.toBeNull();
    expect((f.input.parsed as Record<string, unknown>)["method"]).toBe("initialize");
    expect(f.expected_output).not.toBeNull();
    expect(Array.isArray(f.expected_output!.assertions)).toBe(true);
    expect(f.expected_output!.assertions.length).toBeGreaterThan(0);
  });

  it("tools_list expected_output includes a length_gte assertion on result.tools", () => {
    const f = loadFixture("tools_list");
    const lgtAssert = f.expected_output!.assertions.find(
      (a) => a.op === "length_gte" && a.path === "result.tools"
    );
    expect(lgtAssert).toBeDefined();
    expect(typeof (lgtAssert!.value)).toBe("number");
  });

  it("unknown_method expected_output requires error.code -32601", () => {
    const f = loadFixture("unknown_method");
    const codeAssert = f.expected_output!.assertions.find(
      (a) => a.op === "eq" && a.path === "error.code"
    );
    expect(codeAssert).toBeDefined();
    expect(codeAssert!.value).toBe(-32601);
  });
});

// ---------------------------------------------------------------------------
// Scenario structure — notification fixture
// ---------------------------------------------------------------------------

describe("notification fixture structure", () => {
  it("initialized_notification has null expected_output", () => {
    const f = loadFixture("initialized_notification");
    expect(f.scenario_type).toBe("notification");
    expect(f.expected_output).toBeNull();
    // Notification wire_line must not contain an 'id' field
    const parsed = JSON.parse(f.input.wire_line) as Record<string, unknown>;
    expect(parsed["id"]).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// Scenario structure — error fixtures
// ---------------------------------------------------------------------------

describe("error fixture structure", () => {
  it("malformed_json has null parsed and error.code -32700", () => {
    const f = loadFixture("malformed_json");
    expect(f.scenario_type).toBe("request_error");
    expect(f.input.parsed).toBeNull();
    const codeAssert = f.expected_output!.assertions.find(
      (a) => a.op === "eq" && a.path === "error.code"
    );
    expect(codeAssert!.value).toBe(-32700);
  });

  it("invalid_envelope has error.code -32600", () => {
    const f = loadFixture("invalid_envelope");
    const codeAssert = f.expected_output!.assertions.find(
      (a) => a.op === "eq" && a.path === "error.code"
    );
    expect(codeAssert!.value).toBe(-32600);
  });

  it("error fixtures have id_correlation of may_be_null for parse/invalid errors", () => {
    const malformed = loadFixture("malformed_json");
    const invalid = loadFixture("invalid_envelope");
    expect(malformed.expected_output!.id_correlation).toBe("may_be_null");
    expect(invalid.expected_output!.id_correlation).toBe("may_be_null");
  });

  it("unknown_method has id_correlation of must_match_input_id", () => {
    const f = loadFixture("unknown_method");
    expect(f.expected_output!.id_correlation).toBe("must_match_input_id");
  });
});

// ---------------------------------------------------------------------------
// Stdio framing utilities
// ---------------------------------------------------------------------------

describe("buildStdioLine / parseStdioLine", () => {
  it("round-trips a simple JSON-RPC request", () => {
    const obj = { jsonrpc: "2.0", id: 1, method: "initialize", params: {} };
    const line = buildStdioLine(obj);
    expect(line.endsWith("\n")).toBe(true);
    const parsed = parseStdioLine(line) as typeof obj;
    expect(parsed.jsonrpc).toBe("2.0");
    expect(parsed.id).toBe(1);
    expect(parsed.method).toBe("initialize");
  });

  it("parseStdioLine trims surrounding whitespace before parsing", () => {
    const obj = { jsonrpc: "2.0", id: 2, method: "test" };
    const padded = "  " + JSON.stringify(obj) + "  \n";
    const parsed = parseStdioLine(padded) as typeof obj;
    expect(parsed.id).toBe(2);
  });

  it("parseStdioLine throws SyntaxError for non-JSON input", () => {
    expect(() => parseStdioLine("not json")).toThrow(SyntaxError);
  });

  it("wire_line from initialize_happy fixture round-trips through parseStdioLine", () => {
    const f = loadFixture("initialize_happy");
    const parsed = parseStdioLine(f.input.wire_line) as Record<string, unknown>;
    expect(parsed["jsonrpc"]).toBe("2.0");
    expect(parsed["method"]).toBe("initialize");
  });
});

describe("readChunkedLines", () => {
  it("splits a clean multi-line buffer into individual lines", () => {
    const buf =
      '{"jsonrpc":"2.0","id":1,"result":{}}\n{"jsonrpc":"2.0","id":2,"result":{}}\n';
    const lines = readChunkedLines(buf);
    expect(lines.length).toBe(2);
    expect(lines[0]).toContain('"id":1');
    expect(lines[1]).toContain('"id":2');
  });

  it("discards a trailing partial line (no terminating newline)", () => {
    const buf = '{"jsonrpc":"2.0","id":1,"result":{}}\n{"partial":true';
    const lines = readChunkedLines(buf);
    expect(lines.length).toBe(1);
    expect(lines[0]).toContain('"id":1');
  });

  it("handles a single-line buffer correctly", () => {
    const buf = '{"jsonrpc":"2.0","id":3,"result":{}}\n';
    const lines = readChunkedLines(buf);
    expect(lines.length).toBe(1);
  });

  it("returns empty array for an empty buffer", () => {
    expect(readChunkedLines("")).toEqual([]);
    expect(readChunkedLines("\n")).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// ID correlation helper
// ---------------------------------------------------------------------------

describe("correlateId", () => {
  it("returns true when request.id === response.id", () => {
    expect(
      correlateId({ jsonrpc: "2.0", id: 1 }, { jsonrpc: "2.0", id: 1 })
    ).toBe(true);
  });

  it("returns false when ids differ", () => {
    expect(
      correlateId({ jsonrpc: "2.0", id: 1 }, { jsonrpc: "2.0", id: 2 })
    ).toBe(false);
  });

  it("returns false when request has no id", () => {
    expect(
      correlateId({ jsonrpc: "2.0" }, { jsonrpc: "2.0", id: 1 })
    ).toBe(false);
  });

  it("returns false for non-object arguments", () => {
    expect(correlateId(null, { id: 1 })).toBe(false);
    expect(correlateId({ id: 1 }, null)).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Assertion evaluation
// ---------------------------------------------------------------------------

describe("evaluateAssertions", () => {
  const successResponse = {
    jsonrpc: "2.0",
    id: 42,
    result: {
      protocolVersion: "2024-11-05",
      serverInfo: { name: "test-server", version: "1.0.0" },
      capabilities: { tools: {} },
      tools: ["a", "b", "c"],
    },
  };

  it("op=eq passes for matching value", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "jsonrpc", op: "eq", value: "2.0" },
    ]);
    expect(results[0].passed).toBe(true);
  });

  it("op=eq fails for mismatched value", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "jsonrpc", op: "eq", value: "1.0" },
    ]);
    expect(results[0].passed).toBe(false);
    expect(results[0].reason).toBeTruthy();
  });

  it("op=eq_input_id passes when id matches", () => {
    const results = evaluateAssertions(
      successResponse,
      [{ path: "id", op: "eq_input_id" }],
      { jsonrpc: "2.0", id: 42 }
    );
    expect(results[0].passed).toBe(true);
  });

  it("op=eq_input_id fails when id mismatches", () => {
    const results = evaluateAssertions(
      successResponse,
      [{ path: "id", op: "eq_input_id" }],
      { jsonrpc: "2.0", id: 99 }
    );
    expect(results[0].passed).toBe(false);
  });

  it("op=exists passes when path is present", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "result.serverInfo", op: "exists" },
    ]);
    expect(results[0].passed).toBe(true);
  });

  it("op=exists fails when path is absent", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "result.missing_key", op: "exists" },
    ]);
    expect(results[0].passed).toBe(false);
  });

  it("op=not_exists passes when path is absent", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "error", op: "not_exists" },
    ]);
    expect(results[0].passed).toBe(true);
  });

  it("op=not_exists fails when path is present", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "result", op: "not_exists" },
    ]);
    expect(results[0].passed).toBe(false);
  });

  it("op=typeof array passes for actual arrays", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "result.tools", op: "typeof", value: "array" },
    ]);
    expect(results[0].passed).toBe(true);
  });

  it("op=typeof string passes for actual strings", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "jsonrpc", op: "typeof", value: "string" },
    ]);
    expect(results[0].passed).toBe(true);
  });

  it("op=length_gte passes when array is long enough", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "result.tools", op: "length_gte", value: 3 },
    ]);
    expect(results[0].passed).toBe(true);
  });

  it("op=length_gte fails when array is too short", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "result.tools", op: "length_gte", value: 10 },
    ]);
    expect(results[0].passed).toBe(false);
  });

  it("multiple assertions are all evaluated independently", () => {
    const results = evaluateAssertions(successResponse, [
      { path: "jsonrpc", op: "eq", value: "2.0" },
      { path: "error", op: "not_exists" },
      { path: "result.serverInfo.name", op: "exists" },
      { path: "result.tools", op: "length_gte", value: 1 },
    ]);
    expect(results.length).toBe(4);
    expect(results.every((r) => r.passed)).toBe(true);
  });
});

describe("assertAll", () => {
  it("does not throw when all assertions pass", () => {
    expect(() =>
      assertAll(
        { jsonrpc: "2.0", id: 1, result: { protocolVersion: "2024-11-05" } },
        [
          { path: "jsonrpc", op: "eq", value: "2.0" },
          { path: "result.protocolVersion", op: "exists" },
        ]
      )
    ).not.toThrow();
  });

  it("throws with failure details when assertions fail", () => {
    expect(() =>
      assertAll({ jsonrpc: "1.0" }, [
        { path: "jsonrpc", op: "eq", value: "2.0" },
      ])
    ).toThrow("1 assertion(s) failed");
  });
});

// ---------------------------------------------------------------------------
// End-to-end: run fixture assertions against a synthetic response
// ---------------------------------------------------------------------------

describe("end-to-end: initialize_happy assertions against synthetic response", () => {
  it("all assertions pass against a well-formed initialize response", () => {
    const fixture = loadFixture("initialize_happy");
    const syntheticResponse = {
      jsonrpc: "2.0",
      id: (fixture.input.parsed as Record<string, unknown>)["id"],
      result: {
        protocolVersion: "2024-11-05",
        serverInfo: { name: "ast-grep", version: "1.0.0" },
        capabilities: { tools: {} },
      },
    };
    expect(() =>
      assertAll(
        syntheticResponse,
        fixture.expected_output!.assertions,
        fixture.input.parsed
      )
    ).not.toThrow();
  });

  it("assertions fail when response is missing result fields", () => {
    const fixture = loadFixture("initialize_happy");
    const incompleteResponse = { jsonrpc: "2.0", id: 1 };
    const results = evaluateAssertions(
      incompleteResponse,
      fixture.expected_output!.assertions,
      fixture.input.parsed
    );
    const failed = results.filter((r) => !r.passed);
    // At least result.protocolVersion, result.serverInfo, result.capabilities are missing
    expect(failed.length).toBeGreaterThanOrEqual(3);
  });
});
