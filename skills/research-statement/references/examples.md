# Annotated Real Examples

Ten dissected real opening paragraphs from successful CS faculty applications. Patterns extend to other disciplines.

## How to Use This File

For each example: read the verbatim opening, then read the structural decomposition. Adapt the **structure**, not the words. Copying any of these is plagiarism.

---

## Example 1: Mae Milano (PL × Distributed Systems)

**Verbatim:**
> "My research focuses on building new systems and designing new language abstractions to make programming at scale feasible for more people, without sacrificing performance, correctness, or expressive power in the process."

**Decomposition:**
- *Domain:* "building new systems and designing new language abstractions"
- *Stake:* "make programming at scale feasible for more people"
- *Triple constraint:* "without sacrificing performance, correctness, or expressive power"
- *Pattern:* Vision-then-method, single-sentence

**Why it works:** the triple constraint is what gives the sentence specific intellectual content. Most candidates would say "make programming at scale easier" and stop. Naming the trade-off triangle signals research taste.

**Source:** https://www.languagesforsyste.ms/files/faculty-applications/research%20statement%20(new).pdf

---

## Example 2: Sam Westrick (PL / Parallelism)

**Verbatim:**
> "To address the difficulty of parallel programming, my goal is to raise the level of abstraction at which programmers can achieve high performance."

**Decomposition:**
- *Gap:* "the difficulty of parallel programming"
- *Vision:* "raise the level of abstraction"
- *Constraint:* "at which programmers can achieve high performance"
- *Pattern:* Compressed; gap → vision in one sentence

**Why it works:** economical; nothing wasted. The closing constraint ("can achieve high performance") prevents the vision from being just "make it easier" — it's "make it easier *while keeping speed*", which is a real research challenge.

**Source:** https://www.cs.cmu.edu/~swestric/other/westrick-research-statement.pdf

---

## Example 3: Ryan Marcus (ML for Database Systems)

**Verbatim:**
> "From database query optimizers to garbage collectors, today's computer systems are composed of hand-tuned heuristics. These off-the-shelf heuristics are convenient and freely available, but are optimized for a 'general purpose' case, and thus do not maximize system performance for most actual applications."

**Decomposition:**
- *Sentence 1:* counter-intuitive observation about the field
- *Sentence 2:* the gap that observation reveals
- *Pattern:* Gap-as-revelation; vision sentence comes in paragraph 2

**Why it works:** the framing "today's computer systems are composed of hand-tuned heuristics" is observational and surprising — most readers haven't thought of database optimizers and garbage collectors together this way. By the time the vision arrives, the reader is already invested in the gap.

**Source:** https://rmarcus.info/blog/assets/RMarcusApplicationMaterials.pdf

---

## Example 4: Talia Ringer (Verification)

**Verbatim:**
> "My long-term goal as a researcher is to make it easy for programmers of all skill levels across all domains to build formally verified software systems."

**Decomposition:**
- *Vision:* "make it easy for programmers... to build formally verified software systems"
- *Scope:* "of all skill levels across all domains"
- *Pattern:* Pure-vision, single declarative

**Why it works:** the scope qualifier is what makes this ambitious without being grandiose. "All skill levels across all domains" is a measurable bar — a reviewer can immediately think "what would that look like?"

**Source:** https://dependenttyp.es/materials/research.pdf

---

## Example 5: Bharath Hariharan (Computer Vision)

**Verbatim:**
> "Behind the exceptional abilities of modern computer vision models are millions of hours of human labor in annotation. I therefore seek to build learning-based computer vision systems that can learn from very limited data."

**Decomposition:**
- *Hidden cost:* "millions of hours of human labor in annotation"
- *Vision:* "learn from very limited data"
- *Pattern:* Counter-intuitive observation → derived vision

**Why it works:** points at a structural problem the field has internalized but rarely names directly. The "I therefore" connector explicitly derives the vision from the gap, which models good research-statement reasoning.

**Source:** https://www.cs.cornell.edu/~bharathh/researchstatement.pdf

---

## Example 6: Ashok Cutkosky (ML / Optimization)

**Verbatim:**
> "I am broadly interested in making machine learning more about engineering and less about intuition and guesswork. Although machine learning is widely and profitably deployed throughout industry, many crucial design decisions are driven primarily by trial and error rather than by principled understanding."

**Decomposition:**
- *Vision (sentence 1):* engineering vs. guesswork distinction
- *Evidence the gap exists (sentence 2):* trial-and-error in industry
- *Pattern:* Vision-then-evidence

**Why it works:** "engineering vs. intuition and guesswork" compresses a research taste claim into 9 words. Sentence 2 immediately substantiates by describing actual industry practice.

**Source:** https://cs.stanford.edu/~ashokc/jobs/researchstatement.pdf

---

## Example 7: Talia Ringer (paragraph 2 — vision elaboration)

**Verbatim:**
> "[After her vision sentence] These tools have already been used to automate difficult changes, and to support an industrial proof engineer writing proofs about an implementation of the TLS handshake protocol."

**Decomposition:**
- *Evidence of impact:* "automate difficult changes"
- *Industrial validation:* "industrial proof engineer writing proofs about TLS"
- *Pattern:* vision-then-validation

**Why it works:** in two sentences, the vision is shown to already be working in practice. The TLS handshake protocol citation is specific enough to be checkable; that specificity is the signal.

---

## Example 8: Dimi Racordon (PL)

**Verbatim:**
> "My research advances methods and techniques that empower developers to write expressive, efficient, and reliable software. I gravitate toward model checking, formal verification, and programming language design, with a particular focus on advanced type systems."

**Decomposition:**
- *Sentence 1:* vision (developer-facing outcome)
- *Sentence 2:* methods (technical approach)
- *Pattern:* Vision-then-method, two-sentence

**Why it works:** "I gravitate toward" is a research-taste signal — declarative without being preachy. The list of methods is specific enough that a PL reviewer immediately places the candidate.

**Source:** https://kyouko-taiga.github.io/assets/pdfs/research-statement.pdf

---

## Example 9: Michael D. Adams (PL)

**Verbatim:**
> "My research vision is for programmers to be able to communicate their intent to a computer (i.e., write programs) as quickly as and at the same high level that they can communicate to other programmers and that the resulting software artifacts would be clear enough that they obviously have no bugs instead of having no obvious bugs."

**Decomposition:**
- *Vision:* programmers communicating intent at high level
- *Memorable hook:* "obviously have no bugs instead of having no obvious bugs" (Hoare echo)
- *Pattern:* Vision with literary hook

**Why it works:** the Hoare echo is a known phrase in the PL community; using it signals belonging in the community while making the vision sentence memorable. Risk: this only works if your subfield has a recognizable phrase to invert.

---

## Example 10: Pratik Chaudhari (ML)

**Verbatim:**
> "I work on understanding how the geometric structure in the space of learnable tasks enables artificial neural networks to learn efficiently."

**Decomposition:**
- *Vision compressed:* understanding geometric structure → efficient learning
- *Pattern:* Single declarative; everything is the vision

**Why it works:** in 22 words, names a specific intellectual territory ("geometric structure in the space of learnable tasks") and the consequence ("learn efficiently"). No padding; nothing wasted.

---

## Pattern Inventory (from the 10 examples)

| Pattern | Examples | Use when |
|---|---|---|
| Pure-vision (single sentence) | Ringer, Cutkosky (s1), Chaudhari | You have a memorable, compressed vision |
| Vision-then-method | Milano, Racordon | You want to signal both vision and technical reach |
| Gap-then-vision | Marcus, Hariharan | The gap is itself a strong observation |
| Compressed (one sentence carries everything) | Westrick | You have an economical phrasing |
| Vision-with-literary-hook | Adams | Your subfield has a recognizable phrase to invert |

## What All 10 Have in Common

1. **First-person**: "I" or "My research" within the first sentence (or in two cases, as the first word).
2. **No autobiography**: zero childhood references; no formative-experience narratives.
3. **No definitions**: none open with "Computer science is..." or "Machine learning has..."
4. **No declarations of feeling**: no "passionate", "fascinated", "love".
5. **Specific subfield language**: PL terms, ML terms, systems terms — the reader is assumed to be field-literate.
6. **Compressed**: all 10 are ≤2 sentences for the core vision; most are 1.
7. **Falsifiable in spirit**: each vision could be argued against by a reviewer with different research taste — the signal of a real claim, not boilerplate.
