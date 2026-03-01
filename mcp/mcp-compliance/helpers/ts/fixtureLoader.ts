/**
 * Shared stdio fixture loader and assertion helpers for MCP compliance testing.
 *
 * Consumed by both ast-grep-mcp-server (Vitest) and fdep-mcp-server (pytest via
 * the sibling Python helper).  All types and logic are self-contained; no runtime
 * dependency on any MCP SDK is required.
 *
 * Path anchor: this file lives at mcp-compliance/helpers/ts/fixtureLoader.ts.
 * The FIXTURES_DIR is resolved relative to __dirname at runtime.
 */

import { readFileSync } from "node:fs";
import path from "node:path";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

/** Supported assertion operators (mirrors Python counterpart). */
export type AssertionOp =
  | "eq"
  | "eq_input_id"
  | "exists"
  | "not_exists"
  | "typeof"
  | "length_gte";

export interface Assertion {
  /** Dot-separated path into the response object, e.g. "error.code". */
  path: string;
  op: AssertionOp;
  /** Expected value; interpretation depends on op. */
  value?: unknown;
}

export interface FixtureExpectedOutput {
  id_correlation: "must_match_input_id" | "may_be_null";
  assertions: Assertion[];
  error_code_reference?: Record<string, string>;
}

export interface FixtureInput {
  /** Exact JSON string to write to stdin (without trailing newline). */
  wire_line: string;
  /** Pre-parsed object for convenient inspection; null when wire_line is malformed. */
  parsed: unknown;
  id?: number | string;
  method?: string;
  notes?: string;
}

export interface StdioFixtureScenario {
  id: string;
  description: string;
  transport: "stdio";
  framing: "newline_delimited_json";
  scenario_type: "request_response" | "notification" | "request_error";
  input: FixtureInput;
  /** null for notifications (no response expected). */
  expected_output: FixtureExpectedOutput | null;
  notes?: string;
}

export interface FixtureIndexEntry {
  id: string;
  file: string;
  scenario_type: string;
  method: string | null;
  description: string;
}

export interface FixtureIndex {
  version: string;
  description: string;
  framing_rule: string;
  scenarios: FixtureIndexEntry[];
  assertion_ops: Record<string, string>;
}

export interface AssertionResult {
  passed: boolean;
  assertion: Assertion;
  actual: unknown;
  reason: string | undefined;
}

// ---------------------------------------------------------------------------
// Path resolution
// ---------------------------------------------------------------------------

const FIXTURES_DIR = path.resolve(__dirname, "../../fixtures");

// ---------------------------------------------------------------------------
// Fixture loading
// ---------------------------------------------------------------------------

/** Load a named scenario from mcp-compliance/fixtures/scenarios/<name>.json */
export function loadFixture(name: string): StdioFixtureScenario {
  const filePath = path.join(FIXTURES_DIR, "scenarios", `${name}.json`);
  const raw = readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as StdioFixtureScenario;
}

/** Load the fixture manifest (mcp-compliance/fixtures/index.json). */
export function loadFixtureIndex(): FixtureIndex {
  const filePath = path.join(FIXTURES_DIR, "index.json");
  return JSON.parse(readFileSync(filePath, "utf-8")) as FixtureIndex;
}

/** Load all scenarios listed in the index, in order. */
export function loadAllFixtures(): StdioFixtureScenario[] {
  const index = loadFixtureIndex();
  return index.scenarios.map((entry) => loadFixture(entry.id));
}

// ---------------------------------------------------------------------------
// Stdio framing utilities
// ---------------------------------------------------------------------------

/**
 * Serialize an object to a newline-terminated stdio wire line.
 * This is the correct framing unit for MCP stdio transport.
 */
export function buildStdioLine(obj: unknown): string {
  return JSON.stringify(obj) + "\n";
}

/**
 * Parse a single stdio line into a JSON value.
 * Throws SyntaxError when the line is not valid JSON.
 */
export function parseStdioLine(line: string): unknown {
  return JSON.parse(line.trim());
}

/**
 * Split a (potentially chunked) buffer received from stdout into complete
 * JSON-RPC lines.  Trailing partial lines (no terminating newline) are
 * discarded so callers always receive only complete frames.
 */
export function readChunkedLines(buffer: string): string[] {
  const parts = buffer.split("\n");
  // The last element is either an empty string (when buffer ends with \n) or a
  // partial line fragment — drop it in both cases.
  return parts.slice(0, parts.length - 1).filter((l) => l.trim().length > 0);
}

// ---------------------------------------------------------------------------
// ID correlation
// ---------------------------------------------------------------------------

/**
 * Returns true when response.id equals request.id.
 * Both arguments must be plain objects; returns false for primitives/null.
 */
export function correlateId(request: unknown, response: unknown): boolean {
  if (typeof request !== "object" || request === null) return false;
  if (typeof response !== "object" || response === null) return false;
  const reqId = (request as Record<string, unknown>)["id"];
  const resId = (response as Record<string, unknown>)["id"];
  return reqId !== undefined && reqId === resId;
}

// ---------------------------------------------------------------------------
// Assertion evaluation
// ---------------------------------------------------------------------------

/** Navigate a dot-path within obj; returns undefined if any segment is absent. */
function getAtPath(obj: unknown, dotPath: string): unknown {
  const segments = dotPath.split(".");
  let current: unknown = obj;
  for (const seg of segments) {
    if (typeof current !== "object" || current === null) return undefined;
    current = (current as Record<string, unknown>)[seg];
  }
  return current;
}

/**
 * Evaluate all assertions from a fixture's expected_output against a server
 * response.
 *
 * When any assertion uses op "eq_input_id", pass the original input.parsed as
 * inputRequest so the helper can read the expected id value.
 */
export function evaluateAssertions(
  response: unknown,
  assertions: Assertion[],
  inputRequest?: unknown
): AssertionResult[] {
  return assertions.map((assertion): AssertionResult => {
    const actual = getAtPath(response, assertion.path);

    switch (assertion.op) {
      case "eq":
        return {
          passed: actual === assertion.value,
          assertion,
          actual,
          reason:
            actual === assertion.value
              ? undefined
              : `Expected ${JSON.stringify(assertion.value)}, got ${JSON.stringify(actual)}`,
        };

      case "eq_input_id": {
        const inputId = inputRequest
          ? (inputRequest as Record<string, unknown>)["id"]
          : undefined;
        const passed = actual !== undefined && actual === inputId;
        return {
          passed,
          assertion,
          actual,
          reason: passed
            ? undefined
            : `Expected id=${JSON.stringify(inputId)}, got ${JSON.stringify(actual)}`,
        };
      }

      case "exists":
        return {
          passed: actual !== undefined,
          assertion,
          actual,
          reason:
            actual !== undefined
              ? undefined
              : `Expected path "${assertion.path}" to exist in response`,
        };

      case "not_exists":
        return {
          passed: actual === undefined,
          assertion,
          actual,
          reason:
            actual === undefined
              ? undefined
              : `Expected path "${assertion.path}" to be absent; got ${JSON.stringify(actual)}`,
        };

      case "typeof":
        if (assertion.value === "array") {
          const passed = Array.isArray(actual);
          return {
            passed,
            assertion,
            actual,
            reason: passed
              ? undefined
              : `Expected array at "${assertion.path}", got ${typeof actual}`,
          };
        }
        {
          const passed = typeof actual === assertion.value;
          return {
            passed,
            assertion,
            actual,
            reason: passed
              ? undefined
              : `Expected typeof "${assertion.value}" at "${assertion.path}", got "${typeof actual}"`,
          };
        }

      case "length_gte":
        if (Array.isArray(actual) && typeof assertion.value === "number") {
          const passed = actual.length >= assertion.value;
          return {
            passed,
            assertion,
            actual,
            reason: passed
              ? undefined
              : `Expected length >= ${assertion.value}, got ${actual.length}`,
          };
        }
        return {
          passed: false,
          assertion,
          actual,
          reason: `length_gte requires an array; got ${typeof actual}`,
        };

      default:
        return {
          passed: false,
          assertion,
          actual,
          reason: `Unknown assertion op: ${(assertion as Assertion).op}`,
        };
    }
  });
}

/**
 * Convenience: run evaluateAssertions and throw with a descriptive message
 * if any assertion fails.  Useful in test afterEach/cleanup hooks.
 */
export function assertAll(
  response: unknown,
  assertions: Assertion[],
  inputRequest?: unknown
): void {
  const results = evaluateAssertions(response, assertions, inputRequest);
  const failures = results.filter((r) => !r.passed);
  if (failures.length > 0) {
    const lines = failures.map(
      (f) =>
        `  [${f.assertion.op}] ${f.assertion.path}: ${f.reason}`
    );
    throw new Error(`${failures.length} assertion(s) failed:\n${lines.join("\n")}`);
  }
}
