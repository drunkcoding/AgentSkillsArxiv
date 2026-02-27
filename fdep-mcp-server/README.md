# fdep-mcp-server

Model Context Protocol (MCP) server for function dependency analysis using Tree-sitter. Trace call chains and analyze function relationships across 8 languages.

## Installation
```bash
pip install -e .
```

## Local Inspection (npx)
To verify the server's protocol compliance and list available tools, use the MCP Inspector:
```bash
PYTHONPATH=. npx @modelcontextprotocol/inspector --cli --method tools/list /usr/bin/python3 -m fdep_mcp
```

## Compliance & Operations
For detailed compliance notes, breaking changes, and troubleshooting, see:
- [Breaking Changes](../mcp-compliance/docs/BREAKING_CHANGES.md)
- [Operator Guide](../mcp-compliance/docs/OPERATOR_GUIDE.md)