---
topic: cuda-kernels
concept: cp-async
source: CUDA C++ Programming Guide §B.27
hardware: sm_80+
keywords: cp.async, commit_group, wait_group, pipeline
---

# cp.async (test fixture)

#topic-cuda-kernels #concept-cp-async

`cp.async` enables Ampere+ asynchronous global-to-shared copies. The 4/8/16-byte
per-thread variants are issued with `cp.async.ca.shared.global` and tracked via
`cp.async.commit_group` / `cp.async.wait_group(N)`.
