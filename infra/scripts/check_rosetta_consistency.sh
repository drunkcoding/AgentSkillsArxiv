#!/usr/bin/env bash
# Rosetta consistency linter for skills/tutor-core/references/cross-stack-rosetta.md
# Enforces RID scheme, citation rule, minimum row counts, and YAML question-seed schema.
#
# Usage: ./infra/scripts/check_rosetta_consistency.sh
# Exit 0 on success; non-zero on first failure.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROSETTA="${REPO_ROOT}/skills/tutor-core/references/cross-stack-rosetta.md"
TOPIC_FILES=(
    "${REPO_ROOT}/skills/cuda-tutor-setup/references/topic-cuda-kernels.md"
    "${REPO_ROOT}/skills/cuda-tutor-setup/references/topic-cutlass.md"
    "${REPO_ROOT}/skills/cuda-tutor-setup/references/topic-cutile.md"
    "${REPO_ROOT}/skills/triton-tutor-setup/references/topic-triton-basics.md"
    "${REPO_ROOT}/skills/triton-tutor-setup/references/topic-tiling-autotuning.md"
    "${REPO_ROOT}/skills/triton-tutor-setup/references/topic-matmul-patterns.md"
    "${REPO_ROOT}/skills/triton-tutor-setup/references/topic-attention-reductions.md"
    "${REPO_ROOT}/skills/triton-tutor-setup/references/topic-compiler-internals.md"
)

# Color output
if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; RESET=''
fi
fail() { printf "${RED}FAIL${RESET}: %s\n" "$*" >&2; exit 1; }
ok() { printf "${GREEN}ok${RESET}: %s\n" "$*"; }
warn() { printf "${YELLOW}warn${RESET}: %s\n" "$*" >&2; }

[ -f "$ROSETTA" ] || fail "missing: $ROSETTA"
ok "found rosetta: $ROSETTA"

# Delegate to embedded Python for YAML parsing + table parsing.
# The Python script reads the rosetta, all 8 topic files, and emits failures via non-zero exit.
python3 - "$ROSETTA" "${TOPIC_FILES[@]}" <<'PYEOF'
import re
import sys
import os

rosetta_path = sys.argv[1]
topic_paths = sys.argv[2:]

with open(rosetta_path) as f:
    rosetta = f.read()

errors = []

# ─── 1. No placeholder strings (table rows only — prose may discuss the rule) ──
for i, line in enumerate(rosetta.splitlines(), 1):
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        continue
    for forbidden in ["TODO", "FIXME", "XXX", "???"]:
        if forbidden in stripped:
            errors.append(f"rosetta:{i}: forbidden placeholder '{forbidden}' in table row: {stripped[:120]}")
    # A bare 'TBD' as a cell value (not inside an identifier or longer word) is the actual concern.
    for cell in [c.strip() for c in stripped.split("|")[1:-1]]:
        if cell == "TBD" or cell == "?" or cell == "TODO":
            errors.append(f"rosetta:{i}: bare placeholder cell '{cell}' in table row")

# ─── 2. Parse mapping tables (sections 2-6) and validate RIDs + Sources ────
# Mapping tables are markdown tables under "## N. ..." headers where N in 2..6.
# Row format: | RID | ... | ... | ... | Source |
# Header row is the one starting with "| RID |".
# Separator row follows with hyphens.
# Data rows have a RID matching R{section}-{nn}.

section_re = re.compile(r"^## (\d+)\. ", re.MULTILINE)
section_starts = [(int(m.group(1)), m.start(), m.end()) for m in section_re.finditer(rosetta)]
sections = {}
for i, (sec_num, start, end) in enumerate(section_starts):
    next_start = section_starts[i + 1][1] if i + 1 < len(section_starts) else len(rosetta)
    sections[sec_num] = rosetta[end:next_start]

MIN_ROWS = {2: 12, 3: 8, 4: 8, 5: 6, 6: 8}
canonical_rids = {}  # RID -> dict with cuda_side, triton_side, source

for sec_num, min_rows in MIN_ROWS.items():
    if sec_num not in sections:
        errors.append(f"rosetta: missing section {sec_num}")
        continue
    body = sections[sec_num]
    # Find first markdown table in this section
    table_lines = []
    in_table = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)
            in_table = True
        elif in_table and not stripped:
            # blank line ends the table
            break
        elif in_table and not stripped.startswith("|"):
            break
    if len(table_lines) < 3:
        errors.append(f"rosetta: section {sec_num} has no mapping table")
        continue
    header = [c.strip() for c in table_lines[0].split("|")[1:-1]]
    if header[0] != "RID":
        errors.append(f"rosetta: section {sec_num} header column 1 must be 'RID', got '{header[0]}'")
        continue
    if header[-1] != "Source":
        errors.append(f"rosetta: section {sec_num} header LAST column must be 'Source', got '{header[-1]}'")
        continue
    # Data rows: index >= 2 (skip header + separator)
    data_rows = table_lines[2:]
    if len(data_rows) < min_rows:
        errors.append(f"rosetta: section {sec_num} has {len(data_rows)} rows, need ≥{min_rows}")
    for row_idx, row_line in enumerate(data_rows, 1):
        cells = [c.strip() for c in row_line.split("|")[1:-1]]
        if len(cells) != len(header):
            errors.append(f"rosetta: section {sec_num} row {row_idx} column count mismatch")
            continue
        rid = cells[0]
        if not re.match(rf"^R{sec_num}-\d{{2}}$", rid):
            errors.append(f"rosetta: section {sec_num} row {row_idx}: RID '{rid}' doesn't match R{sec_num}-NN format")
        if rid in canonical_rids:
            errors.append(f"rosetta: duplicate RID '{rid}'")
        source = cells[-1].strip()
        if not source or source.lower() in {"tbd", "?", "todo"}:
            errors.append(f"rosetta: row {rid} has empty/placeholder Source")
        # CUDA side is column 1 (index 1), Triton side column 2 (index 2)
        canonical_rids[rid] = {
            "cuda_side": cells[1] if len(cells) > 1 else "",
            "triton_side": cells[2] if len(cells) > 2 else "",
            "source": source,
            "section": sec_num,
        }

# ─── 3. Parse YAML question seeds from section 7 ──────────────────────────
sec7_match = re.search(r"^## 7\.", rosetta, re.MULTILINE)
if not sec7_match:
    errors.append("rosetta: missing section 7 (question seeds)")
    seeds = []
else:
    sec7_body = rosetta[sec7_match.end():]
    yaml_blocks = re.findall(r"```yaml\n(.*?)\n```", sec7_body, re.DOTALL)
    seeds = []
    for i, block in enumerate(yaml_blocks):
        # Tiny YAML parser sufficient for our schema (no nested dicts beyond options list)
        seed = {}
        in_options = False
        options = []
        for raw in block.splitlines():
            line = raw.rstrip()
            if not line:
                continue
            if in_options:
                m_opt = re.match(r"^  - (.+)$", line)
                if m_opt:
                    val = m_opt.group(1).strip()
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    options.append(val)
                    continue
                else:
                    in_options = False
                    seed["options"] = options
            m_kv = re.match(r"^([a-z-]+):\s*(.*)$", line)
            if m_kv:
                key, val = m_kv.group(1), m_kv.group(2).strip()
                if key == "options":
                    in_options = True
                    options = []
                else:
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    seed[key] = val
        if in_options:
            seed["options"] = options
        seeds.append((i + 1, seed))

REQUIRED_FIELDS = {"id", "rid", "direction", "mapping-section", "question-type",
                   "primary-topic", "source", "stem", "options", "correct"}
DIRECTIONS = {"cuda-to-triton", "triton-to-cuda"}
QUESTION_TYPES = {"recall", "conceptual", "distinction", "behavioral", "debugging"}

# ─── 4. Validate every seed ───────────────────────────────────────────────
for idx, seed in seeds:
    missing = REQUIRED_FIELDS - seed.keys()
    if missing:
        errors.append(f"seed Q{idx}: missing fields {sorted(missing)}")
        continue
    if seed["direction"] not in DIRECTIONS:
        errors.append(f"seed Q{idx}: bad direction '{seed['direction']}'")
    try:
        ms = int(seed["mapping-section"])
        if ms not in MIN_ROWS:
            errors.append(f"seed Q{idx}: bad mapping-section '{ms}'")
    except ValueError:
        errors.append(f"seed Q{idx}: non-integer mapping-section '{seed['mapping-section']}'")
    if seed["question-type"] not in QUESTION_TYPES:
        errors.append(f"seed Q{idx}: bad question-type '{seed['question-type']}'")
    if seed["rid"] not in canonical_rids:
        errors.append(f"seed Q{idx}: rid '{seed['rid']}' does not resolve to any canonical row")
    if not seed.get("source", "").strip():
        errors.append(f"seed Q{idx}: empty source")
    if len(seed.get("options", [])) != 4:
        errors.append(f"seed Q{idx}: must have exactly 4 options, got {len(seed.get('options', []))}")

# ─── 5. Distribution requirements ─────────────────────────────────────────
if len(seeds) < 36:
    errors.append(f"seeds: total count {len(seeds)} < 36")

direction_counts = {d: 0 for d in DIRECTIONS}
section_counts = {s: 0 for s in MIN_ROWS}
qtype_counts = {q: 0 for q in QUESTION_TYPES}

for idx, seed in seeds:
    if seed.get("direction") in direction_counts:
        direction_counts[seed["direction"]] += 1
    try:
        ms = int(seed.get("mapping-section", -1))
        if ms in section_counts:
            section_counts[ms] += 1
    except ValueError:
        pass
    if seed.get("question-type") in qtype_counts:
        qtype_counts[seed["question-type"]] += 1

for d, n in direction_counts.items():
    if n < 18:
        errors.append(f"seeds: direction '{d}' count {n} < 18")
for s, n in section_counts.items():
    min_n = 4 if s == 5 else 6
    if n < min_n:
        errors.append(f"seeds: mapping-section {s} count {n} < {min_n}")
for q, n in qtype_counts.items():
    if n < 6:
        errors.append(f"seeds: question-type '{q}' count {n} < 6")

# ─── 6. Topic-appendix RID consistency ────────────────────────────────────
for tpath in topic_paths:
    if not os.path.isfile(tpath):
        errors.append(f"topic file missing: {tpath}")
        continue
    with open(tpath) as f:
        content = f.read()
    m_app = re.search(r"^## Cross-Stack Equivalent.*$", content, re.MULTILINE)
    if not m_app:
        # Topics without a peer correctly skip the appendix; only flag for the 8 we expect to have it.
        errors.append(f"{os.path.basename(tpath)}: missing 'Cross-Stack Equivalent' appendix")
        continue
    appendix = content[m_app.start():]
    # Find first markdown table in the appendix
    table_lines = []
    in_table = False
    for line in appendix.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)
            in_table = True
        elif in_table and not stripped:
            break
        elif in_table and not stripped.startswith("|"):
            break
    if len(table_lines) < 3:
        errors.append(f"{os.path.basename(tpath)}: appendix has no table")
        continue
    header = [c.strip() for c in table_lines[0].split("|")[1:-1]]
    if header[0] != "RID":
        errors.append(f"{os.path.basename(tpath)}: appendix table column 1 must be 'RID', got '{header[0]}'")
        continue
    for row_idx, row_line in enumerate(table_lines[2:], 1):
        cells = [c.strip() for c in row_line.split("|")[1:-1]]
        if not cells:
            continue
        rid = cells[0]
        if rid not in canonical_rids:
            errors.append(f"{os.path.basename(tpath)} row {row_idx}: RID '{rid}' does not resolve to canonical Rosetta")
            continue
        # The appendix's "This topic's concept" (cells[1]) is a CONCISE summary, not a
        # verbatim copy. Require at least one backtick-quoted identifier from the
        # appendix concept to appear in either the canonical CUDA-side or Triton-side
        # string. This catches drift (RID renumbering, content mismatch) without
        # rejecting legitimate paraphrasing.
        local_concept = cells[1] if len(cells) > 1 else ""
        cuda_side = canonical_rids[rid]["cuda_side"]
        triton_side = canonical_rids[rid]["triton_side"]
        local_idents = set(re.findall(r"`([^`]+)`", local_concept))
        canonical_idents = set(re.findall(r"`([^`]+)`", cuda_side + " " + triton_side))
        if local_idents and not (local_idents & canonical_idents):
            errors.append(
                f"{os.path.basename(tpath)} row {row_idx} RID {rid}: appendix identifiers "
                f"{sorted(local_idents)[:3]} don't overlap any canonical identifier "
                f"{sorted(canonical_idents)[:5]}"
            )
        elif not local_idents:
            # No identifiers in either side — fall back to substring check on
            # 4+ char alphabetic tokens to detect copy-paste drift.
            local_tokens = set(re.findall(r"[A-Za-z]{4,}", local_concept))
            canonical_tokens = set(re.findall(r"[A-Za-z]{4,}", cuda_side + " " + triton_side))
            if local_tokens and not (local_tokens & canonical_tokens):
                errors.append(
                    f"{os.path.basename(tpath)} row {row_idx} RID {rid}: appendix tokens "
                    f"don't overlap canonical (local='{local_concept[:60]}', "
                    f"canonical='{cuda_side[:40]} / {triton_side[:40]}')"
                )

# ─── Report ────────────────────────────────────────────────────────────────
if errors:
    print(f"\nFAIL: {len(errors)} consistency error(s):", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"\nok: rosetta + {len(topic_paths)} topic appendices consistent")
    print(f"  - canonical RIDs: {len(canonical_rids)}")
    print(f"  - question seeds: {len(seeds)} (≥36)")
    print(f"  - direction counts: {direction_counts}")
    print(f"  - mapping-section counts: {section_counts}")
    print(f"  - question-type counts: {qtype_counts}")

PYEOF

ok "all rosetta consistency checks passed"
