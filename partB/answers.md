# Part B — Capacity Reconciliation: Written Answers

All arithmetic is implemented and verified in `kv_cache_analysis.py`.  
Run: `python kv_cache_analysis.py` to reproduce all numbers.

---

## B1 — KV-Cache Arithmetic (7 pts)

### (a) KV-cache bytes per token

From `bench/model_spec.md`:

| Parameter | Value |
|-----------|-------|
| `layers` | 28 |
| `KV heads (GQA)` | **8** (not 24 — GQA means fewer KV heads than Q heads) |
| `head_dim` | 128 |
| `KV cache precision` | fp16 = 2 bytes |

Each token stores one KEY and one VALUE vector for **every layer**:

```
bytes/token = n_layers × 2 (K+V) × n_kv_heads × head_dim × dtype_bytes
            = 28 × 2 × 8 × 128 × 2
            = 114,688 bytes
            = 112 KB per token
```

**Critical detail**: Use `n_kv_heads = 8` (GQA), NOT `attention_heads = 24` (Q heads). Using 24 would triple the estimate. GQA is the whole point of the spec listing them separately.

### (b) Maximum concurrent 4096-token sequences

```
GPU VRAM                  : 24 GB
× gpu_memory_utilization  : 0.92
= usable VRAM             : 22.08 GB
− model weights (4.2B fp16): 4.2e9 × 2 bytes = 7.82 GB
− non-KV runtime overhead : 1.60 GB
= available for KV cache  : 12.66 GB = 13,590,232,555 bytes

vLLM allocates KV cache in fixed 16-token blocks:
  block size in bytes     = 16 tokens × 114,688 bytes/token = 1,835,008 bytes
  total_blocks            = 13,590,232,555 / 1,835,008 = 7,406 blocks

For 4096-token sequences:
  blocks per sequence     = ceil(4096 / 16) = 256 blocks
  max concurrent seqs     = floor(7,406 / 256) = 28 sequences
```

### Verification against bench_log.csv

| batch | prompt+gen tokens | blocks used | blocks/7406 | reported kv_util | delta |
|-------|------------------|-------------|-------------|-----------------|-------|
| 64 (short, 768 tok) | 64 × 48 = 3,072 blocks | 3,072 | 0.41 | 0.47 | 0.06 — OK |
| 24 (long, 4096 tok) | 24 × 256 = 6,144 blocks | 6,144 | 0.83 | 0.93 | 0.10 — runtime overhead |
| 32 (long, 4096 tok) | 32 × 256 = 8,192 blocks | 8,192 | 1.11 | 0.97 | 0.14 — exceeds budget → preemptions |

The delta between calculated and reported is explained by vLLM reserving blocks for scheduler overhead, speculative decoding, and beam cache. Our formula gives the theoretical floor. The key observation: **at batch=32, our arithmetic predicts >100% utilization — confirming that preemptions must occur**, which matches `preempted_seqs=7` in the log.

---

## B2 — Throughput Anomaly (6 pts)

### Anomaly identified

Looking at long-context rows (prompt=3584, gen=512):

| batch | wall_clock_s | reported_tok_s | kv_cache_util | preempted_seqs |
|-------|-------------|----------------|---------------|---------------|
| 4 | 28.98 | 565.4 | 0.16 | 0 |
| 8 | 36.30 | 902.6 | 0.31 | 0 |
| 16 | 49.97 | 1,311.4 | 0.62 | 0 |
| 24 | 61.16 | 1,607.4 | 0.93 | 0 |
| **32** | **94.71** | **1,384.0** | **0.97** | **7** ← anomaly |
| 48 | 151.41 | 1,298.5 | 0.97 | 23 |

**Throughput drops from 1,607 (batch=24) to 1,384 (batch=32) despite adding 8 more requests** — a 14% decrease. At batch=48 it degrades further to 1,299 (-19% from peak).

### Mechanism

At batch=32, the KV cache is over-committed: 32 × 256 blocks = 8,192 needed but only 7,406 available. The vLLM scheduler must **preempt** sequences — either swapping KV blocks to CPU RAM (swap preemption) or re-running prefill from scratch (recompute preemption). Either way:

- `wall_clock_s` grows super-linearly (94.71s at batch=32 vs. expected ~73s from linear scaling from batch=24)
- Tokens that were already generated must be re-generated = wasted GPU cycles
- `preempted_seqs=7` at batch=32 and `23` at batch=48 confirm this is the scheduler preemption path

**Key evidence**: wall_clock_s from batch=16→24 grows by 22% (perfectly linear). From batch=24→32 it grows by **55%** — more than doubling the expected overhead. This superlinear jump is the signature of preemption.

### Proposed fix

**Limit `max_num_seqs=22` in the vLLM config** (safely below the 28-sequence theoretical maximum, leaving headroom for runtime overhead).

**Predicted quantitative effect**: Throughput at the new batch ceiling ≈ 1,500–1,550 tok/s (interpolating between batch=24 at 1,607 and batch=16 at 1,311), with **zero preemptions** and wall_clock_s growing linearly. This trades ~3–5% peak throughput for elimination of the ~14-19% throughput regression and latency spikes (e2e_ms_p95 = 97,465ms at batch=32 vs 69,221ms at batch=24 — a 41% latency increase that disappears with the limit set).

---

## B3 — Report Misreading (4 pts)

### The misread column: `reported_tok_s`

REPORT_v0 says "batch 16, long prompts hit 1,311 tok/s" and "assume ~1,600 tok/s per L4, scale linearly to 3,200 at batch 48."

The harness column `reported_tok_s` counts **ALL tokens processed** (prompt + generation), not just generated tokens. Verification:

```
batch=16, prompt=3584, gen=512, wall_clock=49.97s
Total tokens processed = (3584 + 512) × 16 = 65,536
65,536 / 49.97s = 1,311.5 tok/s  ← matches reported_tok_s exactly
```

Prompt tokens are **already sent by the user** — they are not tokens the system is producing. The user-visible work is only generating the 512 output tokens.

### Honest goodput — two independent methods

**Method 1 — generation tokens only**:
```
generated tokens = 512 × 16 = 8,192
goodput = 8,192 / 49.97s = 163.9 tok/s
```

**Method 2 — requests/second × gen_len**:
```
requests/second = 16 / 49.97s = 0.3202 req/s
goodput = 0.3202 × 512 = 163.9 tok/s
```

Both methods independently give **163.9 tok/s** — confirming each other.

For batch=24 (REPORT_v0's "peak"):
```
generated = 512 × 24 = 12,288
goodput = 12,288 / 61.16s = 201.0 tok/s
```

### What the report should have said

> "At batch=24 with long prompts (3584+512 tokens), generation goodput peaks at **~201 tok/s** per L4. The harness `reported_tok_s` column includes prefill tokens and overstates throughput by ~8×. Throughput does **not** scale linearly with batch — it peaks at batch=24 and degrades 14-19% at batch=32+ due to KV-cache preemptions. Batch=48 delivers ~1,299 reported tok/s (200 tok/s generation-only), not 3,200. For capacity planning, use ~200 generation tok/s per L4 at the safe operating point (batch ≤ 22)."

---

## B4 — Confirming Metric (3 pts)

**Metric**: `preempted_seqs` (or equivalently, vLLM's `Scheduler.num_preempted` counter in Prometheus).

**Why this metric**: If the throughput drop at batch=32+ is caused by KV-cache saturation and scheduler preemptions (our hypothesis), then `preempted_seqs` should jump from **0 at batch ≤ 24** to a non-zero value **exactly at the batch size where kv_cache_util exceeds ~0.93** (the empirical saturation threshold from the log).

**Expected values**:
- At batch ≤ 24 (safe zone): `preempted_seqs = 0`
- At batch = 32 (over-committed): `preempted_seqs > 0` — specifically, we expect 5–10 preemptions (observed: 7)
- At batch = 48 (severely over-committed): `preempted_seqs >> 0` (observed: 23)

The bench_log already shows this (`preempted_seqs` column). If in production we add this counter to our Grafana dashboard with an alert at `preempted_seqs_per_minute > 0`, it will fire exactly when kv_cache_util saturates — giving us real-time signal to reduce batch size or add a GPU before user-visible latency degrades.

**Complementary metric**: `e2e_ms_p95` — at batch=24 this is 69,221ms; at batch=32 it jumps to 97,465ms (+41%). This latency spike is the user-visible consequence of preemptions and provides an independent confirming signal.
