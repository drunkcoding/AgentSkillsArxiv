import type { ChildProcess } from "node:child_process";
import { spawn } from "node:child_process";
import { access, readFile } from "node:fs/promises";
import { accessSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { OpenClawPluginApi, OpenClawPluginService } from "openclaw/plugin-sdk";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DAEMON_SERVICE_ID = "remote-dispatch-daemon";
const RESTART_DELAY_MS = 10_000;
const FORCE_KILL_DELAY_MS = 5_000;

const DEFAULT_CHANNEL = "whatsapp";
const DEFAULT_PROJECT = "🤖 CodeDispatch";
const DEFAULT_POLL_INTERVAL = 60;
const DEFAULT_MAX_CONCURRENT = 3;

// Resolve scripts directory: try self-contained first, then skill symlink, then original source
const SCRIPTS_SEARCH_PATHS = [
  path.resolve(__dirname, "..", "scripts"),                                    // self-contained (plugin/../scripts)
  path.resolve(__dirname, "scripts"),                                           // scripts inside plugin dir
  path.join(os.homedir(), ".openclaw", "workspace", "skills", "openclaw-remote-dispatch", "scripts"), // skill symlink
  path.resolve(__dirname, "..", "..", "..", "workspace", "skills", "openclaw-remote-dispatch", "scripts"), // relative from extensions/
];

let SCRIPTS_DIR = SCRIPTS_SEARCH_PATHS[0];
let DISPATCHER_PATH = path.join(SCRIPTS_DIR, "dispatcher.py");

// Eagerly resolve scripts dir at import time
for (const candidate of SCRIPTS_SEARCH_PATHS) {
  try {
    const dispatcherCandidate = path.join(candidate, "dispatcher.py");
    accessSync(dispatcherCandidate);
    SCRIPTS_DIR = candidate;
    DISPATCHER_PATH = dispatcherCandidate;
    break;
  } catch {
    // try next path
  }
}
const DEFAULT_STATE_PATH = path.join(os.homedir(), ".openclaw", "remote-dispatch-state.json");

type ReplyAction = "approve" | "reject" | "continue" | "abort";

type DispatchPluginConfig = {
  notifyTarget: string;
  pollInterval: number;
  maxConcurrent: number;
  channel: string;
  project: string;
  autoStart: boolean;
};

type DispatchJob = {
  task_id?: string;
  status?: string;
  host?: string;
  folder?: string;
  title?: string;
  last_event_at?: number;
  error?: string;
};

type DispatchState = {
  daemon_pid?: number;
  last_poll?: number;
  jobs?: Record<string, DispatchJob>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isErrnoException(value: unknown): value is NodeJS.ErrnoException {
  return isRecord(value) && typeof (value as { code?: unknown }).code === "string";
}

function asNonEmptyString(value: unknown): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function asPositiveInteger(value: unknown, fallback: number): number {
  if (typeof value === "number" && Number.isFinite(value) && value > 0) {
    return Math.max(1, Math.floor(value));
  }
  if (typeof value === "string") {
    const parsed = Number.parseInt(value, 10);
    if (Number.isFinite(parsed) && parsed > 0) {
      return Math.max(1, parsed);
    }
  }
  return fallback;
}

function asBoolean(value: unknown, fallback: boolean): boolean {
  if (typeof value === "boolean") {
    return value;
  }
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (normalized === "true" || normalized === "1") {
      return true;
    }
    if (normalized === "false" || normalized === "0") {
      return false;
    }
  }
  return fallback;
}

function getPluginConfig(rawConfig: OpenClawPluginApi["pluginConfig"]): DispatchPluginConfig {
  const cfg = isRecord(rawConfig) ? rawConfig : {};

  return {
    notifyTarget:
      asNonEmptyString(cfg.notifyTarget) ?? asNonEmptyString(process.env.DISPATCH_NOTIFY_TARGET) ?? "",
    pollInterval: asPositiveInteger(cfg.pollInterval, DEFAULT_POLL_INTERVAL),
    maxConcurrent: asPositiveInteger(cfg.maxConcurrent, DEFAULT_MAX_CONCURRENT),
    channel: asNonEmptyString(cfg.channel) ?? DEFAULT_CHANNEL,
    project: asNonEmptyString(cfg.project) ?? DEFAULT_PROJECT,
    autoStart: asBoolean(cfg.autoStart, true),
  };
}

function resolveStatePath(): string {
  return asNonEmptyString(process.env.DISPATCH_STATE_PATH) ?? DEFAULT_STATE_PATH;
}

async function readDispatchState(api: OpenClawPluginApi): Promise<DispatchState | null> {
  const statePath = resolveStatePath();
  try {
    const raw = await readFile(statePath, "utf8");
    const parsed = JSON.parse(raw) as unknown;
    if (!isRecord(parsed)) {
      api.logger.warn(`[remote-dispatch] Invalid state JSON root at ${statePath}`);
      return null;
    }
    return parsed as DispatchState;
  } catch (error) {
    const enoent = isErrnoException(error) && error.code === "ENOENT";
    if (!enoent) {
      api.logger.warn(
        `[remote-dispatch] Failed reading state file ${statePath}: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    }
    return null;
  }
}

function getJobsMap(state: DispatchState | null): Record<string, DispatchJob> {
  if (!state || !isRecord(state.jobs)) {
    return {};
  }
  return state.jobs as Record<string, DispatchJob>;
}

function parseReplyCommand(content: string): { action: ReplyAction; taskPrefix: string } | null {
  const match = content.trim().match(/^(approve|reject|continue|abort)\s+([A-Za-z0-9._:-]+)$/i);
  if (!match) {
    return null;
  }

  const action = match[1]?.toLowerCase() as ReplyAction | undefined;
  const taskPrefix = match[2]?.trim() ?? "";
  if (!action || !taskPrefix) {
    return null;
  }

  return { action, taskPrefix };
}

function resolveTaskIdByPrefix(state: DispatchState | null, taskPrefix: string): {
  taskId: string | null;
  matches: string[];
} {
  const jobs = getJobsMap(state);
  const prefix = taskPrefix.trim().toLowerCase();
  if (!prefix) {
    return { taskId: null, matches: [] };
  }

  const candidateIds = new Set<string>();
  for (const [taskId, job] of Object.entries(jobs)) {
    if (taskId) {
      candidateIds.add(taskId);
    }
    if (typeof job.task_id === "string" && job.task_id.trim()) {
      candidateIds.add(job.task_id.trim());
    }
  }

  const matches = [...candidateIds].filter((taskId) => taskId.toLowerCase().startsWith(prefix));
  if (matches.length === 1) {
    return { taskId: matches[0] ?? null, matches };
  }
  return { taskId: null, matches };
}

function formatTimestamp(epochSeconds: unknown): string {
  if (typeof epochSeconds !== "number" || !Number.isFinite(epochSeconds) || epochSeconds <= 0) {
    return "unknown";
  }
  return new Date(epochSeconds * 1000).toISOString();
}

function formatJobLine(taskId: string, job: DispatchJob): string {
  const shortId = taskId.slice(0, 12);
  const status = typeof job.status === "string" ? job.status : "unknown";
  const host = typeof job.host === "string" && job.host ? job.host : "?";
  const folder = typeof job.folder === "string" && job.folder ? job.folder : "?";
  return `- ${shortId} [${status}] ${host} ${folder}`;
}

function waitForExit(child: ChildProcess, timeoutMs: number): Promise<boolean> {
  return new Promise((resolve) => {
    if (child.exitCode !== null || child.signalCode !== null) {
      resolve(true);
      return;
    }

    let settled = false;
    const done = (value: boolean) => {
      if (settled) {
        return;
      }
      settled = true;
      child.off("exit", onExit);
      clearTimeout(timer);
      resolve(value);
    };

    const onExit = () => done(true);
    const timer = setTimeout(() => done(false), timeoutMs);
    timer.unref?.();
    child.once("exit", onExit);
  });
}

function pipeProcessOutput(
  api: OpenClawPluginApi,
  child: ChildProcess,
  label: string,
  streamName: "stdout" | "stderr",
): void {
  const stream = streamName === "stdout" ? child.stdout : child.stderr;
  if (!stream) {
    return;
  }

  let buffer = "";
  stream.on("data", (chunk: Buffer | string) => {
    buffer += chunk.toString();
    const lines = buffer.split(/\r?\n/);
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      const text = line.trim();
      if (!text) {
        continue;
      }
      if (streamName === "stdout") {
        api.logger.info(`[remote-dispatch] ${label}: ${text}`);
      } else {
        api.logger.warn(`[remote-dispatch] ${label}: ${text}`);
      }
    }
  });

  stream.on("error", (error) => {
    api.logger.warn(
      `[remote-dispatch] ${label} stream error: ${
        error instanceof Error ? error.message : String(error)
      }`,
    );
  });
}

function formatDispatchHelp(): string {
  return [
    "Remote dispatch daemon control:",
    "",
    "/dispatch status  - Show daemon and active jobs",
    "/dispatch start   - Start daemon",
    "/dispatch stop    - Stop daemon",
    "/dispatch jobs    - List all jobs from state",
    "/dispatch help    - Show this help",
  ].join("\n");
}

/** Registers the Remote Dispatch gateway plugin (service, hook, and /dispatch command). */
export default function register(api: OpenClawPluginApi) {
  let daemonProcess: ChildProcess | null = null;
  let restartTimer: ReturnType<typeof setTimeout> | null = null;
  let shouldRunDaemon = false;
  let intentionalStop = false;

  const clearRestartTimer = () => {
    if (restartTimer) {
      clearTimeout(restartTimer);
      restartTimer = null;
    }
  };

  const scheduleRestart = () => {
    if (!shouldRunDaemon || restartTimer) {
      return;
    }

    api.logger.warn(`[remote-dispatch] Daemon restart scheduled in ${RESTART_DELAY_MS / 1000}s`);
    restartTimer = setTimeout(() => {
      restartTimer = null;
      if (!shouldRunDaemon) {
        return;
      }
      void startDaemon("automatic restart");
    }, RESTART_DELAY_MS);
    restartTimer.unref?.();
  };

  const startDaemon = async (reason: string): Promise<boolean> => {
    try {
      if (daemonProcess && daemonProcess.exitCode === null) {
        api.logger.info(`[remote-dispatch] Daemon already running (pid=${daemonProcess.pid ?? "?"})`);
        return true;
      }

      await access(DISPATCHER_PATH);
      const config = getPluginConfig(api.pluginConfig);
      if (!config.notifyTarget) {
        api.logger.error(
          "[remote-dispatch] notifyTarget is required (plugin config or DISPATCH_NOTIFY_TARGET)",
        );
        return false;
      }

      intentionalStop = false;
      clearRestartTimer();

      const args = [
        "-u",
        DISPATCHER_PATH,
        "--daemon",
        "--notify",
        config.notifyTarget,
        "--interval",
        String(config.pollInterval),
        "--max-concurrent",
        String(config.maxConcurrent),
        "--channel",
        config.channel,
        "--project",
        config.project,
      ];

      api.logger.info(
        `[remote-dispatch] Starting dispatcher (${reason}) interval=${config.pollInterval}s max=${config.maxConcurrent}`,
      );

      const child = spawn("python3", args, {
        cwd: SCRIPTS_DIR,
        stdio: ["ignore", "pipe", "pipe"],
      });

      daemonProcess = child;
      pipeProcessOutput(api, child, "daemon/stdout", "stdout");
      pipeProcessOutput(api, child, "daemon/stderr", "stderr");

      child.on("error", (error) => {
        api.logger.error(
          `[remote-dispatch] Failed to start dispatcher: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      });

      child.on("exit", (code, signal) => {
        daemonProcess = null;
        const wasIntentional = intentionalStop || !shouldRunDaemon;
        if (wasIntentional) {
          api.logger.info(
            `[remote-dispatch] Daemon exited intentionally (code=${code ?? "null"}, signal=${signal ?? "null"})`,
          );
          intentionalStop = false;
          return;
        }

        api.logger.warn(
          `[remote-dispatch] Daemon exited unexpectedly (code=${code ?? "null"}, signal=${signal ?? "null"})`,
        );
        scheduleRestart();
      });

      return true;
    } catch (error) {
      api.logger.error(
        `[remote-dispatch] Could not launch daemon: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
      return false;
    }
  };

  const stopDaemon = async (reason: string): Promise<boolean> => {
    shouldRunDaemon = false;
    clearRestartTimer();

    const child = daemonProcess;
    if (!child || child.exitCode !== null) {
      daemonProcess = null;
      intentionalStop = false;
      api.logger.info(`[remote-dispatch] Daemon is not running (${reason})`);
      return false;
    }

    intentionalStop = true;
    api.logger.info(`[remote-dispatch] Stopping daemon (${reason}) pid=${child.pid ?? "?"}`);

    try {
      child.kill("SIGTERM");
    } catch (error) {
      api.logger.warn(
        `[remote-dispatch] SIGTERM failed: ${error instanceof Error ? error.message : String(error)}`,
      );
    }

    const exitedGracefully = await waitForExit(child, FORCE_KILL_DELAY_MS);
    if (!exitedGracefully && child.exitCode === null) {
      api.logger.warn("[remote-dispatch] SIGTERM timeout reached; sending SIGKILL");
      try {
        child.kill("SIGKILL");
      } catch (error) {
        api.logger.warn(
          `[remote-dispatch] SIGKILL failed: ${error instanceof Error ? error.message : String(error)}`,
        );
      }
      await waitForExit(child, 1_000);
    }

    daemonProcess = null;
    intentionalStop = false;
    return true;
  };

  const runReplyRouting = async (messageEvent: unknown): Promise<void> => {
    if (!isRecord(messageEvent) || typeof messageEvent.content !== "string") {
      return;
    }

    const parsed = parseReplyCommand(messageEvent.content);
    if (!parsed) {
      return;
    }

    const state = await readDispatchState(api);
    const resolution = resolveTaskIdByPrefix(state, parsed.taskPrefix);

    if (!resolution.taskId) {
      if (resolution.matches.length > 1) {
        api.logger.warn(
          `[remote-dispatch] Ambiguous task prefix '${parsed.taskPrefix}' matches: ${resolution.matches.join(", ")}`,
        );
      } else {
        api.logger.warn(`[remote-dispatch] No task found for prefix '${parsed.taskPrefix}'`);
      }
      return;
    }

    api.logger.info(
      `[remote-dispatch] Routing reply '${parsed.action}' -> task ${resolution.taskId} from ${
        typeof messageEvent.from === "string" ? messageEvent.from : "unknown"
      }`,
    );

    try {
      await access(DISPATCHER_PATH);
    } catch (error) {
      api.logger.error(
        `[remote-dispatch] Cannot route reply; dispatcher missing at ${DISPATCHER_PATH}: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
      return;
    }

    const replyChild = spawn("python3", [DISPATCHER_PATH, "--reply", resolution.taskId, parsed.action], {
      cwd: SCRIPTS_DIR,
      stdio: ["ignore", "pipe", "pipe"],
    });

    pipeProcessOutput(api, replyChild, `reply/${resolution.taskId.slice(0, 12)}/stdout`, "stdout");
    pipeProcessOutput(api, replyChild, `reply/${resolution.taskId.slice(0, 12)}/stderr`, "stderr");

    replyChild.on("error", (error) => {
      api.logger.error(
        `[remote-dispatch] Reply subprocess failed: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    });

    replyChild.on("exit", (code, signal) => {
      api.logger.info(
        `[remote-dispatch] Reply subprocess completed for ${resolution.taskId} (code=${code ?? "null"}, signal=${signal ?? "null"})`,
      );
    });
  };

  const daemonService: OpenClawPluginService = {
    id: DAEMON_SERVICE_ID,
    start: async () => {
      try {
        const cfg = getPluginConfig(api.pluginConfig);
        if (!cfg.autoStart) {
          shouldRunDaemon = false;
          api.logger.info("[remote-dispatch] autoStart disabled; daemon will not start automatically");
          return;
        }

        shouldRunDaemon = true;
        const started = await startDaemon("service start");
        if (!started) {
          shouldRunDaemon = false;
        }
      } catch (error) {
        shouldRunDaemon = false;
        api.logger.error(
          `[remote-dispatch] Service start failed: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    },
    stop: async () => {
      try {
        await stopDaemon("service stop");
      } catch (error) {
        api.logger.error(
          `[remote-dispatch] Service stop failed: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
      }
    },
  };

  api.registerService(daemonService);

  api.on("message_received", (event) => {
    void runReplyRouting(event).catch((error) => {
      api.logger.error(
        `[remote-dispatch] message_received routing failed: ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
    });
  });

  api.registerCommand({
    name: "dispatch",
    description: "Remote dispatch daemon control",
    acceptsArgs: true,
    handler: async (ctx) => {
      try {
        const subcommand = (ctx.args ?? "").trim().split(/\s+/)[0]?.toLowerCase() ?? "";

        if (!subcommand || subcommand === "help") {
          return { text: formatDispatchHelp() };
        }

        if (subcommand === "start") {
          shouldRunDaemon = true;
          const started = await startDaemon("/dispatch start");
          if (!started) {
            shouldRunDaemon = false;
          }
          return {
            text: started
              ? "Remote dispatch daemon started."
              : "Failed to start daemon (check logs for python/dispatcher availability).",
          };
        }

        if (subcommand === "stop") {
          const stopped = await stopDaemon("/dispatch stop");
          return { text: stopped ? "Remote dispatch daemon stopped." : "Daemon was not running." };
        }

        if (subcommand === "status") {
          const state = await readDispatchState(api);
          const jobs = Object.entries(getJobsMap(state));
          const active = jobs.filter(([, job]) => job.status === "pending" || job.status === "running");
          const daemonStatus =
            daemonProcess && daemonProcess.exitCode === null
              ? `running (pid ${daemonProcess.pid ?? "?"})`
              : "stopped";

          if (active.length === 0) {
            return {
              text:
                `Daemon: ${daemonStatus}\n` +
                `State file: ${resolveStatePath()}\n` +
                `Active jobs: 0 / ${jobs.length}`,
            };
          }

          const lines = active.slice(0, 10).map(([taskId, job]) => formatJobLine(taskId, job));
          const extra = active.length > lines.length ? `\n...and ${active.length - lines.length} more` : "";
          return {
            text:
              `Daemon: ${daemonStatus}\n` +
              `State file: ${resolveStatePath()}\n` +
              `Active jobs: ${active.length} / ${jobs.length}\n` +
              lines.join("\n") +
              extra,
          };
        }

        if (subcommand === "jobs") {
          const state = await readDispatchState(api);
          const jobs = Object.entries(getJobsMap(state)).sort((a, b) => {
            const aTs = typeof a[1].last_event_at === "number" ? a[1].last_event_at : 0;
            const bTs = typeof b[1].last_event_at === "number" ? b[1].last_event_at : 0;
            return bTs - aTs;
          });

          if (jobs.length === 0) {
            return { text: `No jobs found in ${resolveStatePath()}.` };
          }

          const lines = jobs.slice(0, 30).map(([taskId, job]) => {
            const when = formatTimestamp(job.last_event_at);
            const status = typeof job.status === "string" ? job.status : "unknown";
            const title = typeof job.title === "string" && job.title.trim() ? ` — ${job.title.trim()}` : "";
            return `- ${taskId} [${status}] @ ${when}${title}`;
          });
          const more = jobs.length > lines.length ? `\n...and ${jobs.length - lines.length} more` : "";
          return { text: `Jobs (${jobs.length}):\n${lines.join("\n")}${more}` };
        }

        return { text: `Unknown subcommand: ${subcommand}\n\n${formatDispatchHelp()}` };
      } catch (error) {
        api.logger.error(
          `[remote-dispatch] /dispatch command failed: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
        return { text: "Dispatch command failed. See gateway logs for details." };
      }
    },
  });
}
