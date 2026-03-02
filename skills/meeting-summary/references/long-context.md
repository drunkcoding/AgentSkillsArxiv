# Long Meeting Transcripts: Chunking & Synthesis

Guide for processing meeting transcripts that exceed single-pass context limits.

## Table of Contents

- [When Chunking Is Not Needed](#when-chunking-is-not-needed)
- [Default Pipeline: Map→Merge](#default-pipeline-mapmerge)
- [Step 1: Turn-Safe Chunking](#step-1-turn-safe-chunking)
- [Step 2: Per-Chunk Structured Extraction](#step-2-per-chunk-structured-extraction)
- [Step 3: Global Merge + Conflict Resolution](#step-3-global-merge--conflict-resolution)
- [Step 4: Final Render](#step-4-final-render)
- [Alternative Approaches](#alternative-approaches)
- [Meeting-Specific Tips](#meeting-specific-tips)
- [Quality Gates](#quality-gates)

---

## When Chunking Is Not Needed

Use single-pass extraction (no chunking) when **all** conditions are true:

- Transcript ≤ **12k–14k tokens** (~8k–10k words, roughly 45–60 min meeting)
- ≤ **8 active speakers**
- Expected extracted items ≤ **~30 total** (decisions + actions + open questions)
- No multi-session stitching

If any threshold is exceeded, use the chunked pipeline below.

---

## Default Pipeline: Map→Merge

A 2-pass hierarchical extraction pipeline optimized for meeting transcripts.

```
Raw transcript
  → [Turn-safe chunking]
  → [Per-chunk structured extraction (parallel)]
  → [Global merge + conflict resolution]
  → [Final render using standard output format]
```

### Why this approach (not single-pass)

Long-context models suffer from "lost in the middle" — information in the middle of long inputs gets lower recall. Meeting transcripts compound this because:
- Action items span multiple speaker turns (proposed → discussed → modified → assigned)
- Decisions referenced early get acted on later
- Key details hide in low-signal conversational noise

Structured extraction per chunk followed by deterministic merge avoids these pitfalls.

---

## Step 1: Turn-Safe Chunking

### Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Target chunk size | **1,800 tokens** | Balances extraction quality with sufficient context |
| Hard max | **2,400 tokens** | Allows complete speaker turns without forced splits |
| Overlap | **200 tokens** or last **1–2 turns** (whichever is larger) | Preserves cross-turn action item arcs |

### Split priority (in order)

1. **Agenda/topic boundaries** — "Moving on to...", "Next topic:", explicit agenda markers
2. **Facilitator handoffs** — "Sarah, can you walk us through...", moderator transitions
3. **Speaker turn boundaries** — natural pause between speakers
4. **Timestamp gaps** — silences > 30 seconds suggest topic shifts

### Rules

- **Never split mid-speaker-turn** unless a single turn exceeds the hard max (2,400 tokens). In that case, split at sentence boundaries within the turn.
- **Preserve per chunk:** `chunk_id`, `start_timestamp`, `end_timestamp`, `speakers[]`, `turn_ids[]`
- If transcript has no timestamps, split by turn count: ~15–25 turns per chunk as a fallback.

### For very long meetings (> 80k tokens)

Use 3-tier hierarchical mode:
1. Chunk extraction (as above)
2. Topic-level mini-merges (group chunks by detected topic)
3. Global merge across topics

---

## Step 2: Per-Chunk Structured Extraction

Prompt each chunk independently to extract structured JSON:

```json
{
  "chunk_id": "c3",
  "decisions": [
    {
      "decision": "Migrate to GitHub Actions with self-hosted GPU runners",
      "status": "approved",
      "approver": "Sarah",
      "rationale": "Near-zero marginal cost vs CircleCI",
      "evidence": {"start_turn": 42, "end_turn": 47}
    }
  ],
  "action_items": [
    {
      "task": "Draft CI/CD migration plan including parallel Jenkins period",
      "owner": "Mike",
      "deadline": "Friday",
      "context": "Must include self-hosted runner setup + 2-week parallel period",
      "blockers": null,
      "evidence": {"start_turn": 48, "end_turn": 49}
    }
  ],
  "discussion_topics": [
    {
      "topic": "CI/CD vendor comparison",
      "summary": "Three proposals evaluated. GitHub Actions selected on cost and integration.",
      "state": "resolved"
    }
  ],
  "open_questions": [
    {
      "question": "GPU runner sizing — how many instances needed?",
      "assigned_to": "Priya",
      "evidence": {"turn": 46}
    }
  ],
  "parking_lot": []
}
```

### Extraction prompt guidance

- Use low temperature (0–0.2) for consistency
- Require evidence references (turn IDs or timestamps) for every extracted item
- Detect commitment language: "I'll…", "Can you…", "We need to…", "Let's…", "Action item:"
- Detect decision verbs: "approved", "agreed", "decided", "locked", "confirmed", "going with"
- Detect parking lot signals: "take offline", "revisit later", "follow-up meeting", "park that"

---

## Step 3: Global Merge + Conflict Resolution

Combine all chunk JSONs into a single unified extraction.

### Entity normalization

- **Owner names**: Map aliases to canonical names. "Sam", "Samantha", "Samantha L." → "Samantha Lee"
- **Dates**: Convert relative references using meeting date as anchor. "Next Friday" (meeting on March 2) → "March 7"
- **Project/tool names**: Normalize casing and abbreviations. "GHA", "github actions", "GitHub Actions" → "GitHub Actions"

### Dedup rules

**Action items**: Deduplicate by composite key:
```
(normalized_owner, normalized_verb_object_stem, deadline_bucket)
```
- "deadline_bucket" groups within ±2 days (handles "Friday" vs "end of week")
- When duplicates found, keep the version with more context/specificity
- Preserve all source `chunk_ids` as provenance

**Decisions**: Deduplicate by semantic similarity of decision text.
- If same decision appears in multiple chunks at different states:
  - `proposed` < `agreed` < `approved` < `final`
  - Keep highest state. If states conflict, latest timestamp wins **unless** earlier has explicit "final/approved/locked."

### Cross-chunk resolution

- **Open questions**: If a later chunk contains an explicit answer or decision that resolves an earlier open question, mark it resolved and link to the resolving decision.
- **Action item evolution**: If an action item is proposed in chunk 1, modified in chunk 3, and finalized in chunk 5, keep only the final version but note the evolution in provenance.
- **Decision reversals**: If a decision from chunk 2 is explicitly reversed in chunk 7, keep both with timestamps and mark the reversal. Don't silently overwrite.

---

## Step 4: Final Render

Render the merged schema into the standard meeting summary output format (from SKILL.md). Do **not** re-process the raw transcript — use the merged structured data only. This ensures consistency and avoids re-introducing lost-in-the-middle errors.

Apply the same output rules from the core skill:
- Decisions section with rationale
- Action items table with 5-element format (What, Who, When, Why, Next Step)
- Discussion highlights (aggregate from topic summaries)
- Open questions / parking lot
- Next meeting info

---

## Alternative Approaches

### Refine Chain (sequential running summary)

Process chunks sequentially, carrying a running summary forward:
```
chunk_1 → summary_1
chunk_2 + summary_1 → summary_2
chunk_3 + summary_2 → summary_3
...
```

**Use when:** User wants narrative-style recap over structured extraction.
**Avoid when:** Precise action-item dedup and accountability tracking are needed (the default case).
**Risk:** Running summary loses early details as context budget fills. Action items from early chunks get compressed or dropped.

### Single Huge-Context Prompt

Stuff entire transcript into one prompt.

**Use when:** Under the no-chunking thresholds above.
**Avoid when:** Transcript exceeds ~14k tokens or has >8 speakers.
**Risk:** "Lost in the middle" — items in the middle 40% of the transcript get ~30% lower recall.

### RAG Retrieval-Then-Summarize

Embed transcript chunks → retrieve relevant chunks per query → summarize retrieved set.

**Use when:** Post-hoc Q&A after primary summary exists ("What did we say about the timeline?").
**Avoid as primary pipeline:** Misses latent action items spread across non-adjacent chunks that wouldn't be retrieved together.

---

## Meeting-Specific Tips

These distinguish meeting transcript processing from general document chunking:

1. **Speaker turns are atomic units.** Never split mid-turn. A turn where someone says "I'll handle the migration plan by Friday, and I'll loop in Priya" contains two action items that must stay together.

2. **Commitment language is the signal.** Train extraction to weight: "I'll", "I can", "Let me", "Can you", "We need to", "Action item:", "Let's", "You should". These are higher-signal than general discussion.

3. **Decision state is a progression.** Track: mentioned → proposed → discussed → agreed → approved → final. Don't flatten this — the state matters for accountability.

4. **Relative dates are traps.** "Next week", "by Friday", "end of quarter" — always resolve to absolute dates using the meeting date anchor. Flag if meeting date is unknown.

5. **Cross-references happen naturally.** "As Sarah mentioned earlier..." or "Going back to the budget discussion..." — these are signals that information from another chunk is relevant to the current extraction.

6. **Silence and tangents are noise.** Meeting transcripts are ~40-60% low-signal (pleasantries, tangents, repetition, filler). The extraction step should compress aggressively.

---

## Quality Gates

Before rendering the final summary, validate the merged extraction:

| Check | Threshold | Action if Failed |
|-------|-----------|-----------------|
| Action items missing owner | > 15% | Re-extract from source chunks with owner-focused prompt |
| Items missing evidence refs | > 30% | Re-extract with stricter evidence requirements |
| Duplicate decisions after merge | Any | Re-run dedup with lower similarity threshold |
| Unresolved date references | Any | Flag with ⚠️ in output; ask user for meeting date if unknown |
| Zero decisions from >30min meeting | Suspicious | Re-extract with decision-focused prompt; if still zero, note explicitly in output |
