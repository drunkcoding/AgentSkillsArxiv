import { afterEach, beforeEach, describe, expect, test } from "bun:test";

import { DEFAULT_PRD_CONFIG } from "../src/config";
import { distillFileContent } from "../src/distiller";

const ORIGINAL_API_KEY = process.env.OPENAI_API_KEY;

beforeEach(() => {
  process.env.OPENAI_API_KEY = "test-key";
});

afterEach(() => {
  if (ORIGINAL_API_KEY === undefined) {
    delete process.env.OPENAI_API_KEY;
  } else {
    process.env.OPENAI_API_KEY = ORIGINAL_API_KEY;
  }
});

describe("distillFileContent", () => {
  test("distills via openai-compatible endpoint", async () => {
    const config = structuredClone(DEFAULT_PRD_CONFIG);
    config.llm.provider = "openai-compatible";
    config.llm.model = "gpt-4o-mini";
    config.llm.apiKeyEnv = "OPENAI_API_KEY";
    config.llm.baseURL = "https://api.test.local/v1";

    const fetchMock: typeof fetch = async (_url, _init) => {
      const body = {
        choices: [
          {
            message: {
              content: JSON.stringify({
                summary: "Main module orchestrates task execution.",
                key_points: ["Contains initialization flow", "Has error handling path"],
                symbols: [
                  {
                    name: "run",
                    kind: "function",
                    line: 10,
                    signature: "run(config)",
                    why_important: "Entry point",
                  },
                ],
                sections: [
                  {
                    start_line: 1,
                    end_line: 25,
                    label: "Initialization",
                    why_important: "Bootstraps runtime",
                  },
                ],
                warnings: ["Needs raw read for exact patching"],
                escalation_hints: ["Use raw_read for line-accurate edits"],
                raw_read_recommended: true,
              }),
            },
          },
        ],
        usage: {
          prompt_tokens: 100,
          completion_tokens: 50,
          total_tokens: 150,
        },
      };

      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    };

    const result = await distillFileContent(
      "/repo/src/index.ts",
      "export function run(config) { return config }",
      config,
      { sessionID: "s1", lastUserMessage: "analyze this" },
      { fetchImpl: fetchMock },
    );

    expect(result.summary).toContain("orchestrates");
    expect(result.symbols.length).toBe(1);
    expect(result.usage?.totalTokens).toBe(150);
    expect(result.provider).toBe("openai-compatible");
  });

  test("throws on invalid JSON payload", async () => {
    const config = structuredClone(DEFAULT_PRD_CONFIG);
    config.llm.provider = "openai-compatible";
    config.llm.model = "gpt-4o-mini";
    config.llm.apiKeyEnv = "OPENAI_API_KEY";
    config.llm.baseURL = "https://api.test.local/v1";

    const fetchMock: typeof fetch = async (_url, _init) => {
      const body = {
        choices: [{ message: { content: "not-json" } }],
      };
      return new Response(JSON.stringify(body), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    };

    await expect(
      distillFileContent(
        "/repo/src/index.ts",
        "console.log('x')",
        config,
        { sessionID: "s1", lastUserMessage: "summarize this" },
        { fetchImpl: fetchMock },
      ),
    ).rejects.toThrow();
  });
});
