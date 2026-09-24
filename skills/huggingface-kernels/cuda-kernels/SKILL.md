---
name: cuda-kernels
description: "Provides guidance for writing and benchmarking optimized CUDA kernels for NVIDIA GPUs (H100, A100, T4) targeting HuggingFace diffusers and transformers libraries. Supports models like LTX-Video, Stable Diffusion, LLaMA, Mistral, and Qwen. Includes integration with HuggingFace Kernels Hub (get_kernel) for loading pre-compiled kernels. Includes benchmarking scripts to compare kernel performance against baseline implementations. Use for kernel types: attention, rmsnorm, rope, adaln, geglu, benchmark, transformers, diffusers, huggingface-kernels, get_kernel."
allowed-tools: "Read, Grep, Glob, Bash"
---

# CUDA Kernels for Diffusers & Transformers

This skill covers optimized CUDA kernels for HuggingFace diffusers and transformers on H100, A100, and T4 GPUs. The complete per-kernel examples for attention, RMSNorm, RoPE, AdaLN, and GEGLU are preserved in [the kernel examples reference](references/kernel-examples.md).

## Workflow

1. Choose the target model, library, GPU, dtype, and kernel type.
2. Start from the matching kernel example and architecture guide.
3. Build with Nix or pip/uv, then integrate through the diffusers or transformers patching pattern.
4. Inject kernels before CPU offloading and handle model-specific RMSNorm weights and GELU versus GEGLU differences.
5. Benchmark optimized kernels against PyTorch and torch.compile baselines.
6. Profile with Nsight Systems or Nsight Compute and resolve integration issues before claiming speedups.

Supported model families include LTX-Video, Stable Diffusion, FLUX, DiT, LLaMA, Mistral, Qwen, and Falcon. H100 uses sm_90, A100 sm_80, and T4 sm_75. BF16 isn't supported on T4.

## Benchmarking

```bash
python scripts/benchmark_example.py \
    --use-optimized-kernels \
    --batch-size 1 \
    --num-frames 161 \
    --height 512 \
    --width 768 \
    --steps 50 \
    --warmup-iterations 2
```

Compare `--use-optimized-kernels` with `--no-optimized-kernels --compile`, but don't combine the two flags. Capture GPU, precision, resolution, frame count, warmup, and iteration settings with every result. Isolated RMSNorm benchmarks and the full benchmark option matrix are in the reference.

## Integration Rules

Use `get_kernel` for precompiled HuggingFace Kernels Hub modules when appropriate. For diffusers, handle RMSNorm modules whose weight is `None`, match module types by name where necessary, patch before `enable_model_cpu_offload()`, and remember that LTX-Video uses GELU rather than GEGLU. For transformers, account for `variance_epsilon` versus `eps` and always pass RMSNorm weights.

## Build and Profile

```bash
nix run .#build-and-copy --max-jobs 2 --cores 8 -L
uv pip install -e .
nsys profile -o profile python your_script.py
ncu --set full -o metrics python your_script.py
```

Custom kernels and `torch.compile` are mutually exclusive unless registered as PyTorch custom ops. The reference retains the custom-op pattern and troubleshooting details.
