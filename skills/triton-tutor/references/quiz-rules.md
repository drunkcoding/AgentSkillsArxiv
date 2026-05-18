# Triton Quiz Design Rules

## Zero-Hint Policy (CRITICAL)

Every question must be answerable ONLY by someone who actually knows the Triton material.

1. **Option descriptions** NEVER reveal correctness.
   - BAD: `label: "tl.dot"`, `description: "Triton tile dot product that lowers to WGMMA on Hopper"` (definition leaks the answer)
   - GOOD: `label: "tl.dot"`, `description: "Triton language matmul primitive"`

2. **No "(Recommended)" tag** on any option.

3. **Randomize** the correct answer's position — never always first or last.

4. **Question phrasing** asks about behavior/purpose/output, not the name of the answer.
   - BAD: "Which Triton API lowers to `wgmma.mma_async` on Hopper?"
   - GOOD: "When multiplying two FP16 tiles inside a Triton kernel on H100, which language primitive does the compiler lower to Hopper warp-group MMA?"

5. **Plausible distractors** must be real Triton concepts the user could plausibly confuse with the answer (common-misconception based, not absurd).

## Triton-Specific Distractor Pools

When picking the 3 wrong options, draw from realistic confusion sets within the same topic:

| Topic | Common distractor pool (pick concepts the learner is most likely to confuse) |
|-------|------------------------------------------------------------------------------|
| Triton Basics | `tl.program_id(axis)` vs `tl.num_programs(axis)`; `tl.load(ptr, mask)` vs `tl.load(ptr, mask, other)`; pointer arithmetic vs `tl.make_block_ptr`; `tl.arange` vs Python `range`; `tl.constexpr` vs runtime arg; `tl.broadcast_to` vs implicit broadcasting; `tl.where` vs Python `if` |
| Tiling & Autotuning | `triton.Config` vs `triton.heuristics`; `num_warps` vs `num_stages`; `key=[...]` cache key vs `prune_configs_by`; `reset_to_zero` vs `restore_value`; `triton.autotune` vs `triton.jit` cache; pre-hook vs post-hook |
| Matmul Patterns | tiled GEMM pid order vs swizzled pid (`pid_m`/`pid_n` group-of-`GROUP_SIZE_M`); persistent vs non-persistent kernels; split-K vs stream-K; `tl.dot(a, b, acc)` vs `acc = tl.dot(a, b) + acc`; FP8 `tl.dot` scale args; TF32 vs FP32 accumulation |
| Attention & Reductions | online softmax vs two-pass softmax; `tl.associative_scan` vs `tl.cumsum`; FlashAttention-1 vs FlashAttention-2 vs FlashAttention-3 KV iteration order; causal mask via `tl.where` vs `tl.load` mask; block-level reduction (`tl.sum`) vs warp-level shuffle |
| Compiler Internals | TTIR vs TTGIR vs LLIR; layout encodings (`#blocked` vs `#mma` vs `#shared` vs `#dot_op`); `triton-opt` vs `triton-translate`; coalescing pass vs swizzling pass; PTX vs SASS; cuBLAS-style template specialization vs Triton JIT autotuning |
| Ecosystem & Production | `torch.compile` Inductor codegen vs hand-written Triton; AOT (`triton.compile`) vs JIT; `proton` profiler vs Nsight Compute; FBGEMM/xformers/flash-attn vs raw Triton kernels; CUDA Graphs + Triton; `TRITON_INTERPRET=1` vs PTX dump |

## Question Types

1. **Factual recall** — "What does `tl.program_id(axis=0)` return?"
2. **Conceptual understanding** — "Why does pid swizzling improve L2 hit rate in matmul kernels?"
3. **Behavioral prediction** — "What happens when an autotune config has `num_stages=3` but the kernel has no pipelined load?"
4. **Comparison / distinction** — "What is the difference between `tl.constexpr` and a regular kernel argument?"
5. **Debugging scenario** — "Given this `tl.load(ptr, mask)` without `other=`, what does an out-of-bounds element contain?"

## Difficulty Balancing

- **Diagnostic** session: 40% easy, 40% medium, 20% hard.
- **Weak-area drill**: 30% medium, 70% hard.
- **Curriculum-order** session: difficulty matches the topic's place in the chain (foundation = mostly medium; advanced = mostly hard).
- **Hard-mode review**: 100% hard.
- **Cross-topic** drill: at least 1 of the 4 questions probes the interaction (e.g., autotune config interaction with `num_stages` pipelining lowering in TTGIR).

## Drilling Unresolved 🔴 Concepts

When targeting 🔴 concepts from concept files:
- Do NOT repeat the literal previous question.
- Test the same underlying knowledge from a different angle: change the GPU backend (NVIDIA Ampere → Hopper → AMD MI300), change the API surface (`@triton.jit` vs `triton.compile` AOT vs `torch.compile` Inductor), or change the failure scenario.
- Example: previous miss on `tl.dot` operand layout for FP16 → next question asks about the **accumulator layout** for FP8 `tl.dot` on Hopper with `acc_dtype=tl.float32`.

## AskUserQuestion Format

- 4 questions per round, 4 options each, single-select.
- Header: max 12 chars, format `Q1. <tag>` (e.g., `Q1. ProgID`, `Q2. Autotune`, `Q3. Swizzle`, `Q4. TTGIR`).
- Option labels: 1–5 words, preferably the actual Triton identifier (`tl.program_id`, `triton.autotune`, `tl.dot`, `num_stages`).
- Option descriptions: ≤1 sentence, neutral, no give-away.

## File Update Protocol

After grading:
1. Update `concepts/{topic}.md` — add/update concept rows + error notes.
2. Update the dashboard — recalculate topic stats from the concept files.
3. Badges: 🟥 0-39% · 🟨 40-69% · 🟩 70-89% · 🟦 90-100% · ⬜ no data.

## Topic Attribution Rule

If a question spans multiple topics, attribute it to the topic that owns the **primary mechanism** being tested:
- "How does the autotuner pick between `BLOCK_SIZE_M=64` and `BLOCK_SIZE_M=128` for a given matmul shape?" → Tiling & Autotuning (matmul is the mechanism used, but the question tests autotuner cache-key logic; the dual-attribution rule below applies).
- "What does `tl.dot(a, b, acc)` compute?" → Matmul Patterns.
- Dual-attribution (optional): when a question genuinely tests both, write the concept row in BOTH topic files with the same `Concept` text so progress tracks in both. Mark dual-attributed concepts with a trailing `(↔ {other-topic})` in the concept name.

## Language Rule

All prose (question text, descriptions, explanations, file body) in the user's detected `{LANG}`. **Always** preserve the following verbatim in English regardless of `{LANG}`:
- Triton language identifiers: `tl.load`, `tl.store`, `tl.dot`, `tl.program_id`, `tl.num_programs`, `tl.arange`, `tl.constexpr`, `tl.where`, `tl.associative_scan`, `tl.cumsum`, `tl.sum`, `tl.max`, `tl.exp`, `tl.make_block_ptr`, `tl.advance`.
- Decorators / drivers: `@triton.jit`, `@triton.autotune`, `@triton.heuristics`, `triton.Config`, `triton.compile`.
- Tuning knobs: `BLOCK_SIZE_M`, `BLOCK_SIZE_N`, `BLOCK_SIZE_K`, `GROUP_SIZE_M`, `num_warps`, `num_stages`.
- IR layers: `TTIR`, `TTGIR`, `LLIR`, `PTX`, `AMDGCN`, `#blocked`, `#mma`, `#shared`, `#dot_op`.
- Ecosystem tools: `torch.compile`, Inductor, `proton`, `TRITON_INTERPRET`, `TRITON_CACHE_DIR`.

Badge emojis (🟥🟨🟩🟦⬜) and ✅/❌ are universal.
