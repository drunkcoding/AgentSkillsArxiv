/**
 * Test harness for stdio-based MCP server testing.
 * Provides utilities for spawning the server and communicating via JSON-RPC.
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

export interface JSONRPCRequest {
  jsonrpc: '2.0';
  id?: string | number;
  method: string;
  params?: unknown;
}

export interface JSONRPCResponse {
  jsonrpc: '2.0';
  id?: string | number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export class StdioServerHarness extends EventEmitter {
  private process: ChildProcess | null = null;
  private messageBuffer: string = '';
  private pendingRequests: Map<string | number, (response: JSONRPCResponse) => void> = new Map();
  private nextId: number = 1;

  async start(command: string, args: string[] = []): Promise<void> {
    return new Promise((resolve, reject) => {
      this.process = spawn(command, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      if (!this.process.stdout || !this.process.stderr) {
        reject(new Error('Failed to create stdio pipes'));
        return;
      }

      this.process.stdout.on('data', (data: Buffer) => {
        this.handleStdoutData(data);
      });

      this.process.stderr.on('data', (data: Buffer) => {
        this.emit('stderr', data.toString());
      });

      this.process.on('error', (err) => {
        reject(err);
      });

      this.process.on('exit', (code) => {
        this.emit('exit', code);
      });

      // Give the process a moment to start
      setTimeout(resolve, 100);
    });
  }

  private handleStdoutData(data: Buffer): void {
    this.messageBuffer += data.toString();
    this.processMessages();
  }

  private processMessages(): void {
    const lines = this.messageBuffer.split('\n');
    this.messageBuffer = lines[lines.length - 1];

    for (let i = 0; i < lines.length - 1; i++) {
      const line = lines[i].trim();
      if (line) {
        try {
          const message = JSON.parse(line) as JSONRPCResponse;
          this.emit('message', message);

          if (message.id !== undefined && this.pendingRequests.has(message.id)) {
            const callback = this.pendingRequests.get(message.id)!;
            this.pendingRequests.delete(message.id);
            callback(message);
          }
        } catch (err) {
          this.emit('parseError', { line, error: err });
        }
      }
    }
  }

  async send(request: JSONRPCRequest): Promise<JSONRPCResponse> {
    if (!this.process || !this.process.stdin) {
      throw new Error('Server not started');
    }

    const id = request.id ?? this.nextId++;
    const fullRequest = { ...request, id };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, resolve);

      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout for id ${id}`));
      }, 5000);

      this.once('message', () => {
        clearTimeout(timeout);
      });

      this.process!.stdin!.write(JSON.stringify(fullRequest) + '\n', (err) => {
        if (err) {
          this.pendingRequests.delete(id);
          reject(err);
        }
      });
    });
  }

  async stop(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.process) {
        resolve();
        return;
      }

      this.process.on('exit', () => {
        resolve();
      });

      this.process.kill();
      setTimeout(() => {
        if (this.process && !this.process.killed) {
          this.process.kill('SIGKILL');
        }
        resolve();
      }, 1000);
    });
  }
}
