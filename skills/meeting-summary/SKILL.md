---
name: meeting-summary
description: Transform raw meeting notes, transcripts, or recordings into actionable meeting summaries focused on decisions, action items with owners and deadlines, and accountability. Use when the user asks to summarize a meeting, extract action items from meeting notes, create meeting minutes, write a meeting recap, process a meeting transcript, or generate follow-up documentation from any meeting. Triggers on mentions of "meeting summary", "meeting notes", "meeting recap", "action items from meeting", "meeting minutes", "standup notes", "retro summary", or when pasted text appears to be a meeting transcript or notes.
---

# Meeting Summary

Transform meeting notes or transcripts into accountability documents that drive follow-through.

## Core Principle

A meeting summary is not a recap — it is a commitment document. Every summary must answer: **What was decided? Who does what? By when?**

## Workflow

### 1. Assess Input

Determine what was provided:
- **Raw transcript** (verbose, speaker-labeled) → extract and compress
- **Rough notes** (bullet points, shorthand) → structure and clarify
- **Partial notes** (some items, missing context) → structure what exists, flag gaps

If input is ambiguous or too sparse, ask: "Can you share more context about what was discussed or decided?"

**Long transcripts (> ~12k tokens / ~8k words):** Use the chunked extraction pipeline described in [references/long-context.md](references/long-context.md). Do not attempt single-pass summarization on long meetings — quality degrades significantly.

### 2. Identify Meeting Type

Determine the meeting type to select the right format emphasis. See [references/meeting-types.md](references/meeting-types.md) for type-specific formats.

| Type | Primary Focus |
|------|--------------|
| Standup / sync | Blockers + commitments |
| Strategy / planning | Decisions + rationale |
| 1-on-1 | Feedback + growth actions |
| All-hands / town hall | Announcements + Q&A highlights |
| Client / external | Commitments + scope |
| Sprint planning / retro | Assignments + process improvements |
| Brainstorm | Ideas + evaluation next steps |
| General | Balanced across all sections |

If the type is unclear, default to **General**.

### 3. Produce Summary

Use the output format below. Omit sections that have zero content (e.g., no parking lot items), but **never omit Decisions or Action Items** — if none exist, state "None" explicitly.

## Output Format

```markdown
# Meeting Summary: [Topic/Name]

**Date:** [Date] | **Duration:** [Duration if known]
**Attendees:** [Names/roles]
**Purpose:** [One sentence — why this meeting happened]

## Decisions

- [Decision made] — *Rationale: [brief why]*
- [Decision made] — *Rationale: [brief why]*

## Action Items

| # | Task | Owner | Due | Context |
|---|------|-------|-----|---------|
| 1 | [Specific verb + deliverable] | @[Name] | [Date] | [Why this matters] |
| 2 | [Specific verb + deliverable] | @[Name] | [Date] | [Why this matters] |

## Discussion Highlights

- **[Topic]**: [Key points, concerns raised, proposals made]
- **[Topic]**: [Key points, concerns raised, proposals made]

## Open Questions / Parking Lot

- [Unresolved question — needs follow-up from @Name]
- [Deferred topic — revisit at next [meeting]]

## Next Meeting

- **When:** [Date/time if known]
- **Proposed agenda:** [Items carried forward]
```

## Action Item Rules

Every action item MUST have all five elements:

1. **What**: Start with a specific verb. "Draft Q3 budget with line items for A, B, C" not "Look into budget"
2. **Who**: One named person. Never "the team" or "engineering"
3. **When**: Firm date. Never "ASAP", "soon", or "when possible"
4. **Why**: One sentence of context so the owner remembers importance
5. **Next step**: Where the output goes ("Send to @Legal by Monday 9 AM")

If the source material has vague items, sharpen them. If owner or deadline is missing from the notes, flag it:

```
| 3 | Evaluate vendor pricing for CI/CD tools | ⚠️ Owner TBD | ⚠️ Deadline TBD | Needed before Q3 infra budget finalization |
```

## Anti-Patterns to Avoid

- **Passive voice**: "It was decided..." → "Team decided..." or "[Name] decided..."
- **Vague tasks**: "Follow up on X" → "Send X proposal to @Name by Friday"
- **Group ownership**: "Marketing will..." → "@Sarah will..."
- **Missing deadlines**: Always include a date, or explicitly flag ⚠️ Deadline TBD
- **Equal-weight everything**: Tangents and small talk get zero coverage. Weight by decision/action impact
- **Narrative prose for action items**: Use the table format, never bury actions in paragraphs
- **Omitting "no decisions"**: If a long meeting produced no decisions, say so — that's important signal

## Tone

- Direct and factual
- Use active voice throughout
- Use names, not roles ("Sarah" not "the PM")
- Keep discussion highlights to 1-2 sentences per topic — link to docs for depth
- Total summary should be scannable in 60-90 seconds

## Meeting Type Variations

For type-specific format guidance (what to emphasize, what to skip, adapted templates), see [references/meeting-types.md](references/meeting-types.md).

## Examples

For concrete before/after examples showing how to transform messy notes into actionable summaries, see [references/examples.md](references/examples.md).

## Long Meetings

For transcripts exceeding ~12k tokens (~45-60 minutes of conversation), use the chunked Map→Merge pipeline described in [references/long-context.md](references/long-context.md). This covers turn-safe chunking, per-chunk structured extraction, global merge with dedup/conflict resolution, and quality gates.
