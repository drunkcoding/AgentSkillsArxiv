import { describe, expect, test } from "bun:test";

import { DEFAULT_PRD_CONFIG } from "../src/config";
import { decideReadStrategy, estimateTokens } from "../src/policy";

function testConfig() {
  const config = structuredClone(DEFAULT_PRD_CONFIG);
  config.policy.passThroughMaxTokens = 1_500;
  config.policy.distillMinTokens = 1_500;
  config.policy.metadataOnlyMinTokens = 12_000;
  return config;
}

describe("decideReadStrategy", () => {
  test("returns pass_through for small files", () => {
    const config = testConfig();
    const content = "const value = 1;\n".repeat(10);

    const decision = decideReadStrategy(
      "/repo/src/small.ts",
      Buffer.byteLength(content, "utf8"),
      estimateTokens(content),
      { sessionID: "s1", lastUserMessage: "please inspect" },
      config,
      content,
    );

    expect(decision.mode).toBe("pass_through");
  });

  test("returns pass_through for edit intent on medium file", () => {
    const config = testConfig();
    const content = "const value = 1;\n".repeat(600);

    const decision = decideReadStrategy(
      "/repo/src/medium.ts",
      Buffer.byteLength(content, "utf8"),
      estimateTokens(content),
      { sessionID: "s1", lastUserMessage: "please edit this function" },
      config,
      content,
    );

    expect(decision.mode).toBe("pass_through");
  });

  test("returns distill for large normal files", () => {
    const config = testConfig();
    const content = "const value = 1;\n".repeat(2_500);

    const decision = decideReadStrategy(
      "/repo/src/large.ts",
      Buffer.byteLength(content, "utf8"),
      estimateTokens(content),
      { sessionID: "s1", lastUserMessage: "analyze this" },
      config,
      content,
    );

    expect(decision.mode).toBe("distill");
  });

  test("returns metadata_only for huge generated files", () => {
    const config = testConfig();
    const content = "// AUTO-GENERATED\n" + "x=1;".repeat(120_000);

    const decision = decideReadStrategy(
      "/repo/dist/bundle.generated.js",
      Buffer.byteLength(content, "utf8"),
      estimateTokens(content),
      { sessionID: "s1", lastUserMessage: "review this" },
      config,
      content,
    );

    expect(decision.mode).toBe("metadata_only");
    expect(decision.fileClassification).toBe("generated");
  });
});
