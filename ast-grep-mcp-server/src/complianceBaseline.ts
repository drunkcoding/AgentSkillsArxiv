import { readFileSync } from "node:fs";
import path from "node:path";

export const SHARED_COMPLIANCE_BASELINE_PATH = path.resolve(
  __dirname,
  "../../mcp-compliance/baseline-policy.json"
);

export function readSharedComplianceBaseline(): unknown {
  return JSON.parse(readFileSync(SHARED_COMPLIANCE_BASELINE_PATH, "utf-8"));
}
