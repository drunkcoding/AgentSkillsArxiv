# Document Mode — NVIDIA-Aware Workflow

> Transform PDFs (NVIDIA whitepapers, GTC slide decks, programming guides), text, and web pages into study notes.
> All scanning and output MUST stay within CWD.

## Phase D1: Source Discovery & Extraction

1. **Auto-scan CWD** for `**/*.pdf`, `**/*.txt`, `**/*.md` (excluding `README.md` and `StudyVault/`), `**/*.html`, `**/*.epub`. Exclude `node_modules/`, `.git/`, `dist/`, `build/`.
2. **Extract text (MANDATORY tools)**:
   - **PDF → `pdftotext` CLI ONLY** (via Bash). NEVER `Read` directly on PDFs — wastes 10-50x tokens.
     ```bash
     pdftotext -layout "source.pdf" "/tmp/source.txt"
     ```
     Install if missing: `brew install poppler` (macOS) / `apt-get install poppler-utils` (Linux).
   - URLs → WebFetch.
   - `.md`/`.txt`/`.html` → Read directly.
3. **Read extracted `.txt` files** — never the raw PDFs.
4. **Source Content Mapping (MANDATORY for multi-file sources)**:
   - Read cover page + TOC + 3+ sample pages from middle/end of EVERY source file.
   - NEVER assume content from filename — `chapter5.pdf` may not be chapter 5.
   - Build `{ source_file → actual_topics → page_ranges }`. Present to user for verification.

## Phase D2: Content Analysis

1. Build topic hierarchy from the source(s).
2. Decide reorg target:
   - **If sources are NVIDIA official docs** (Programming Guide, PTX ISA, CUTLASS docs, NCCL User Guide, NVSHMEM API Guide, GTC slides on TMA/WGMMA/NVLS): **reorganize into the canonical 6-topic StudyVault structure**. This is the canonical taxonomy for this skill.
   - **If sources are unrelated CUDA-adjacent docs** (academic papers, GPU architecture surveys): preserve their natural hierarchy.
3. Map dependencies between topics.
4. Build a complete topic checklist — every topic / subtopic listed. Drives all subsequent phases.

> **Equal Depth Rule**: even briefly-mentioned subtopics get a full dedicated note supplemented with textbook-level CUDA knowledge.

5. **Source-to-note cross-verification** (MANDATORY): record source file + page range per topic.

## Phase D3: Tag Standard

Same registry as Curriculum mode (see [curriculum-workflow.md](curriculum-workflow.md) Phase CU3). When reorganizing into the 6-topic structure, reuse the same `#topic-*` tags.

## Phase D4: Vault Structure

If reorg target is the 6-topic structure → produce the canonical layout from `templates.md`. Otherwise create numbered folders per source's natural topic hierarchy.

## Phase D5: Dashboard Creation

`00-Dashboard/` with MOC + Quick Reference + Pitfall/Exam-Traps Index. Per [templates.md](templates.md).

## Phase D6: Concept Notes

Per [templates.md](templates.md). Key rules:
- YAML frontmatter: `source_pdf`, `part`, `keywords` (MANDATORY).
- `source_pdf` MUST match the verified Phase D1 mapping — never guess from filename.
- If unavailable: `source_pdf: original not available`.
- `[[wiki-links]]`, callouts, comparison tables > prose.
- ASCII diagrams for processes/flows.
- CUDA identifiers verbatim in English.

## Phase D7: Practice Questions

Per [templates.md](templates.md). Key rules:
- Every topic folder MUST have a practice file (≥8 questions).
- Active recall: answers in `> [!answer]- View Answer` fold callout (localize label to user language).
- Patterns in `> [!hint]-` / `> [!summary]-` fold callouts.
- Question type diversity: ≥60% recall, ≥20% application, ≥2 analysis per file.
- Distractors drawn from the realistic CUDA confusion pools in `cuda-tutor/references/quiz-rules.md`.

## Phase D8: Interlinking

1. `## Related Notes` on every concept note.
2. MOC links to every concept + practice note.
3. Cross-link concept ↔ practice; siblings reference each other.
4. Pitfall-Index → concept notes; bidirectional.

## Phase D9: Self-Review

Verify against [quality-checklist.md](quality-checklist.md) **Document Mode** section. Fix and re-verify until all checks pass.
