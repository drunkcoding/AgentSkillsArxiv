/**
 * Smoke tests for ast-grep MCP server.
 * Tests basic server startup, tool listing, and stdio protocol compliance.
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { StdioServerHarness } from './harness';
import path from 'path';

describe('ast-grep MCP Server Smoke Tests', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    const serverPath = path.join(__dirname, '..', 'dist', 'index.js');
    await harness.start('node', [serverPath]);
  });

  afterAll(async () => {
    await harness.stop();
  });

  it('should initialize the server', async () => {
    const response = await harness.send({
      jsonrpc: '2.0',
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
          name: 'test-client',
          version: '1.0.0',
        },
      },
    });

    expect(response.jsonrpc).toBe('2.0');
    expect(response.result).toBeDefined();
    expect(response.result).toHaveProperty('protocolVersion');
    expect(response.result).toHaveProperty('capabilities');
    expect(response.result).toHaveProperty('serverInfo');
  });

  it('should list available tools', async () => {
    // Initialize first
    await harness.send({
      jsonrpc: '2.0',
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
          name: 'test-client',
          version: '1.0.0',
        },
      },
    });

    // Send initialized notification
    await harness.send({
      jsonrpc: '2.0',
      method: 'notifications/initialized',
    });

    // List tools
    const response = await harness.send({
      jsonrpc: '2.0',
      method: 'tools/list',
    });

    expect(response.jsonrpc).toBe('2.0');
    expect(response.result).toBeDefined();
    const result = response.result as any;
    expect(result).toHaveProperty('tools');
    expect(Array.isArray(result.tools)).toBe(true);
    expect(result.tools.length).toBeGreaterThan(0);

    // Verify tool structure
    result.tools.forEach((tool: any) => {
      expect(tool).toHaveProperty('name');
      expect(tool).toHaveProperty('description');
      expect(typeof tool.name).toBe('string');
      expect(typeof tool.description).toBe('string');
    });
  });
  it('should handle unknown method with error', async () => {
    const response = await harness.send({
      jsonrpc: '2.0',
      method: 'unknown/method',
      params: {},
    });

    expect(response.jsonrpc).toBe('2.0');
    expect(response.error).toBeDefined();
    expect(response.error).toHaveProperty('code');
    expect(response.error).toHaveProperty('message');
    expect(typeof response.error!.code).toBe('number');
    expect(typeof response.error!.message).toBe('string');
  });

  it('should respond with valid JSON-RPC envelope structure', async () => {
    const response = await harness.send({
      jsonrpc: '2.0',
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
          name: 'test-client',
          version: '1.0.0',
        },
      },
    });

    // Verify JSON-RPC 2.0 compliance
    expect(response).toHaveProperty('jsonrpc');
    expect(response.jsonrpc).toBe('2.0');
    expect(response).toHaveProperty('id');
    expect(response.result || response.error).toBeDefined();
    expect(!(response.result && response.error)).toBe(true); // Not both
  });
});

