# Platform Mechanics: OpenReview vs HotCRP

## Table of Contents

1. [OpenReview](#openreview)
2. [HotCRP](#hotcrp)
3. [Key Differences](#key-differences)

---

## OpenReview

### Rebuttal Stage Configuration
OpenReview rebuttal is a configurable stage. Venue chairs set:
- Start date and deadline
- Number of rebuttals allowed (per paper, per review, or multiple)
- Reader visibility (who sees responses and when)
- Custom rebuttal form fields and limits

### Default Rebuttal Form
The platform default form specifies:
- `type: string`
- `maxLength: 2500`
- `markdown: true`

**This is a template default — venues override it.** NeurIPS uses 10,000 chars, ICML uses 5,000 chars, AAAI uses 2,500 chars.

### Formatting
- CommonMark-based markdown
- Inline HTML: **not supported**
- Images: **not supported** in markdown renderer
- LaTeX math: venue-dependent (many ML venues enable it)
- Markdown availability itself is venue-configurable

### Visibility Model
- **Batch reveal** (NeurIPS model): all rebuttals revealed to reviewers/ACs at end of rebuttal window, not immediately on submission
- **Continuous** (ICLR model): comments visible as posted during discussion period
- **Immediate** (some venues): response visible to reviewer upon posting

Always check: does the reviewer see your response immediately, or only after the window closes? This affects strategy — batch reveal means you cannot iteratively respond.

### Author Actions During Rebuttal
- Submit text response (markdown)
- Cannot upload files (most ML venues)
- Cannot include links (NeurIPS) or non-anonymized URLs (ICML)
- Cannot upload revised paper (NeurIPS/ICML) vs. can revise (ICLR)

### How ACs/SACs Use Responses
- AC reads all reviews + all responses before writing meta-review
- Responses that directly address reviewer concerns with evidence are most useful
- ACs use responses to adjudicate disagreements between reviewers
- Unanswered concerns are assumed to be valid weaknesses

---

## HotCRP

### Rebuttal Configuration
HotCRP treats author responses as comments:
- Chairs enable response collection in decision settings
- Response is optional and conference-configured
- Format, limits, and allowed content set per conference

### Format Options
- **Text field** (most common): direct text entry with word/character limit
- **PDF upload**: some venues allow PDF rebuttal (rare for systems venues)
- LaTeX math support: available in HotCRP but venue-dependent
- Rich formatting: HotCRP supports advanced formatting but most systems venues use plain text

### Visibility Model
- Typically reviewers see response before or during PC discussion
- PC chair controls when responses become visible
- Response is part of the discussion record visible to all PC members assigned to the paper

### One-Shot Revision (OSR) Model
Some HotCRP venues (NSDI, SIGCOMM, MOBICOM) use OSR instead of or in addition to classic rebuttal:
- Authors receive reviews
- Authors submit a **revised paper** addressing specific concerns
- PC evaluates revised version
- This is distinct from a text rebuttal — it is a full paper revision cycle

### Author Actions During Rebuttal
- Submit text response within word limit
- Cannot attach files (most systems venues)
- Cannot include revised figures in text response (EuroSys explicitly strips these)
- New experiments explicitly disallowed (OSDI) or conditionally allowed (ASPLOS)

### How PC Uses Responses
- PC members read response before discussion
- PC discussion references response when adjudicating
- Short, direct responses are more likely to be fully read
- SOSP explicitly notes reviewers are "not expected to read very long responses"

---

## Key Differences

| Aspect | OpenReview | HotCRP |
|--------|-----------|--------|
| Response format | Markdown text field | Text field (some venues: PDF) |
| Typical limit unit | Characters | Words |
| Visibility | Batch or continuous (venue-configured) | Typically visible before PC discussion |
| Revised paper upload | Venue-dependent (ICLR yes, NeurIPS/ICML no) | Via OSR process at some venues |
| Discussion model | Can be multi-round (ICLR) or single-shot (NeurIPS/ICML) | Typically single-shot response |
| Math support | Venue-dependent | Available but venue-dependent |
| Image/figure support | Not in markdown renderer | Not in text responses (EuroSys explicitly strips) |

### Practical Implications

**For OpenReview venues:**
- Check character limit carefully — "2500" vs "10000" is a 4x difference
- Know whether you get one response or per-review responses
- Know whether visibility is batch or immediate
- Plan for follow-up rounds if available (ICML, ICLR)

**For HotCRP venues:**
- Check word limit in CFP — varies from ~500 to 2000
- Assume text-only unless explicitly told otherwise
- Be concise — PC members reading 100+ papers will skim long responses
- If OSR is available and your paper is borderline, understand the OSR process separately
