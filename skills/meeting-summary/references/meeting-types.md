# Meeting Type Formats

Type-specific guidance for adapting the core summary format. Each type emphasizes different sections and may omit others.

## Table of Contents

- [Standup / Daily Sync](#standup--daily-sync)
- [Strategy / Planning](#strategy--planning)
- [1-on-1](#1-on-1)
- [All-Hands / Town Hall](#all-hands--town-hall)
- [Client / External](#client--external)
- [Sprint Planning / Retro](#sprint-planning--retro)
- [Brainstorm / Ideation](#brainstorm--ideation)

---

## Standup / Daily Sync

**Keep it short.** Standups are status checks, not deep discussions.

**Emphasize:** Blockers, commitments for today, items needing escalation.
**De-emphasize:** Discussion highlights (minimal), rationale (skip).
**Omit:** Parking lot (escalate blockers immediately instead).

**Adapted format:**

```markdown
# Standup — [Team Name] — [Date]

## Blockers 🚨
- [Blocker] — Owner: @Name — Needs: [what would unblock]

## Commitments Today
- @Name: [What they will deliver today]
- @Name: [What they will deliver today]

## FYI / Updates
- [Brief update relevant to the team]
```

**Target length:** 10-20 lines. If it's longer, the standup had too much discussion.

---

## Strategy / Planning

**Decision-heavy.** These meetings exist to make big calls. Capture the reasoning.

**Emphasize:** Decisions with detailed rationale, trade-offs considered, what was rejected and why.
**De-emphasize:** Granular task assignments (those happen in follow-up execution meetings).
**Include:** Risks identified, assumptions made, success criteria defined.

**Adapted format:**

```markdown
# [Strategy/Planning Topic] — [Date]

**Attendees:** [Names]
**Purpose:** [Strategic question being addressed]

## Decisions

| Decision | Rationale | Alternatives Considered | Owner |
|----------|-----------|------------------------|-------|
| [What was decided] | [Why — 1-2 sentences] | [What was rejected and why] | @Name |

## Strategic Context
- **Goal:** [What success looks like]
- **Constraints:** [Budget, timeline, dependencies]
- **Risks:** [Key risks identified, with mitigation owners]
- **Assumptions:** [What we're assuming is true]

## Action Items
[Standard action item table]

## Open Questions
[Standard parking lot]
```

---

## 1-on-1

**Private and growth-oriented.** Focus on feedback, career development, and personal follow-ups.

**Emphasize:** Feedback given/received, growth actions, personal commitments.
**De-emphasize:** Project status (keep that in standups).
**Tone:** Slightly more personal. Use first names naturally.

**Adapted format:**

```markdown
# 1-on-1: [Manager] ↔ [Report] — [Date]

## Feedback
- **Given:** [Feedback delivered, with context]
- **Received:** [Feedback received, with action planned]

## Discussion
- [Topic discussed — key takeaway]

## Action Items
| Task | Owner | Due |
|------|-------|-----|
| [Growth action or follow-up] | @Name | [Date] |

## Check-in Items for Next Time
- [Carry-forward topic]
```

---

## All-Hands / Town Hall

**Information-dense, low action.** These are broadcast meetings — capture what was announced and what questions came up.

**Emphasize:** Announcements, key metrics shared, Q&A highlights (especially unanswered questions).
**De-emphasize:** Action items (few people get assigned tasks in all-hands).
**Include:** Links to slides/recordings if available.

**Adapted format:**

```markdown
# All-Hands — [Date]

**Presented by:** [Names]

## Key Announcements
- [Announcement — impact/context]
- [Announcement — impact/context]

## Metrics / Results Shared
- [Metric]: [Value] ([trend: up/down/flat vs last period])

## Q&A Highlights
- **Q:** [Question asked] — **A:** [Answer given]
- **Q:** [Question asked] — **A:** ⚠️ Unanswered — follow-up from @Name

## Resources
- [Link to slides/recording]
```

---

## Client / External

**Scope-conscious and commitment-careful.** Every word matters — clients will reference this.

**Emphasize:** Commitments made (by both sides), scope changes, next steps with dates.
**De-emphasize:** Internal discussion, technical implementation details.
**Critical:** Clearly separate "we committed to" from "we discussed" — these are different.

**Adapted format:**

```markdown
# Meeting Summary: [Client Name] — [Date]

**Attendees:** [Names + company affiliations]
**Purpose:** [Meeting objective]

## Commitments Made
| Commitment | By | To | Due |
|------------|----|----|-----|
| [What was promised] | [Our team / Client] | [Recipient] | [Date] |

## Decisions
- [Decision — who approved]

## Discussion Summary
- [Topic]: [Key points — client perspective noted]

## Scope Changes ⚠️
- [Any scope additions/removals discussed — status: agreed/proposed/TBD]

## Next Steps
- Next meeting: [Date]
- [Deliverable due before next meeting]
```

---

## Sprint Planning / Retro

**Commitment and improvement focused.** Planning = what we commit to deliver. Retro = what we improve.

### Sprint Planning

**Emphasize:** Stories/tasks committed, capacity, sprint goal.

```markdown
# Sprint Planning — Sprint [N] — [Date]

**Sprint Goal:** [One sentence — what this sprint achieves]
**Capacity:** [X story points / hours available]

## Committed Work
| Story/Task | Owner | Points | Dependencies |
|------------|-------|--------|-------------|
| [Story title] | @Name | [N] | [Blocked by / None] |

## Not Committed (Stretch / Backlog)
- [Item punted — reason]

## Risks
- [Risk — mitigation plan]
```

### Retrospective

**Emphasize:** Process improvements with owners. Actions, not feelings.

```markdown
# Retro — Sprint [N] — [Date]

## What Went Well
- [Positive — why it worked]

## What Needs Improvement
- [Problem — root cause if discussed]

## Action Items for Next Sprint
| Improvement | Owner | Measure of Success |
|-------------|-------|--------------------|
| [Specific process change] | @Name | [How we know it worked] |
```

---

## Brainstorm / Ideation

**Idea-capture focused.** Don't kill ideas by over-structuring — but do create clear next steps to evaluate them.

**Emphasize:** Ideas generated (all of them), evaluation criteria, next steps to validate.
**De-emphasize:** Decisions (brainstorms shouldn't make final calls).
**Include:** Who proposed what (for follow-up questions).

**Adapted format:**

```markdown
# Brainstorm: [Topic] — [Date]

**Attendees:** [Names]
**Prompt:** [The question or problem being brainstormed]

## Ideas Generated
1. [Idea] — proposed by @Name — [brief description]
2. [Idea] — proposed by @Name — [brief description]
3. [Idea] — proposed by @Name — [brief description]

## Evaluation Criteria (if discussed)
- [Criterion 1: e.g., implementation cost]
- [Criterion 2: e.g., user impact]

## Top Candidates (if narrowed)
- [Idea X] — [why it rose to the top]
- [Idea Y] — [why it rose to the top]

## Next Steps
| Step | Owner | Due |
|------|-------|-----|
| [Evaluate/prototype/research idea X] | @Name | [Date] |
```
