import process from "node:process";
import type { Readable, Writable } from "node:stream";
import {
  JSONRPCMessageSchema,
  type JSONRPCMessage,
  type JSONRPCResponse,
  type RequestId,
} from "@modelcontextprotocol/sdk/types.js";
import type { Transport } from "@modelcontextprotocol/sdk/shared/transport.js";

const PARSE_ERROR_CODE = -32700;
const INVALID_REQUEST_CODE = -32600;

function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function extractResponseId(candidate: unknown): RequestId | undefined {
  if (!isObjectRecord(candidate)) {
    return undefined;
  }

  const id = candidate.id;
  if (typeof id === "string" || typeof id === "number" || id === null) {
    return id ?? undefined;
  }
  return undefined;
}

function buildErrorResponse(id: RequestId | undefined, code: number, message: string): JSONRPCResponse {
  const response: JSONRPCResponse = {
    jsonrpc: "2.0",
    error: { code, message },
  };

  if (id !== undefined) {
    response.id = id;
  }

  return response;
}

export class StrictStdioServerTransport implements Transport {
  private _stdin: Readable;
  private _stdout: Writable;
  private _buffer = "";
  private _started = false;

  onclose?: () => void;
  onerror?: (error: Error) => void;
  onmessage?: (message: JSONRPCMessage) => void;

  constructor(stdin: Readable = process.stdin, stdout: Writable = process.stdout) {
    this._stdin = stdin;
    this._stdout = stdout;
  }

  private _ondata = (chunk: Buffer): void => {
    this._buffer += chunk.toString("utf8");
    this.processBuffer();
  };

  private _onerror = (error: Error): void => {
    this.onerror?.(error);
  };

  async start(): Promise<void> {
    if (this._started) {
      throw new Error(
        "StrictStdioServerTransport already started! If using Server class, note that connect() calls start() automatically."
      );
    }
    this._started = true;
    this._stdin.on("data", this._ondata);
    this._stdin.on("error", this._onerror);
  }

  private processBuffer(): void {
    while (true) {
      const newlineIndex = this._buffer.indexOf("\n");
      if (newlineIndex < 0) {
        return;
      }

      const line = this._buffer.slice(0, newlineIndex).replace(/\r$/, "");
      this._buffer = this._buffer.slice(newlineIndex + 1);

      if (line.trim().length === 0) {
        continue;
      }

      this.processLine(line);
    }
  }

  private processLine(line: string): void {
    let parsed: unknown;
    try {
      parsed = JSON.parse(line);
    } catch (error) {
      this.sendParseOrInvalidError(undefined, PARSE_ERROR_CODE, "Parse error", error);
      return;
    }

    const parsedMessage = JSONRPCMessageSchema.safeParse(parsed);
    if (!parsedMessage.success) {
      const id = extractResponseId(parsed);
      this.sendParseOrInvalidError(
        id,
        INVALID_REQUEST_CODE,
        "Invalid Request",
        parsedMessage.error
      );
      return;
    }

    this.onmessage?.(parsedMessage.data);
  }

  private sendParseOrInvalidError(
    id: RequestId | undefined,
    code: number,
    message: string,
    error: unknown
  ): void {
    const response = buildErrorResponse(id, code, message);
    this.send(response).catch((sendError) => {
      const wrapped = sendError instanceof Error ? sendError : new Error(String(sendError));
      this.onerror?.(wrapped);
    });
    if (error instanceof Error) {
      this.onerror?.(error);
    } else {
      this.onerror?.(new Error(String(error)));
    }
  }

  async close(): Promise<void> {
    this._stdin.off("data", this._ondata);
    this._stdin.off("error", this._onerror);

    if (this._stdin.listenerCount("data") === 0) {
      this._stdin.pause();
    }

    this._buffer = "";
    this.onclose?.();
  }

  send(message: JSONRPCMessage): Promise<void> {
    return new Promise((resolve) => {
      const payload = `${JSON.stringify(message)}\n`;
      if (this._stdout.write(payload)) {
        resolve();
      } else {
        this._stdout.once("drain", resolve);
      }
    });
  }
}
