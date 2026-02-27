import type { ChildProcess } from 'node:child_process';
import path from 'node:path';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { StdioServerHarness } from './harness';
import type { JSONRPCRequest, JSONRPCResponse } from './harness';
import { loadFixture, assertAll } from '../../mcp-compliance/helpers/ts/fixtureLoader';

function parseFixtureRequest(fixtureId: string): JSONRPCRequest {
  return loadFixture(fixtureId).input.parsed as JSONRPCRequest;
}

function getExpectedAssertions(fixtureId: string) {
  const expectedOutput = loadFixture(fixtureId).expected_output;
  if (!expectedOutput) {
    throw new Error(`Fixture "${fixtureId}" has no expected_output assertions`);
  }
  return expectedOutput.assertions;
}

function assertEnvelope(response: JSONRPCResponse, expectedId: string | number): void {
  expect(response).toHaveProperty('jsonrpc', '2.0');
  expect(response).toHaveProperty('id', expectedId);

  const hasResult = response.result !== undefined;
  const hasError = response.error !== undefined;
  expect(hasResult || hasError).toBe(true);
  expect(hasResult && hasError).toBe(false);

  if (hasError) {
    const error = response.error;
    if (!error) {
      throw new Error('Expected error to be present in error envelope');
    }
    expect(error).toHaveProperty('code');
    expect(error).toHaveProperty('message');
    expect(typeof error.code).toBe('number');
    expect(typeof error.message).toBe('string');
  }
}

function requireRequestId(request: JSONRPCRequest): string | number {
  if (request.id === undefined) {
    throw new Error(`Fixture request for method "${request.method}" is missing an id`);
  }
  return request.id;
}

function requireError(response: JSONRPCResponse): NonNullable<JSONRPCResponse['error']> {
  if (!response.error) {
    throw new Error('Expected JSON-RPC error response but got success envelope');
  }
  return response.error;
}

async function sendNotificationAndCapture(
  harness: StdioServerHarness,
  notification: Omit<JSONRPCRequest, 'id'>,
  captureMs = 150
): Promise<JSONRPCResponse[]> {
  const processHandle = (harness as unknown as { process: ChildProcess | null }).process;
  if (!processHandle || !processHandle.stdin) {
    throw new Error('Server process or stdin unavailable');
  }

  const captured: JSONRPCResponse[] = [];
  const onMessage = (message: JSONRPCResponse): void => {
    captured.push(message);
  };

  harness.on('message', onMessage);

  await new Promise<void>((resolve, reject) => {
    const stdin = processHandle.stdin;
    if (!stdin) {
      reject(new Error('Server stdin is unavailable'));
      return;
    }

    stdin.write(`${JSON.stringify(notification)}\n`, (err) => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });

  await new Promise((resolve) => setTimeout(resolve, captureMs));
  harness.off('message', onMessage);

  return captured;
}

describe('ast-grep MCP lifecycle contract tests', () => {
  let harness: StdioServerHarness;

  beforeAll(async () => {
    harness = new StdioServerHarness();
    const serverPath = path.join(__dirname, '..', 'dist', 'index.js');
    await harness.start('node', [serverPath]);
  });

  afterAll(async () => {
    await harness.stop();
  });

  it('enforces initialize -> initialized notification -> tools/list -> tools/call lifecycle', async () => {
    const initializeReq = parseFixtureRequest('initialize_happy');
    const initializeRes = await harness.send(initializeReq);
    assertEnvelope(initializeRes, requireRequestId(initializeReq));
    assertAll(initializeRes, getExpectedAssertions('initialize_happy'), initializeReq);

    const initializedNotification = parseFixtureRequest('initialized_notification');
    const notificationFrames = await sendNotificationAndCapture(harness, initializedNotification);
    expect(notificationFrames.length).toBe(0);

    const toolsListReq = parseFixtureRequest('tools_list');
    const toolsListRes = await harness.send(toolsListReq);
    assertEnvelope(toolsListRes, requireRequestId(toolsListReq));
    assertAll(toolsListRes, getExpectedAssertions('tools_list'), toolsListReq);

    const toolsCallReq = parseFixtureRequest('tools_call_valid');
    const toolsCallRes = await harness.send(toolsCallReq);
    assertEnvelope(toolsCallRes, requireRequestId(toolsCallReq));
    assertAll(toolsCallRes, getExpectedAssertions('tools_call_valid'), toolsCallReq);
  });

  it('rejects invalid lifecycle sequencing when initialized notification is sent as a request', async () => {
    const localHarness = new StdioServerHarness();
    const serverPath = path.join(__dirname, '..', 'dist', 'index.js');
    await localHarness.start('node', [serverPath]);

    try {
      const invalidInitializedReq: JSONRPCRequest = {
        jsonrpc: '2.0',
        id: 91,
        method: 'notifications/initialized',
        params: {},
      };

      const preInitRes = await localHarness.send(invalidInitializedReq);
      assertEnvelope(preInitRes, 91);
      expect(preInitRes.result).toBeUndefined();
      const preInitError = requireError(preInitRes);
      expect(preInitError.code).toBe(-32601);
      expect(preInitError.message.toLowerCase()).toContain('method not found');

      const initializeReq = parseFixtureRequest('initialize_happy');
      const initializeRes = await localHarness.send(initializeReq);
      assertEnvelope(initializeRes, requireRequestId(initializeReq));

      const postInitRes = await localHarness.send({
        ...invalidInitializedReq,
        id: 92,
      });
      assertEnvelope(postInitRes, 92);
      expect(postInitRes.result).toBeUndefined();
      const postInitError = requireError(postInitRes);
      expect(postInitError.code).toBe(-32601);
      expect(postInitError.message.toLowerCase()).toContain('method not found');
    } finally {
      await localHarness.stop();
    }
  });
});
