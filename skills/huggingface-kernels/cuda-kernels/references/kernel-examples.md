# Extracted Artifacts

> Version pins (CUDA toolkit, GPU architectures, package versions) in this file reflect the state when it was written. Verify against current toolchain docs before relying on them.

## Contents

- [Code and output listings](#code-and-output-listings)

## Code and Output Listings

## RMSNorm

## RoPE

## AdaLN

## GEGLU

## Attention

## Integration

## Benchmarking


```bash
# Benchmark with optimized kernels (6% end-to-end speedup)
python generate_video.py --use-optimized-kernels

# Benchmark baseline with torch.compile (34% speedup)
python generate_video.py --no-optimized-kernels --compile

# Compare configurations (note: --compile and --use-optimized-kernels are mutually exclusive)
python generate_video.py --use-optimized-kernels && \
python generate_video.py --no-optimized-kernels --compile
```

```python
from kernels import get_kernel

# Load optimized activation kernels
activation = get_kernel("kernels-community/activation", version=1)

# Use the kernel
y = torch.empty_like(x)
activation.gelu_fast(y, x)
```
| Library | Supported Models | Key Kernels |
|---------|------------------|-------------|
| **diffusers** | LTX-Video, Stable Diffusion, FLUX, DiT | RMSNorm, GEGLU, RoPE, AdaLN |
| **transformers** | LLaMA, Mistral, Qwen, Falcon | RMSNorm, Attention |
| GPU | Compute Capability | Guide |
|-----|-------------------|-------|
| H100 | sm_90 | [h100-optimization-guide.md](h100-optimization-guide.md) |
| A100 | sm_80 | [a100-optimization-guide.md](a100-optimization-guide.md) |
| T4 | sm_75 | [t4-optimization-guide.md](t4-optimization-guide.md) |

```bash
# Full benchmark with all options
python scripts/benchmark_example.py \
    --use-optimized-kernels \
    --compile \
    --batch-size 1 \
    --num-frames 161 \
    --height 512 \
    --width 768 \
    --steps 50 \
    --warmup-iterations 2
```
| Option | Default | Description |
|--------|---------|-------------|
| `--use-optimized-kernels` | auto | Use custom H100 CUDA kernels |
| `--no-optimized-kernels` | - | Use baseline implementation |
| `--compile` | false | Enable torch.compile on transformer |
| `--batch-size` | 1 | Number of videos per prompt |
| `--num-frames` | 161 | Number of frames to generate |
| `--height` | 512 | Video height in pixels |
| `--width` | 768 | Video width in pixels |
| `--steps` | 50 | Denoising steps |
| `--warmup-iterations` | 2 | Warmup runs before benchmark |
| Configuration | Time (s) | it/s | Speedup | Notes |
|:---|:---:|:---:|:---:|:---|
| Baseline (no compile) | 2.87 | 12.58 | 1.00x | Reference |
| **Optimized Kernels** | 2.70 | 13.52 | **1.06x** | 6% faster |
| Baseline + torch.compile | 2.14 | 19.05 | 1.34x | 34% faster |
| Shape | Custom (ms) | PyTorch (ms) | Speedup |
|:---|:---:|:---:|:---:|
| [1×1024×2048] | 0.019 | 0.065 | **3.37x** |
| [2×1024×2048] | 0.024 | 0.073 | **3.04x** |
| [4×1024×2048] | 0.036 | 0.093 | **2.58x** |
| [2×4096×3072] | 0.087 | 0.208 | **2.41x** |
| [4×4096×3072] | 0.157 | 0.392 | **2.49x** |

```
.claude/skills/cuda-kernels/
├── scripts/
│   ├── benchmark_example.py              # End-to-end video generation benchmark
│   ├── benchmark_rmsnorm.py              # Isolated RMSNorm micro-benchmark
│   ├── ltx_kernel_injection_example.py   # Minimal diffusers integration (~150 lines)
│   ├── transformers_injection_example.py # Minimal transformers integration (~120 lines)
│   └── huggingface_kernels_example.py    # HuggingFace Kernels Hub integration
├── references/
│   ├── diffusers-integration.md          # Complete diffusers integration guide
│   ├── transformers-integration.md       # Complete transformers integration guide
│   ├── huggingface-kernels-integration.md # HuggingFace Kernels Hub (get_kernel) guide
│   ├── troubleshooting.md                # Common issues and solutions
│   ├── kernel-templates.md               # CUDA kernel templates (includes vectorized)
│   ├── h100-optimization-guide.md        # H100 (Hopper) optimization deep dive
│   ├── a100-optimization-guide.md        # A100 (Ampere) optimization deep dive
│   └── t4-optimization-guide.md          # T4 (Turing) optimization deep dive
└── SKILL.md                              # This file

examples/ltx_video/                  # Complete working example
├── kernel_src/
│   └── rmsnorm.cu                  # Vectorized RMSNorm kernel (2.67x faster)
├── torch-ext/                      # PyTorch bindings
├── generate_video.py               # Full benchmark script
├── benchmark_rmsnorm.py            # Isolated kernel benchmark
└── setup.py                        # pip install -e .
```
| Spec | Value | Optimization Impact |
|------|-------|---------------------|
| SMs | 132 | Grid sizing: aim for multiples of 132 |
| Threads/SM | 2048 | Max 16 blocks of 128 threads per SM |
| Shared Memory | 192 KB/SM | Large tiles possible |
| L2 Cache | 50 MB | Reuse across blocks |
| Memory BW | 3.35 TB/s | Coalesced access critical |
| Warp Size | 32 | All reductions use warp shuffles |
| Spec | H100 | A100 | T4 |
|------|------|------|-----|
| SMs | 132 | 108 | 40 |
| Memory BW | 3.35 TB/s | 2.0 TB/s | 320 GB/s |
| Shared Mem/SM | 192 KB | 164 KB | 64 KB |
| BF16 Support | Yes | Yes | **No (FP16 only)** |
| Compute Cap | sm_90 | sm_80 | sm_75 |

```cuda
// Load 2 bfloat16 elements at once (32-bit load)
const __nv_bfloat162* vec_input = reinterpret_cast<const __nv_bfloat162*>(row_input);

#pragma unroll 4
for (int i = tid; i < vec_hidden; i += stride) {
    __nv_bfloat162 v = vec_input[i];
    float v0 = __bfloat162float(v.x);
    float v1 = __bfloat162float(v.y);
    sum_sq += v0 * v0 + v1 * v1;
}
```

```cuda
template <typename T>
__device__ __forceinline__ T warp_reduce_sum(T val) {
    #pragma unroll
    for (int offset = 16; offset > 0; offset >>= 1) {
        val += __shfl_xor_sync(0xffffffff, val, offset);
    }
    return val;
}
```

```toml
[general]
name = "ltx_kernels"
backends = ["cuda"]

[kernel.your_kernel]
backend = "cuda"
src = ["kernel_src/your_kernel.cu"]
cuda-capabilities = ["9.0"]
```

```python
from kernels import get_kernel, has_kernel

# Check availability and load
if has_kernel("kernels-community/activation"):
    activation = get_kernel("kernels-community/activation", version=1)

    # Use the kernel
    x = torch.randn((4, 4), dtype=torch.float16, device="cuda")
    y = torch.empty_like(x)
    activation.gelu_fast(y, x)
```

```python
from transformers import AutoModelForCausalLM
from ltx_kernels import rmsnorm

def patch_rmsnorm(model):
    for name, module in model.named_modules():
        if 'RMSNorm' in type(module).__name__:
            eps = getattr(module, 'variance_epsilon', None) or getattr(module, 'eps', 1e-6)
            def make_forward(mod, epsilon):
                def forward(x):
                    return rmsnorm(x, mod.weight, eps=epsilon)
                return forward
            module.forward = make_forward(module, eps)

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", torch_dtype=torch.bfloat16)
patch_rmsnorm(model)
```

```python
has_weight = hasattr(module, 'weight') and module.weight is not None
if has_weight:
    output = rmsnorm(x, module.weight, eps=eps)
else:
    weight = torch.ones(x.shape[-1], device=x.device, dtype=x.dtype)
    output = rmsnorm(x, weight, eps=eps)
```

```python
from diffusers import LTXPipeline
from ltx_kernels import rmsnorm

def patch_rmsnorm_modules(model):
    """Patch all RMSNorm modules to use custom kernel."""
    for name, module in model.named_modules():
        if type(module).__name__ == 'RMSNorm':
            eps = getattr(module, 'eps', 1e-6)
            has_weight = hasattr(module, 'weight') and module.weight is not None

            if has_weight:
                def make_forward(mod, epsilon):
                    def forward(x):
                        return rmsnorm(x, mod.weight, eps=epsilon)
                    return forward
                module.forward = make_forward(module, eps)
            else:
                def make_forward(epsilon):
                    def forward(x):
                        w = torch.ones(x.shape[-1], device=x.device, dtype=x.dtype)
                        return rmsnorm(x, w, eps=epsilon)
                    return forward
                module.forward = make_forward(eps)

# Usage
pipe = LTXPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.bfloat16)
pipe.to("cuda")
patch_rmsnorm_modules(pipe.transformer)
pipe.enable_model_cpu_offload()
```

```python
import torch

@torch.library.custom_op("ltx_kernels::rmsnorm", mutates_args={"out"})
def rmsnorm(out: torch.Tensor, input: torch.Tensor, weight: torch.Tensor, eps: float) -> None:
    ops.rmsnorm_forward(out, input.contiguous(), weight.contiguous(), eps)

@rmsnorm.register_fake
def _(out, input, weight, eps):
    pass  # No shape changes
```
