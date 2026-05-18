---
topic: cutlass
concept: cute-layout
source: CUTLASS docs/cute/00_quickstart.md
hardware: all
---

# cute::Layout (test fixture)

#topic-cutlass #concept-cute-layout

`cute::Layout` pairs a `Shape` with a `Stride`. The pair maps logical
coordinates to physical offsets. `Stride` can itself be hierarchical, enabling
column-major / row-major / swizzled / nested-tile compositions in one type.
