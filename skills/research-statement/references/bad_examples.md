# Annotated Bad Examples

Five bad-example excerpts with diagnosis-and-fix. Use to recognize anti-patterns in drafts under review.

## How to Use This File

For each example: read the bad excerpt, identify the failures listed in the diagnosis, then study the improvement. When reviewing a draft, scan for similar patterns.

---

## Bad Example 1: The Boy-Genius Opener (CS PhD applications)

Source pattern: documented by Andy Pavlo (CMU) — `https://www.cs.cmu.edu/~pavlo/blog/2015/10/how-to-write-a-bad-statement-for-a-computer-science-phd-admissions-application.html`

**Bad excerpt (representative composite):**

> "When I was eight years old, my father brought home a computer, and I immediately became fascinated with how software works. Since that day, I have dreamed of getting a Ph.D. in computer science to pursue a career in research."

**Diagnoses:**

1. **Irrelevant hook.** Pavlo: "We don't care that you got the first computer on your street." Childhood narrative says nothing about research potential.
2. **Unverifiable claim.** No reviewer believes that an 8-year-old's reaction predicted research aptitude.
3. **Boring.** Reviewers reading 200 statements have seen this opener 50 times.
4. **Zero research content.** No question, no method, no result. Two sentences entirely wasted.
5. **Telling not showing.** "Fascinated" — declared, not demonstrated.

**Improvement (Pavlo's own example):**

> "I am interested in database systems, specifically in making it easier for developers to build applications that process large amounts of data. During my undergraduate research, I worked on [specific project] where I [specific contribution], which convinced me that [specific intellectual insight]."

**Why the fix works:**
- Opens with current research interest (specific subfield).
- Demonstrates concrete experience.
- Identifies a forward-looking intellectual insight.
- Preserves the same paragraph length while filling it with content.

---

## Bad Example 2: The Vague Generic (ML application)

Source pattern: documented by Stanley Chan (Purdue) via GradPilot — `https://gradpilot.com/news/sop-faculty-insights-graduate-school`

**Bad excerpt:**

> "I am interested in machine learning and would like to work on deep learning applications. I am also interested in optimization and statistics, and I believe these areas have great potential to make an impact in the world."

**Diagnoses:**

1. **Subfield too broad.** "Machine learning" + "deep learning applications" + "optimization" + "statistics" = "I haven't chosen yet."
2. **No question.** What specific problem in any of these areas?
3. **Generic impact claim.** "Make an impact in the world" is interchangeable across 100 statements.
4. **List addiction (mini).** Three areas listed without connection.
5. **Hedging stack.** "Would like to" + "believe" + "potential to" — three layers of softening.

**Improvement:**

> "I am interested in neural architecture search, specifically in developing gradient-based search methods that reduce computational cost while maintaining accuracy. My experience with optimization algorithms in [specific project] established the technical foundation for this direction. Professor Z's work on [specific paper or system] aligns directly with my approach."

**Why the fix works:**
- Names a specific subfield within ML.
- Identifies a concrete technical claim ("gradient-based search... reduce cost while maintaining accuracy").
- Connects past work to future direction.
- Names a specific faculty fit with a specific paper.

---

## Bad Example 3: Karen Kelsky's "Worst Job Letter" Pattern

Source pattern: composite from Karen Kelsky's blog `https://theprofessorisin.com/2012/09/28/the-worst-job-letter-ever-written-not-really-but/`

**Bad excerpt (composite):**

> "My research spans many areas, including environmental policy, sustainability, climate justice, energy transition, and global governance. I am completing two independent projects related to my dissertation. I believe that I would be an asset to your department because my interdisciplinary background and dedication to teaching and research would contribute to your community. I am well prepared to meet these goals and look forward to contributing."

**Diagnoses:**

1. **List addiction.** Five areas in one sentence — no theme.
2. **Vague trajectory.** "Two independent projects related to my dissertation" — are they extending or departing? Reader cannot tell.
3. **Begging language.** "I would be an asset" + "well prepared" + "look forward to contributing" — three desperate lines.
4. **No core argument.** Dissertation never named with a thesis. No idea what the candidate has actually argued.
5. **Generic appeal.** "Interdisciplinary background and dedication to teaching and research" — interchangeable across all candidates.
6. **Closing pleasantries.** Wastes the closing sentence on filler.

**Improvement:**

> "My research argues that [specific thesis from dissertation]. The dissertation, [Title], demonstrates this through [specific case study], showing that [specific finding]. The two follow-on projects extend this argument to [domain X] and [domain Y]. Project A asks [specific question]; Project B asks [specific question]. These connect to [target department's existing strength on Z]."

**Why the fix works:**
- Names the thesis directly.
- Connects the dissertation to specific follow-on projects.
- Each follow-on project has a specific question.
- Fit paragraph references existing department strength.

---

## Bad Example 4: The Generic Lesson Learned

Source pattern: documented by Adrian Sampson (Cornell) — `https://www.cs.cornell.edu/~asampson/blog/gradstatement.html`

**Bad excerpt:**

> "Working on this project, experiments were conducted to evaluate the system's performance. The results were analyzed and presented at a workshop. This project taught me the importance of collaboration and clear communication in research, lessons that I will carry forward into my future work."

**Diagnoses:**

1. **Passive voice (twice).** "Experiments were conducted" + "results were analyzed" — obscures what the candidate specifically did.
2. **Generic lesson.** Sampson: "Exactly the things that everybody learns when giving their first talk." Says nothing.
3. **No technical content.** What system? What workshop? What measured? What concluded?
4. **Future hand-wave.** "Lessons that I will carry forward" — empty.
5. **No quantification.** Even within the limited content, no numbers.

**Improvement:**

> "I designed and implemented a distributed consensus module in the Veni filesystem, which required developing a novel leader-election protocol. The protocol reduced recovery time from 200ms to 40ms in a 10-node cluster, a 5× improvement over the prior best. I presented this at OSDI 2024."

**Why the fix works:**
- Active voice with explicit role.
- Names the system and the workshop/conference.
- Quantifies the result (5× speedup).
- Names the technical contribution (novel leader-election protocol).

---

## Bad Example 5: The Coy Theorist

Source pattern: documented by Karen Kelsky as "The Job Search is Not a Striptease" — `https://theprofessorisin.com/2017/09/01/the-job-search-is-not-a-striptease/`

**Bad excerpt:**

> "I argue that my dissertation research has implications for our understanding of how policy interacts with vulnerable populations in non-trivial ways. I conclude that gender plays a significant role in shaping these dynamics, and that further research is needed to fully understand these complex interactions."

**Diagnoses:**

1. **Pseudo-theoretical hedge.** "Non-trivial ways" + "complex interactions" + "significant role" — three vague hedges.
2. **No actual argument stated.** What does the candidate actually argue? The reader knows: dissertations have implications, gender plays a role. Tell me what.
3. **Future research as deflection.** "Further research is needed" — every paper says this. Doesn't tell the committee what *you* will do.
4. **Withholding.** Kelsky: the striptease — promising the argument while never delivering it.
5. **Reviewer fatigue.** By sentence 2, the reviewer has stopped reading carefully.

**Improvement:**

> "My dissertation argues that policy implementations of housing assistance produce systematically different outcomes for women and men, primarily because evaluation criteria privilege full-time employment histories over caregiving labor. The mechanism is [specific mechanism]; I demonstrate this through analysis of [specific dataset / case studies]. My future research extends this to [specific second case], asking whether [specific question]."

**Why the fix works:**
- States the actual argument with a specific mechanism.
- Names the data / case study.
- Future research opens a specific second case with a specific question.
- No "further research is needed" hedge.

---

## Diagnosis Vocabulary

When reviewing a draft, use these compact diagnostic labels:

| Label | What it means | Where to look in `red_flags.md` |
|---|---|---|
| **boy-genius opener** | childhood-narrative opening | Red Flag 1 |
| **passion declaration** | "I am passionate" without evidence | Red Flag 2 |
| **world-changer** | grandiose generic claim | Red Flag 3 |
| **gap-without-stakes** | "no one has studied this" | Red Flag 4 |
| **pseudo-theoretical hedge** | jargon-laden non-claim | Red Flag 5 |
| **anyone-could-say-this** | generic statement | Red Flag 6 |
| **open-ended researcher** | "I'm interested in everything" | Red Flag 7 |
| **studying-under** | deferential to advisor | Red Flag 8 |
| **I-statement avalanche** | self-centered prose | Red Flag 9 |
| **generic flattery** | unspecific department praise | Red Flag 10 |
| **passive obscuration** | passive voice hides role | Red Flag 11 |
| **generic lesson** | "I learned communication is important" | Red Flag 13 |
| **closing pleasantry** | "I look forward to..." | Red Flag 14 |
| **list addiction** | spawned by lack of focus | Red Flag 15 |
| **begging** | "I would be an asset" | Red Flag 16 |
| **apologetic ambition** | softening ambitions | Red Flag 17 |
| **trauma disclosure** | inappropriate personal disclosure | Red Flag 18 |
| **trend-surfing** | "in recent years..." opener | Red Flag 19 |
| **quantification-free result** | "significant improvement" | Red Flag 20 |
| **chronological past** | year-ordered past work | Pattern A |
| **single-continuation future** | only "extend my dissertation" | Pattern B |
| **fit-as-praise** | adjective-stuffed fit paragraph | Pattern C |

When delivering review feedback, use one diagnostic label per sentence; do not combine multiple labels into one comment.
