/** Position in a file (0-indexed line and column). */
export interface AstGrepPosition {
  line: number;
  column: number;
}

/** Byte offset range. */
export interface AstGrepByteOffset {
  start: number;
  end: number;
}

/** Source range combining byte offsets and line/column positions. */
export interface AstGrepRange {
  byteOffset: AstGrepByteOffset;
  start: AstGrepPosition;
  end: AstGrepPosition;
}

/** A single match from `ast-grep run --json=compact`. */
export interface AstGrepMatch {
  text: string;
  range: AstGrepRange;
  file: string;
  lines: string;
  charCount: { leading: number; trailing: number };
  language: string;
  /** Present when a rewrite pattern (-r) is provided. */
  replacement?: string;
  /** Byte offsets for the replacement text. */
  replacementOffsets?: AstGrepByteOffset;
  /** Captured meta-variables (present with rewrite). */
  metaVariables?: {
    single: Record<string, { text: string; range: AstGrepRange }>;
    multi: Record<string, unknown>;
    transformed: Record<string, unknown>;
  };
}

/** A label attached to a scan diagnostic. */
export interface AstGrepLabel {
  text: string;
  range: AstGrepRange;
  style: string;
}

/** A single result from `ast-grep scan --json=compact`. */
export interface AstGrepScanResult {
  text: string;
  range: AstGrepRange;
  file: string;
  lines: string;
  charCount: { leading: number; trailing: number };
  language: string;
  ruleId: string;
  severity: string;
  note: string | null;
  message: string;
  labels: AstGrepLabel[];
}

/** Result of executing the ast-grep CLI. */
export interface CliResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}
