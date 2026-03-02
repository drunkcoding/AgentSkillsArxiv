# Meeting Summary Examples

Concrete before/after examples showing how to transform messy input into actionable summaries.

## Table of Contents

- [Example 1: Vague Notes → Actionable Summary](#example-1-vague-notes--actionable-summary)
- [Example 2: Raw Transcript → Executive Summary](#example-2-raw-transcript--executive-summary)
- [Example 3: Anti-Pattern Gallery](#example-3-anti-pattern-gallery)

---

## Example 1: Vague Notes → Actionable Summary

### Input (messy notes)

```
Product sync 2/15
- talked about the new onboarding flow
- Sarah mentioned the drop-off rate is bad
- Mike said we should try a shorter flow
- design team will look into it
- also need to update the pricing page, Jake had some ideas
- Q2 goals coming up, need to finalize
- database migration still ongoing, some issues with staging
```

### Output (actionable summary)

```markdown
# Meeting Summary: Product Sync

**Date:** Feb 15 | **Attendees:** Sarah, Mike, Jake, [others]
**Purpose:** Weekly product sync — onboarding, pricing, Q2 planning

## Decisions

- Proceed with testing a shorter onboarding flow to address drop-off — *Rationale: Current 5-step flow has high abandonment at step 3 (data from Sarah)*

## Action Items

| # | Task | Owner | Due | Context |
|---|------|-------|-----|---------|
| 1 | Design 2 shortened onboarding flow variants (3-step max) for A/B test | ⚠️ Owner TBD (design team) | ⚠️ Deadline TBD | Drop-off rate at step 3 is the primary conversion blocker |
| 2 | Draft pricing page update proposal with mockups | @Jake | ⚠️ Deadline TBD | Jake had specific ideas — needs to document for team review |
| 3 | Finalize Q2 product goals and share with team | ⚠️ Owner TBD | ⚠️ Deadline TBD | Upcoming Q2 planning cycle |
| 4 | Resolve staging environment issues blocking database migration | ⚠️ Owner TBD | ⚠️ Deadline TBD | Migration ongoing — staging issues creating risk |

## Discussion Highlights

- **Onboarding drop-off**: Sarah shared data showing high abandonment at step 3. Mike proposed a shorter flow. Team agreed to test this approach.
- **Pricing page**: Jake has ideas for an update — details not discussed in depth.
- **Database migration**: Staging environment issues are causing delays. No resolution discussed.

## Open Questions / Parking Lot

- Who owns the onboarding redesign? (Design team mentioned but no individual assigned)
- What are the specific staging issues blocking the migration?
- When are Q2 goals due for finalization?
```

**What changed:**
- Vague "design team will look into it" → flagged with ⚠️ Owner TBD
- Missing deadlines explicitly called out
- "drop-off rate is bad" → quantified as "high abandonment at step 3"
- Scattered topics → organized by impact

---

## Example 2: Raw Transcript → Executive Summary

### Input (transcript excerpt)

```
[10:02] Sarah: Okay so the big thing this week is we got the vendor
proposals back for the CI/CD migration. We got three proposals.

[10:03] Mike: Yeah I looked at all three. CircleCI is $2,400/month,
GitHub Actions would be basically free since we're already on Enterprise,
and Jenkins Cloud is $1,800 but needs dedicated DevOps support.

[10:04] Sarah: What's your recommendation?

[10:04] Mike: GitHub Actions honestly. The cost is negligible and the
integration with our existing repos would be seamless. Only downside is
the runner limitations for our ML pipeline jobs.

[10:05] Sarah: What about those ML jobs specifically?

[10:06] Mike: We'd need self-hosted runners for those. Maybe 2-3 GPU
instances. I estimate about $600/month for that.

[10:07] Sarah: So $600 total vs $2,400 for CircleCI? Let's go with
GitHub Actions. Mike can you put together a migration plan?

[10:07] Mike: Yeah I'll have it by Friday. Should I coordinate with
the ML team about the runner setup?

[10:08] Sarah: Yes, loop in Priya. She knows the pipeline requirements.
Let's target having the migration done by end of March.

[10:09] Jake: One thing — we should probably keep Jenkins running in
parallel for at least two weeks during transition. Don't want to break
anything mid-sprint.

[10:09] Sarah: Good call. Mike, include that in the plan.
```

### Output

```markdown
# Meeting Summary: CI/CD Migration Decision

**Date:** [Date] | **Attendees:** Sarah, Mike, Jake
**Purpose:** Evaluate vendor proposals and decide on CI/CD migration path

## Decisions

- **Migrate to GitHub Actions** with self-hosted GPU runners for ML pipeline — *Rationale: Near-zero marginal cost ($600/mo for GPU runners vs $2,400/mo CircleCI), seamless repo integration. Jenkins Cloud rejected due to dedicated DevOps overhead.*
- **Run Jenkins in parallel for 2 weeks during transition** — *Rationale: De-risk mid-sprint breakage (Jake's recommendation)*

## Action Items

| # | Task | Owner | Due | Context |
|---|------|-------|-----|---------|
| 1 | Draft CI/CD migration plan including parallel Jenkins period | @Mike | Friday | Must include self-hosted runner setup + 2-week parallel period |
| 2 | Coordinate with @Priya on ML pipeline runner requirements | @Mike | Before migration plan | Priya knows GPU pipeline specs — input needed for plan |
| 3 | Complete full CI/CD migration to GitHub Actions | @Mike | End of March | Target date set by Sarah |

## Discussion Highlights

- **Vendor comparison**: Three proposals evaluated — CircleCI ($2,400/mo), GitHub Actions (~$600/mo with GPU runners), Jenkins Cloud ($1,800/mo + DevOps overhead). GitHub Actions won on cost and integration.
- **ML pipeline risk**: Self-hosted GPU runners needed (2-3 instances). Mike to size with Priya.
- **Transition safety**: Jake recommended parallel Jenkins operation during migration. Adopted.
```

---

## Example 3: Anti-Pattern Gallery

Common mistakes and their fixes.

### ❌ Vague action item
```
- Follow up on the vendor thing
```

### ✅ Fixed
```
| 1 | Send vendor comparison spreadsheet to @Sarah for budget approval | @Mike | Feb 20 | Needed before Q3 budget lock |
```

---

### ❌ Group ownership
```
- Engineering will fix the performance issues
```

### ✅ Fixed
```
| 1 | Profile and fix the top 3 API latency bottlenecks (p99 > 500ms) | @Jake | Mar 1 | Customer complaints increasing — SLA at risk |
```

---

### ❌ Passive voice decision
```
- It was decided that we should probably move forward with option B
```

### ✅ Fixed
```
- **Proceed with Option B (event-driven architecture)** — *Rationale: 40% lower infrastructure cost vs Option A, and team has existing Kafka expertise. Sarah approved.*
```

---

### ❌ Missing deadline
```
- Jake to update the docs
```

### ✅ Fixed
```
| 1 | Update API docs to reflect v3 endpoint changes | @Jake | Feb 22 | Partner integration launching Feb 25 — docs must be ready 3 days prior |
```

---

### ❌ Burying action items in narrative
```
During the discussion about the Q3 roadmap, the team agreed that it
would be beneficial to conduct user research on the new dashboard
feature, and Sarah mentioned she could probably take the lead on
setting up the interviews, with Mike providing the question framework
from the previous research cycle.
```

### ✅ Fixed
```
## Discussion Highlights
- **Q3 roadmap**: Team agreed user research is needed before building the new dashboard feature.

## Action Items
| # | Task | Owner | Due | Context |
|---|------|-------|-----|---------|
| 1 | Set up 5 user research interviews for dashboard feature | @Sarah | Mar 5 | Validate dashboard concept before Q3 dev starts |
| 2 | Provide interview question framework (reuse from last cycle) | @Mike | Mar 1 | Sarah needs this before scheduling interviews |
```
