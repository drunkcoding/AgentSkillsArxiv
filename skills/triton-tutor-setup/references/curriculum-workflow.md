# Curriculum Mode — Triton Learning Path Workflow

> Generate a 6-topic Triton StudyVault from scratch. No source files required.
> All vault output MUST stay within CWD.

## Topic Slugs (fixed canonical names)

These slugs must be used consistently in folder names, tags, frontmatter, and concept-file filenames in the paired `triton-tutor` skill:

| Slug | Display Name | Folder |
|------|--------------|--------|
| `triton-basics` | Triton Basics | `01-Triton-Basics/` |
| `tiling-autotuning` | Tiling & Autotuning | `02-Tiling-Autotuning/` |
| `matmul-patterns` | Matmul Patterns | `03-Matmul-Patterns/` |
| `attention-reductions` | Attention & Reductions | `04-Attention-Reductions/` |
| `compiler-internals` | Compiler Internals | `05-Compiler-Internals/` |
| `ecosystem-production` | Ecosystem & Production | `06-Ecosystem-Production/` |

## Phase TU1: Pre-flight

Use `AskUserQuestion` to determine:

1. **Target hardware** — NVIDIA Ampere (sm_80, A100/RTX 30) / NVIDIA Hopper (sm_90, H100) / NVIDIA Blackwell (sm_100, B200) / NVIDIA Ada (sm_89, RTX 40) / AMD MI250 (CDNA2) / AMD MI300 (CDNA3) / Intel PVC / mixed. This selects which backend-specific features (WGMMA, TMA, MFMA) are emphasized.
2. **Prior knowledge** — none / PyTorch user / wrote a CUDA kernel / shipped Triton in prod / ML researcher only. Skip-or-emphasize toggle per topic.
3. **Audience language** — for prose only (technical identifiers always English).
4. **Scope** — all 6 topics / subset (let them deselect).
5. **Focus-of-day** — optional "I am preparing for X" (e.g., writing a FlashAttention variant, optimizing an Inductor codegen path, porting Triton to AMD) — adjusts milestone selection.

Persist answers in the dashboard frontmatter:
```yaml
target_hardware: hopper
prior_knowledge: pytorch-user
audience_language: en
scope: [triton-basics, tiling-autotuning, matmul-patterns, attention-reductions]
focus: flash-attention-author
```

## Phase TU2: Topic Plan

Construct the prereq DAG. Use the canonical chain:

- `triton-basics` → `tiling-autotuning`
- `triton-basics` → `matmul-patterns`
- `tiling-autotuning` ↔ `matmul-patterns` (peer; matmul kernels canonically use autotune)
- `tiling-autotuning` → `attention-reductions`
- `matmul-patterns` → `attention-reductions`
- `attention-reductions` → `compiler-internals` (need real fused kernels to motivate IR digging)
- `attention-reductions` → `ecosystem-production` (FA/Inductor are the canonical prod consumers)
- `compiler-internals` ↔ `ecosystem-production` (peer; tooling and runtime considerations interact)

If the user deselected topics in TU1, prune the DAG but keep cross-link annotations.

## Phase TU3: Tag Standard

Registry (English kebab-case, present to user for approval before use):

| Tag Category | Examples | Rule |
|--------------|----------|------|
| Topic | `#topic-triton-basics`, `#topic-tiling-autotuning`, `#topic-matmul-patterns`, `#topic-attention-reductions`, `#topic-compiler-internals`, `#topic-ecosystem-production` | Exactly one per concept note (the owning topic). |
| Concept | `#concept-program-id`, `#concept-mask-load`, `#concept-pid-swizzling`, `#concept-online-softmax`, `#concept-ttgir-layout`, `#concept-inductor-codegen` | One or more. Detail tags MUST co-attach the parent topic tag. |
| Milestone | `#milestone-vector-add`, `#milestone-tiled-matmul`, `#milestone-flash-attention-v1`, `#milestone-ir-dump` | On hands-on milestone notes. |
| Pitfall | `#pitfall-mask-without-other`, `#pitfall-autotune-cache-thrash`, `#pitfall-num-stages-mismatch` | On pitfall index entries. |
| Backend | `#backend-nvidia`, `#backend-amd`, `#backend-intel` | When a concept is backend-specific. |
| Architecture | `#sm-80`, `#sm-90`, `#sm-100`, `#cdna3`, `#arch-ampere`, `#arch-hopper`, `#arch-mi300` | When a concept is arch-gated. |
| IR Stage | `#ir-source`, `#ir-ttir`, `#ir-ttgir`, `#ir-llir`, `#ir-ptx`, `#ir-amdgcn` | On compiler-internals notes. |

## Phase TU4: Vault Structure

```
StudyVault/
├── 00-Dashboard/
│   ├── MOC.md
│   ├── Prereq-DAG.md
│   ├── Glossary.md
│   ├── Quick-Reference.md
│   └── Pitfall-Index.md
├── 01-Triton-Basics/
├── 02-Tiling-Autotuning/
├── 03-Matmul-Patterns/
├── 04-Attention-Reductions/
├── 05-Compiler-Internals/
├── 06-Ecosystem-Production/
└── 99-Exercises/
```

Per-topic folder skeleton (created per topic in TU6):

```
0N-<TopicName>/
├── Overview.md             # 1-page summary + concept ladder
├── Concepts/
│   ├── <concept-1>.md
│   ├── <concept-2>.md
│   └── ...
├── Milestones.md           # Hands-on milestones with success criteria
├── Pitfalls.md             # Common mistakes (fold callouts)
└── Resources.md            # Authoritative URLs, papers, code samples
```

## Phase TU5: Dashboard

### `00-Dashboard/MOC.md` (required)

Per the dashboard template in [templates.md](templates.md), with these Triton-specific sections:

- **Curriculum Order** table — 6 rows, one per topic, with status checkbox and links to `Overview.md`.
- **Prereq DAG** — link to `Prereq-DAG.md` plus inline ASCII diagram.
- **Hardware Target** — pulled from frontmatter (set in TU1).
- **Backend Target** — NVIDIA / AMD / Intel; affects emphasis on `wgmma`/`mma.sync` vs `mfma`.
- **Recommended Order** — explicit "If you are a PyTorch user with no kernel experience: start at 1. If you know CUDA and want to write FlashAttention: jump to 4 after 1+3." narrative.
- **Tag Index** with the categories from TU3.

### `00-Dashboard/Prereq-DAG.md`

The ASCII DAG plus per-edge justification (1 sentence each):

> Triton Basics → Matmul Patterns: matmul kernels are the canonical 2D-tile use case for `tl.load` + `tl.dot`; without ownership of `tl.program_id`, `tl.arange`, and `tl.make_block_ptr` the matmul tutorial is opaque.

### `00-Dashboard/Glossary.md`

Terms that recur across topics: program, block, tile, warp, CTA, `tl.constexpr`, autotune, `num_warps`, `num_stages`, persistent kernel, split-K, online softmax, layout encoding, TTIR/TTGIR, Inductor. One row per term with the topic that "owns" it.

### `00-Dashboard/Quick-Reference.md`

Triton-specific reference: peak FLOPS table by GPU and dtype (A100/H100/B200/MI300), `tl.dot` operand shape constraints per backend, max `BLOCK_SIZE` ranges per dtype, autotune env vars, common compiler env vars (`TRITON_INTERPRET`, `TRITON_CACHE_DIR`, `TRITON_KERNEL_DUMP`, `MLIR_ENABLE_DUMP`). Pulled from `topic-triton-basics.md` and `topic-compiler-internals.md` resources.

### `00-Dashboard/Pitfall-Index.md`

Aggregated pitfalls from all 6 topics. One table:

| Pitfall | Topic | Severity | → Note |
|---------|-------|----------|--------|
| `tl.load` without `other=` on masked lanes | Triton Basics | 🔥 | `[[01-Triton-Basics/Pitfalls#mask-without-other]]` |

## Phase TU6: Per-Topic Notes (LAZY-LOADED)

> **CRITICAL**: load `references/topic-{slug}.md` ONLY when you start authoring that topic. Author the entire topic folder, then drop the reference from working memory before reading the next topic file. Never pre-load all 6.

For each topic, in canonical order:

1. **Read** `references/topic-<slug>.md`.
2. **Create** `0N-<TopicName>/Overview.md` containing:
   - Topic description (2-3 sentences).
   - Concept ladder table (Beginner / Intermediate / Advanced / Expert rows from the reference file).
   - "What you should know before starting" — prereqs section from the reference file.
   - "Where this leads" — cross-links to dependent topics.
3. **Create** one concept note per major concept in the Concepts column of the ladder. Use the concept note template from [templates.md](templates.md). Concept notes MUST include:
   - `source: triton-docs` or specific URL from the reference file's Authoritative URLs section.
   - Comparison table (e.g., for `tl.load` with vs without `other=`).
   - At least one ASCII diagram or code snippet for flow/hierarchy/kernel-shape concepts.
   - `## Related Notes` with `[[wiki-links]]` to peer concepts in the same topic and to the topic's predecessors/successors.
4. **Create** `0N-<TopicName>/Milestones.md` from the reference file's Hands-On Milestones section. For each milestone:
   - **Success criteria** (specific, measurable — e.g., ">90% of cuBLAS FP16 throughput on M=N=K=4096" not "is fast").
   - **Estimated effort** (≤1h / half-day / multi-day).
   - **Verification command** when applicable (e.g., `python bench.py --kernel=matmul`, `TRITON_KERNEL_DUMP=1 python kernel.py`, `proton --hook=triton python bench.py`).
5. **Create** `0N-<TopicName>/Pitfalls.md` — one fold callout per pitfall (`> [!warning]- <Pitfall>`).
6. **Create** `0N-<TopicName>/Resources.md` — authoritative URLs from the reference file, plus links to existing skills in this repo when relevant:
   - For Triton Basics & Matmul Patterns → also link to existing `cuda-tutor` topic-cuda-kernels and topic-cutlass for analogous CUDA concepts.
   - For Compiler Internals → link to `cuda-tutor-setup/references/topic-cutlass.md` (analogous to CuTe-DSL → Tile-IR comparison).

## Phase TU7: Hands-On Milestones (cross-topic exercises)

Create `99-Exercises/` notes that intentionally span 2+ topics:

- **`Autotuned-Matmul-Bench.md`** — implement tiled matmul + autotune + benchmark against cuBLAS (topics 1+2+3).
- **`FlashAttention-Forward-from-Scratch.md`** — minimal FA-2 forward in Triton with online softmax (topics 1+3+4).
- **`Dump-and-Read-TTGIR.md`** — pick a matmul kernel, dump TTGIR with `MLIR_ENABLE_DUMP=1`, identify the `#mma` layout and convert_layout ops (topics 3+5).
- **`torch.compile-Inspect-Generated-Kernel.md`** — compile a small PyTorch model with `torch.compile`, locate the Inductor-generated Triton kernel, modify and recompile (topics 1+6).

Each cross-topic exercise note links back to the relevant per-topic concept notes.

## Phase TU8: Pitfall Notes

Already created per topic in TU6. Verify they all appear in the Dashboard `Pitfall-Index.md`.

## Phase TU9: Interlinking + Self-Review

1. Verify every concept note has `## Related Notes` populated.
2. Verify every `Overview.md` has cross-links per the prereq DAG.
3. Verify Dashboard MOC links to every concept note.
4. Run the **Curriculum Mode** section of [quality-checklist.md](quality-checklist.md). Fix and re-verify until all checks pass.
5. Report to user: vault location, topic count, total concept-note count, suggested next step (run `triton-tutor`).
