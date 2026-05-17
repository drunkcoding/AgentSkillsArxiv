# Proficiency Tracking — Exact Math and Edge Cases

> Read this file when updating the dashboard or a concept file. Provides the precise formulas the quiz tutor must implement deterministically.

## Per-Concept Status

A concept row tracks: `Concept` (name), `Attempts`, `Correct`, `Last Tested` (ISO date), `Status`.

**Status state machine** (🔴 = unresolved, 🟢 = resolved):

| Trigger | Old Status | New Status |
|---------|------------|------------|
| First time tested, answered **wrong** | (none) | 🔴 |
| First time tested, answered **correct** | (none) | 🟢 |
| Existing 🔴, answered **correct** | 🔴 | 🟢 (KEEP the error-note as history) |
| Existing 🔴, answered **wrong** again | 🔴 | 🔴 (UPDATE error-note, increment counters) |
| Existing 🟢, answered **wrong** | 🟢 | 🔴 (ADD error-note, increment counters) |
| Existing 🟢, answered **correct** | 🟢 | 🟢 (just increment counters) |

For EVERY trigger, increment `Attempts`; increment `Correct` only on correct answers; set `Last Tested` to today's date in ISO 8601 (`YYYY-MM-DD`).

## Per-Topic Badge

After updating concept rows, recompute the topic badge:

```
correct_topic = sum(Correct) across all rows in concepts/{topic}.md
attempts_topic = sum(Attempts) across all rows in concepts/{topic}.md
```

If `attempts_topic == 0` → badge ⬜ Unmeasured (rate displayed as `-`).

Otherwise:

```
rate = correct_topic / attempts_topic * 100   # rounded to nearest integer
```

| Rate range | Badge | Label |
|------------|-------|-------|
| 0–39       | 🟥    | Weak |
| 40–69      | 🟨    | Fair |
| 70–89      | 🟩    | Good |
| 90–100     | 🟦    | Mastered |
| no data    | ⬜    | Unmeasured |

**Tiebreaker convention**: boundary values belong to the LOWER tier. Examples:
- 39.4% → 🟥 (floor at 39)
- 39.6% → 🟨 (rounds to 40, crosses into Fair)
- 70.0% → 🟩
- 89.999% → 🟩 (89 floor)
- 90.0% → 🟦

## Cumulative (Whole-Vault) Rate

```
correct_total = sum of correct across all 6 concept files
attempts_total = sum of attempts across all 6 concept files
cumulative_rate = correct_total / attempts_total * 100
```

If `attempts_total == 0` → display `-`.

## Weakest / Strongest Topic

Among topics with `attempts_topic > 0` (i.e., NOT ⬜):

- **Weakest** = the topic with the lowest `rate`. Tiebreaker: highest `attempts_topic` (the one we know the most confidently is weak). Second tiebreaker: lowest topic number (1–6).
- **Strongest** = the topic with the highest `rate`. Tiebreaker: highest `attempts_topic`. Second tiebreaker: lowest topic number.

If no topic has `attempts_topic > 0` → display `-`.

## Resolved / Unresolved Concept Counts

```
unresolved_total = count of 🔴 rows across all 6 concept files
resolved_total   = count of 🟢 rows across all 6 concept files
```

These appear in the dashboard's `## Stats` section.

## Dual-Attribution Rule

When a question genuinely tests two topics (per `quiz-rules.md` Topic-Attribution Rule), write the SAME concept row in BOTH topic concept files. Mark the concept name with a trailing `(↔ {other-topic})`, e.g.:

```
| TMA cp.async.bulk in CUTLASS mainloop (↔ cutlass) | 2 | 1 | 2026-05-15 | 🔴 |
```

- Both files increment `Attempts` and (if correct) `Correct`.
- Status transitions apply independently in each file (a wrong answer flips BOTH files' rows to 🔴).
- The dual-attributed concept counts in BOTH topic badges' computations.
- It counts ONCE in `unresolved_total` / `resolved_total` — deduplicate by concept name (strip the `(↔ …)` suffix and compare).

## Edge Cases

| Case | Handling |
|------|----------|
| Concept tested for the first time, answered correctly | New row with `Attempts=1`, `Correct=1`, `Status=🟢`. No error-note. |
| Concept tested 10 times all wrong | `Attempts=10`, `Correct=0`, rate=0%, badge for topic is 🟥 (if it's the only concept). |
| Same concept appears in 2 quiz rounds (different rephrasings) | ONE row, accumulate counters across rounds. Update error note with the latest confusion. |
| Quiz answer is partially correct (none of our options support this) | All questions are 4-option single-select; there is no partial credit. Treat as wrong. |
| Concept file does not yet exist | Create it from the template in `cuda-tutor/SKILL.md` before adding the first row. |
| `attempts_topic == 0` (division by zero) | Skip the rate formula entirely; emit badge ⬜ Unmeasured and rate `-`. The same applies to `attempts_total == 0`. |
| Dashboard does not yet exist | Create from the template in `cuda-tutor/SKILL.md`; initialize all 6 rows with `0/0/-/⬜`. |
| User cancels mid-quiz | Do NOT update the concept file or dashboard. Quiz only counts if grading completes. |

## Error-Note Lifecycle

- ADD a note when a concept transitions to 🔴 (first miss OR repeated miss).
- KEEP the most recent error note when 🔴 → 🟢 (learning history is valuable).
- DO NOT delete error notes when the concept is mastered — they are useful for spaced-recall design later.
- Format strictly:
  ```
  **<concept name>**
  - Confusion: <what the user picked instead>
  - Key point: <correct understanding in one sentence>
  ```

## Verifiability Hook

Whenever you finish Phase 6 of the quiz workflow, the dashboard's `Total` row must satisfy:

```
Total.Correct  == sum(per-topic.Correct)
Total.Wrong    == sum(per-topic.Attempts - per-topic.Correct)
Total.Rate     == Total.Correct / sum(per-topic.Attempts) * 100   (if denom > 0)
```

If any of these fail, re-derive from the concept files and re-write the dashboard. NEVER manually edit the `Total` row.
