# ast-grep-mcp-server

Model Context Protocol (MCP) server for ast-grep. Provide structural code search, rewriting, and linting capabilities to LLMs.

## Installation & Build
```bash
npm install && npm run build
```

## Local Inspection (npx)
To verify the server's protocol compliance and list available tools, use the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector --cli --method tools/list node dist/index.js
```

## Compliance & Operations
For detailed compliance notes, breaking changes, and troubleshooting, see:
- [Breaking Changes](../mcp-compliance/docs/BREAKING_CHANGES.md)
- [Operator Guide](../mcp-compliance/docs/OPERATOR_GUIDE.md)