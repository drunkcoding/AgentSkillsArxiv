import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

import type { PluginInput } from "@opencode-ai/plugin";

import PreReadDistillationPlugin from "../src/index";

const ORIGINAL_XDG_CONFIG_HOME = process.env.XDG_CONFIG_HOME;
const ORIGINAL_XDG_DATA_HOME = process.env.XDG_DATA_HOME;
const ORIGINAL_OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ORIGINAL_FETCH = globalThis.fetch;

const tempDirectories: string[] = [];

async function makeTempDir(prefix: string) {
  const directory = await mkdtemp(join(tmpdir(), prefix));
  tempDirectories.push(directory);
  return directory;
}

function makePluginInput(directory: string): PluginInput {
  const client = {
    app: {
      log: async () => {
        return;
      },
    },
  } as unknown as PluginInput["client"];

  return {
    client,
    directory,
    worktree: directory,
    project: {
      id: "project-id",
      name: "project-name",
      path: directory,
    } as PluginInput["project"],
    serverUrl: new URL("http://localhost:4096"),
    $: {} as PluginInput["$"],
  };
}

function makeReadOutput(filePath: string, content: string): string {
  const numbered = content
    .split(/\r?\n/)
    .map((line, index) => `${index + 1}: ${line}`)
    .join("\n");

  return [
    `<path>${filePath}</path>`,
    "<type>file</type>",
    "<content>",
    numbered,
    "",
    `(End of file - total ${content.split(/\r?\n/).length} lines)`,
    "</content>",
  ].join("\n");
}

async function writeConfig(configHome: string, configObject: Record<string, unknown>) {
  const opencodeDir = join(configHome, "opencode");
  await mkdir(opencodeDir, { recursive: true });
  await writeFile(join(opencodeDir, "prd.jsonc"), JSON.stringify(configObject, null, 2), "utf8");
}

beforeEach(() => {
  process.env.OPENAI_API_KEY = "test-openai-key";
});

afterEach(async () => {
  globalThis.fetch = ORIGINAL_FETCH;

  if (ORIGINAL_XDG_CONFIG_HOME === undefined) {
    delete process.env.XDG_CONFIG_HOME;
  } else {
    process.env.XDG_CONFIG_HOME = ORIGINAL_XDG_CONFIG_HOME;
  }

  if (ORIGINAL_XDG_DATA_HOME === undefined) {
    delete process.env.XDG_DATA_HOME;
  } else {
    process.env.XDG_DATA_HOME = ORIGINAL_XDG_DATA_HOME;
  }

  if (ORIGINAL_OPENAI_API_KEY === undefined) {
    delete process.env.OPENAI_API_KEY;
  } else {
    process.env.OPENAI_API_KEY = ORIGINAL_OPENAI_API_KEY;
  }

  await Promise.all(tempDirectories.map((directory) => rm(directory, { recursive: true, force: true })));
  tempDirectories.length = 0;
});

describe("plugin hooks", () => {
  test("tool.execute.after distills large read outputs", async () => {
    const configHome = await makeTempDir("prd-config-");
    const dataHome = await makeTempDir("prd-data-");
    const projectDir = await makeTempDir("prd-project-");

    process.env.XDG_CONFIG_HOME = configHome;
    process.env.XDG_DATA_HOME = dataHome;

    await writeConfig(configHome, {
      enabled: true,
      llm: {
        provider: "openai-compatible",
        model: "gpt-4o-mini",
        apiKeyEnv: "OPENAI_API_KEY",
        baseURL: "https://api.test.local/v1",
      },
      policy: {
        passThroughMaxTokens: 10,
        distillMinTokens: 20,
        metadataOnlyMinTokens: 100000,
      },
    });

    globalThis.fetch = (async () => {
      const body = {
        choices: [
          {
            message: {
              content: JSON.stringify({
                summary: "Large file distilled.",
                key_points: ["point"],
                symbols: [],
                sections: [],
                warnings: [],
                escalation_hints: ["Use raw_read when patching"],
                raw_read_recommended: true,
              }),
            },
          },
        ],
        usage: {
          prompt_tokens: 60,
          completion_tokens: 20,
          total_tokens: 80,
        },
      };

      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;

    const plugin = await PreReadDistillationPlugin(makePluginInput(projectDir));

    const filePath = join(projectDir, "large.ts");
    const content = "const value = 1;\n".repeat(300);
    const output = {
      title: "read",
      output: makeReadOutput(filePath, content),
      metadata: {},
    };

    await plugin["tool.execute.after"]?.(
      {
        tool: "read",
        sessionID: "session-1",
        callID: "call-1",
        args: { filePath },
      },
      output,
    );

    expect(output.output).toContain("[PRE_READ_DISTILL_V1]");
    expect(output.output).toContain("Large file distilled.");
  });

  test("tool.execute.after can return metadata-only", async () => {
    const configHome = await makeTempDir("prd-config-");
    const dataHome = await makeTempDir("prd-data-");
    const projectDir = await makeTempDir("prd-project-");

    process.env.XDG_CONFIG_HOME = configHome;
    process.env.XDG_DATA_HOME = dataHome;

    await writeConfig(configHome, {
      enabled: true,
      llm: {
        provider: "openai-compatible",
        model: "gpt-4o-mini",
        apiKeyEnv: "OPENAI_API_KEY",
        baseURL: "https://api.test.local/v1",
      },
      policy: {
        passThroughMaxTokens: 10,
        distillMinTokens: 20,
        metadataOnlyMinTokens: 25,
      },
    });

    const plugin = await PreReadDistillationPlugin(makePluginInput(projectDir));

    const filePath = join(projectDir, "very-large.ts");
    const content = "const value = 1;\n".repeat(300);
    const output = {
      title: "read",
      output: makeReadOutput(filePath, content),
      metadata: {},
    };

    await plugin["tool.execute.after"]?.(
      {
        tool: "read",
        sessionID: "session-2",
        callID: "call-2",
        args: { filePath },
      },
      output,
    );

    expect(output.output).toContain("[PRE_READ_METADATA_ONLY_V1]");
  });

  test("tool.definition appends read behavior note", async () => {
    const configHome = await makeTempDir("prd-config-");
    const dataHome = await makeTempDir("prd-data-");
    const projectDir = await makeTempDir("prd-project-");

    process.env.XDG_CONFIG_HOME = configHome;
    process.env.XDG_DATA_HOME = dataHome;

    await writeConfig(configHome, {
      enabled: true,
    });

    const plugin = await PreReadDistillationPlugin(makePluginInput(projectDir));

    const output = {
      description: "Read files from disk.",
      parameters: {},
    };

    await plugin["tool.definition"]?.({ toolID: "read" }, output);

    expect(output.description).toContain("raw_read");
  });
});
