# MCP Server Operator Guide & Troubleshooting

This guide provides operational details for the MCP servers in this repository, including how to verify compliance, interpret failures, and troubleshoot connection issues.

## Compliance Baseline

All servers in this repository are audited against the **MCP Compliance Baseline**.

- **Policy**: `mcp/mcp-compliance/baseline-policy.json`
- **Snapshots**:
  - `mcp/mcp-compliance/snapshots/ast-grep/tools-snapshot.json`
  - `mcp/mcp-compliance/snapshots/fdep/tools-snapshot.json`

### Key Compliance Breakthroughs

1.  **Strict JSON-RPC Envelope Enforcement**: Servers reject any request that does not strictly follow the JSON-RPC 2.0 specification.
2.  **Protocol/Tool Error Separation**:
    - **Protocol Error**: Top-level `error` field in JSON-RPC response. Indicates malformed request, invalid parameters, or method not found.
    - **Tool Error**: `result.isError=true` within a successful JSON-RPC `result` object. Indicates the tool ran but failed (e.g., file not found).
3.  **Stdio Framing Integrity**: Protocol messages are strictly on `stdout`. All logs, diagnostics, and errors are on `stderr`.

---

## Local Invocation & Inspection

You can manually inspect the servers using the MCP Inspector.

### ast-grep-mcp-server (Node.js)

**Build**:
```bash
cd mcp/ast-grep-mcp-server && npm run build
```

**Inspect `tools/list`**:
```bash
npx @modelcontextprotocol/inspector --cli --method tools/list node mcp/ast-grep-mcp-server/dist/index.js
```

**Troubleshooting Node.js**:
- Ensure `dist/index.js` exists. If not, run `npm run build`.
- If the inspector fails to connect, check `stderr` for Node-specific errors (e.g., missing dependencies).

### fdep-mcp-server (Python)

**Inspect `tools/list`**:
```bash
PYTHONPATH=mcp/fdep-mcp-server npx @modelcontextprotocol/inspector --cli --method tools/list /usr/bin/python3 -m fdep_mcp
```

**Troubleshooting Python**:
- Ensure the `PYTHONPATH` includes the directory containing the `fdep_mcp` package.
- If the inspector returns "Connection closed", check `stderr` for Python import errors or missing packages.

---

## Interpreting Test Failures

### 1. Protocol Violation (-32600, -32700)
If a test returns a parse error (`-32700`) or invalid request (`-32600`), the client is sending malformed JSON or an invalid JSON-RPC envelope. 

**Action**: Verify the client's output against the `stdio_contract` in `baseline-policy.json`.

### 2. Invalid Parameters (-32602)
If a test returns invalid parameters, the request includes unknown fields or missing required fields.

**Action**: Check the `strictness_matrix` in `baseline-policy.json` and the tool's `inputSchema` in the snapshots.

### 3. Framing Corruption
If the client fails to parse a message, it may be due to "leakage" where non-protocol text is printed to `stdout`.

**Action**: Ensure the server code only uses `console.error` (Node) or `sys.stderr` (Python) for logging. Protocol messages must be the only content on `stdout`.

---

## Verification Evidence

Historical compliance runs and evidence logs are stored in:
- `.sisyphus/evidence/final-matrix/`

Key evidence files:
- `ast-test.log`: Full Vitest output for ast-grep server.
- `fdep-pytest.log`: Full Pytest output for fdep server.
- `inspector-ast-tools-list.log`: Trace of successful npx inspector run for ast-grep.
- `inspector-fdep-tools-list.log`: Trace of successful npx inspector run for fdep.
- `matrix-fail-fast.log`: Evidence that the test suite stops immediately on failure to prevent stale results.
