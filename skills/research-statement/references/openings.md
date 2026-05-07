# Opening Paragraphs

The first 4–6 sentences decide whether the rest of the document gets read. Subfield-distant committee members skim; only paragraph 1 is read carefully.

## The Four-Job Opening Checklist

Every opening paragraph must do all four, in any order, in 4–6 sentences:

1. **Name the problem domain** with non-trivial framing (not a textbook definition).
2. **Name the gap or tension** that animates your work — what existing approaches miss.
3. **State the vision** in one bold, falsifiable-in-spirit sentence.
4. **Hint at the method/tools** you bring to the gap.

A good opening passes a final test: a colleague in your subfield should recognize it as a real problem; a non-specialist should be able to paraphrase the vision sentence after one read.

## 10 Successful Opening Paragraphs (Verbatim)

These are public, real, faculty-search openings that resulted in tenure-track CS jobs. Patterns extend to other disciplines.

1. **Mae Milano (PL × Distributed Systems):** *"My research focuses on building new systems and designing new language abstractions to make programming at scale feasible for more people, without sacrificing performance, correctness, or expressive power in the process."* — names domain, names gap (scale + correctness + performance pulled in different directions), states vision (new abstractions), hints at method (language design).

2. **Sam Westrick (PL / Parallelism):** *"To address the difficulty of parallel programming, my goal is to raise the level of abstraction at which programmers can achieve high performance."* — economical: gap → vision in one sentence.

3. **Ryan Marcus (ML for Database Systems):** *"From database query optimizers to garbage collectors, today's computer systems are composed of hand-tuned heuristics. These off-the-shelf heuristics are convenient and freely available, but are optimized for a 'general purpose' case, and thus do not maximize system performance for most actual applications."* — names a counter-intuitive observation, sets up the gap before the vision arrives.

4. **Talia Ringer (Verification):** *"My long-term goal as a researcher is to make it easy for programmers of all skill levels across all domains to build formally verified software systems."* — pure vision sentence; method comes in paragraph 2.

5. **Bharath Hariharan (Computer Vision):** *"Behind the exceptional abilities of modern computer vision models are millions of hours of human labor in annotation. I therefore seek to build learning-based computer vision systems that can learn from very limited data."* — names the hidden cost behind a successful field, then turns it into the vision.

6. **Ashok Cutkosky (ML / Optimization):** *"I am broadly interested in making machine learning more about engineering and less about intuition and guesswork."* — research taste compressed to one sentence.

7. **Jan Paul (Verification / Type Theory):** *"As systems grow more intricate, our ability to ensure their correctness and reliability faces significant challenges. Traditional verification methods, rooted in testing and manual inspection, struggle to keep pace with the exponential growth in system complexity and state spaces."* — gap is named precisely with stakes.

8. **Dimi Racordon (PL):** *"My research advances methods and techniques that empower developers to write expressive, efficient, and reliable software. I gravitate toward model checking, formal verification, and programming language design, with a particular focus on advanced type systems."* — vision + methods in two sentences.

9. **Michael D. Adams (PL):** *"My research vision is for programmers to be able to communicate their intent to a computer (i.e., write programs) as quickly as and at the same high level that they can communicate to other programmers and that the resulting software artifacts would be clear enough that they obviously have no bugs instead of having no obvious bugs."* — uses Hoare echo for memorable phrasing; vision is precise enough to be falsifiable.

10. **Pratik Chaudhari (ML):** *"I work on understanding how the geometric structure in the space of learnable tasks enables artificial neural networks to learn efficiently."* — single declarative sentence; nothing wasted.

## Pattern Inventory

Opening patterns that work across disciplines:

| Pattern | Template | Example above |
|---|---|---|
| Pure-vision | "My long-term goal is to [X]." | Ringer, Cutkosky, Chaudhari |
| Gap-then-vision | "Today's [X] suffers from [gap]. My research [vision]." | Marcus, Hariharan |
| Vision-then-method | "My research advances [vision]. I work on [methods]." | Milano, Racordon |
| Compressed | One declarative sentence carrying domain + gap + vision. | Westrick |
| Counter-intuitive observation | Surprising fact about the field, then the vision it implies. | Hariharan, Marcus |

## Anti-Patterns (Block on Sight)

Listed by frequency, with diagnosis.

| Anti-pattern | Why it fails | Replacement |
|---|---|---|
| "Ever since I was a child, I have been fascinated by..." | Irrelevant; not believable; reads as filler. | Open with the problem or the vision. |
| "Computer science is a field that..." | Definitional opening on the most expensive sentence in the document. | Assume the reader knows the field. |
| "This research is critically important to humanity." | Grandiosity without evidence. | State a specific stake. |
| "I am passionate about [field]." | Telling not showing. Indistinguishable from boilerplate. | Show via specific work / question. |
| Opening with a question. | Reads as soft, indirect, or rhetorical. | Make a claim. |
| Opening with a Turing-quote / Asimov-quote. | Distracts from your voice. Earns no points. | Skip. |
| "In recent years, machine learning has..." | Trend-following intro. Aging instantly. | Specific gap, not a trend. |
| "I am writing to express my interest in..." | This is a cover letter sentence, not a research statement. | Delete; start with vision. |

## The "Self-Sufficient First Paragraph" Test

After writing the opening, run this test:

> Read only paragraph 1. Close the document. Write down: (a) the candidate's research vision in one sentence; (b) one method they use; (c) one stake / consequence of the work.

If you cannot fill in all three from paragraph 1 alone, the opening is incomplete.

## Calibration to Length

| Length cap | Opening allocation | Notes |
|---|---|---|
| 1 page | ~3–4 sentences | Pure-vision or compressed pattern only |
| 2 pages | ~4–6 sentences (≈10–15% of length) | Gap-then-vision works well |
| 3 pages | 1 paragraph (~120–150 words) | Can use vision-then-method |
| 4–5 pages | 1–2 paragraphs (~200–250 words) | Allow a second framing paragraph |
| 7–10 pages (humanities) | 1–2 paragraphs introducing the book project | Different conventions; see discipline_variants.md |
