# MCP Servers: Intentional Breaking Changes

**Date**: 2026-02-27  
**Scope**: mcp/ast-grep-mcp-server (Task 11), mcp/fdep-mcp-server (Task 12)  
**Reason**: Protocol compliance hardening to enforce strict JSON-RPC and MCP contract semantics

---

## Overview

Tasks 11 and 12 introduced intentional breaking changes to both MCP servers to enforce strict protocol compliance. These changes ensure deterministic error handling, proper stdio framing, and clear separation between protocol-level and tool-level errors.

---

## ast-grep-mcp-server Breaking Changes

### 1. Strict Stdio Transport (Task 11)

**What Changed**:
- Replaced MCP SDK's default `StdioServerTransport` with a custom `StrictStdioServerTransport`
- The strict transport enforces protocol-level error responses for malformed JSON and invalid JSON-RPC envelopes

**Why**:
- The SDK's default transport silently discards malformed input without emitting error responses
- Strict compliance requires deterministic error responses for parse errors and invalid requests
- This ensures clients can reliably detect protocol violations

**Impact**:
- **Clients sending malformed JSON**: Previously received no response; now receive JSON-RPC error response with code `-32700` (Parse error)
- **Clients sending invalid JSON-RPC envelopes**: Previously received no response; now receive JSON-RPC error response with code `-32600` (Invalid Request)
- **Valid requests**: No change in behavior

**Migration Path**:
- Clients should expect error responses for malformed input
- Clients should validate JSON before sending to the server
- Clients should handle JSON-RPC error responses with codes `-32700` and `-32600`

**Snapshot Reference**:
- See `mcp/mcp-compliance/snapshots/ast-grep/tools-snapshot.json` for protocol response shapes

---

### 2. Protocol/Tool Error Boundary Enforcement

**What Changed**:
- Protocol errors (malformed JSON, invalid envelopes, unknown methods, invalid params) are now strictly separated from tool-level errors
- Protocol errors return top-level `error` field in JSON-RPC response
- Tool-level errors return `result.isError=true` with no top-level `error` field

**Why**:
- Clear error boundary prevents clients from confusing protocol failures with tool execution failures
- Enables clients to implement different recovery strategies for each error type
- Aligns with MCP specification semantics

**Impact**:
- **Clients parsing error responses**: Must check for top-level `error` field for protocol errors
- **Clients parsing tool results**: Must check `result.isError` for tool-level failures
- **Error handling logic**: Clients must distinguish between the two error types

**Migration Path**:
- Update error handling to check both `error` (protocol) and `result.isError` (tool) fields
- Implement separate recovery strategies for protocol vs. tool errors
- See baseline policy in `mcp/mcp-compliance/baseline-policy.json` for detailed error semantics

---

## fdep-mcp-server Breaking Changes

### 1. Custom JSON-RPC Dispatcher (Task 12)

**What Changed**:
- Replaced FastMCP framework's automatic request handling with a custom `FdepMcpServer` class
- The custom dispatcher enforces strict JSON-RPC envelope validation and deterministic error responses

**Why**:
- FastMCP's automatic handling does not enforce strict protocol compliance
- Custom dispatcher enables deterministic error codes and messages
- Ensures consistent behavior across all error paths

**Impact**:
- **Malformed JSON**: Now returns JSON-RPC error with code `-32700` (Parse error)
- **Invalid JSON-RPC envelopes**: Now returns JSON-RPC error with code `-32600` (Invalid Request)
- **Unknown methods**: Now returns JSON-RPC error with code `-32601` (Method not found)
- **Invalid params**: Now returns JSON-RPC error with code `-32602` (Invalid params)
- **Valid requests**: No change in behavior

**Migration Path**:
- Clients should expect deterministic error responses for all error conditions
- Clients should validate requests before sending
- Clients should handle all JSON-RPC error codes: `-32700`, `-32600`, `-32601`, `-32602`

**Snapshot Reference**:
- See `mcp/mcp-compliance/snapshots/fdep/tools-snapshot.json` for protocol response shapes

---

### 2. Strict Unknown Field Rejection

**What Changed**:
- Top-level request fields and method-specific params fields are now strictly validated
- Unknown/extra fields in requests are rejected with error code `-32602` (Invalid params)

**Why**:
- Prevents silent acceptance of misspelled or unsupported fields
- Enables forward compatibility: new fields can be added without breaking old clients
- Aligns with strict JSON-RPC semantics

**Impact**:
- **Requests with extra fields**: Previously accepted; now rejected with error
- **Requests with correct fields**: No change in behavior

**Migration Path**:
- Remove any extra fields from requests
- Validate request structure against the baseline policy
- See `mcp/mcp-compliance/baseline-policy.json` for allowed fields per method

---

### 3. Deterministic Error Serialization

**What Changed**:
- All JSON-RPC responses use deterministic serialization with sorted keys and compact separators
- Error messages are consistent and actionable

**Why**:
- Enables reliable snapshot testing and regression detection
- Ensures consistent behavior across repeated calls
- Simplifies client-side error message parsing

**Impact**:
- **Error message format**: Slightly different formatting (compact JSON)
- **Error message content**: More consistent and actionable
- **Snapshot testing**: Errors are now deterministically comparable

**Migration Path**:
- Update error message parsing if relying on specific formatting
- Use snapshot testing to detect unintended changes
- See `mcp/mcp-compliance/snapshots/fdep/tools-snapshot.json` for error response shapes

---

## Shared Breaking Changes (Both Servers)

### 1. Stdout/Stderr Framing Enforcement

**What Changed**:
- Protocol messages are now strictly confined to stdout (newline-delimited JSON-RPC)
- All diagnostic/logging output is strictly confined to stderr
- No debug prints, progress text, or stack traces on stdout

**Why**:
- Prevents protocol stream corruption
- Enables reliable message framing and parsing
- Aligns with stdio transport specification

**Impact**:
- **Clients reading stdout**: Will only see valid JSON-RPC messages
- **Clients reading stderr**: May see diagnostic output (implementation-dependent)
- **Protocol parsing**: More reliable and deterministic

**Migration Path**:
- Clients should validate that stdout contains only JSON-RPC messages
- Clients should ignore stderr output (or log it separately)
- See `mcp/mcp-compliance/baseline-policy.json` for stdio contract details

---

### 2. Notification Handling

**What Changed**:
- Valid notifications (requests without `id` field) are processed without emitting a response
- Invalid notifications (with `id` field) are treated as requests and receive error responses

**Why**:
- Aligns with JSON-RPC 2.0 specification
- Enables one-way communication for non-critical updates
- Prevents unnecessary response overhead

**Impact**:
- **Clients sending notifications**: Will not receive responses (expected behavior)
- **Clients sending invalid notifications**: Will receive error responses
- **Protocol efficiency**: Reduced overhead for one-way messages

**Migration Path**:
- Ensure notifications do not include `id` field
- Do not expect responses for notifications
- See baseline policy for notification semantics

---

## Compliance Baseline Reference

All breaking changes are documented in the compliance baseline:

- **File**: `mcp/mcp-compliance/baseline-policy.json`
- **Sections**:
  - `error_boundary`: Protocol vs. tool error semantics
  - `stdio_contract`: Stdout/stderr framing rules
  - `strictness_matrix`: Detailed policy for each error category

---

## Snapshot Artifacts

Tool descriptor and protocol response snapshots are available:

- **ast-grep**: `mcp/mcp-compliance/snapshots/ast-grep/tools-snapshot.json`
- **fdep**: `mcp/mcp-compliance/snapshots/fdep/tools-snapshot.json`

These snapshots capture:
- Tool names and descriptions
- Protocol response envelope shapes
- Error response codes and messages

---

## Verification

To verify compliance with these breaking changes:

1. **ast-grep-mcp-server**:
   ```bash
   cd mcp/ast-grep-mcp-server
   npm run test
   ```

2. **fdep-mcp-server**:
   ```bash
   cd mcp/fdep-mcp-server
   pytest -q
   ```

Both test suites include:
- Lifecycle contract tests (initialize → tools/list → tools/call)
- Negative-path tests (malformed JSON, invalid envelopes, unknown methods, invalid params)
- Framing integrity tests (stdout/stderr separation)

---

## Questions & Support

For questions about these breaking changes:

1. Review the baseline policy: `mcp/mcp-compliance/baseline-policy.json`
2. Check the test suites for expected behavior
3. Review the snapshot artifacts for protocol response shapes
4. Consult the MCP specification: https://modelcontextprotocol.io/specification/draft
