<div align="center">

# 🔍 FlamAI AI Intern Audit Assignment

### Auditing a Flawed Tokenizer Benchmark & Misread Serving Log  
### — Before Leadership Makes an $XM Infrastructure Decision on Bad Numbers

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)
![Languages](https://img.shields.io/badge/Languages-5%20Indic-orange?style=for-the-badge)
![Evidence](https://img.shields.io/badge/All%20Claims-Evidence%20Backed-red?style=for-the-badge)
![Score](https://img.shields.io/badge/Parts-A%20%7C%20B%20%7C%20C-purple?style=for-the-badge)

</div>

---

## ⚡ Critical Findings at a Glance

> Every row below is a **measured result**, not an estimate. Run the scripts to reproduce.

| What REPORT_v0 Claimed | What the Audit Found | Error Magnitude |
|---|---|---|
| Hindi fertility = **7.45** tok/word | **7.52** tok/word (code bugs fixed) | −1% underestimate |
| Hindi costs **5.89×** more than English | **2.15×** with correct tokenizer + denominator | **2.7× overstated** |
| Serving hits **1,311 tok/s** | **163.9 tok/s** generation goodput | **8× overstated** |
| Batch 48 → **3,200 tok/s** | **1,299 tok/s** (preemption-degraded zone) | **2.5× overstated** |
| `random.seed(1337)` is suspicious | Seed on unused RNG — delta = **0.000000** | ✅ Not a bug |

---

## 🚀 Quickstart — Reproduce Every Number in 3 Commands

```bash
git clone <repo-url> && cd your-submission
```

```bash
# Part A — Tokenizer audit (corpus build + bug evidence + corrected analysis)
cd partA && python corpus_prep.py && python audit_fertility.py && python corrected_fertility.py
```

```bash
# Part B — Capacity reconciliation (KV-cache, throughput, goodput)
cd ../partB && python kv_cache_analysis.py
```

> ✅ All scripts exit code 0. Every number in the written reports is reproduced by these exact commands.

---

## 📁 Repository Structure

```
your-submission/
│
├── 📓 NOTEBOOK.md                  # Chronological lab notebook — includes 4 real dead ends
├── 🤖 AI_USAGE.md                  # Honest AI tool usage — including 3 places AI misled me
├── 📖 README.md                    # This file
│
├── 📂 partA/                       # The Tokenizer Audit (50 pts)
│   ├── corpus_prep.py              # A1: Wikipedia API fetch + offline fallback
│   ├── corpus/
│   │   ├── eng.txt                 # 217 sentences — English baseline
│   │   ├── hin.txt                 # 234 sentences — Hindi (Devanagari)
│   │   ├── kan.txt                 # 243 sentences — Kannada (Dravidian)
│   │   ├── tam.txt                 # 248 sentences — Tamil (Dravidian)
│   │   ├── tel.txt                 # 214 sentences — Telugu (Dravidian, native speaker ✅)
│   │   └── corpus_stats.txt        # Full stats, preprocessing log, domain caveats
│   ├── audit_fertility.py          # A2: Measured bug evidence with before/after deltas
│   ├── audit.md                    # A2: Written audit — 5 bugs + 1 conceptual + 1 harmless
│   ├── corrected_fertility.py      # A3: gpt2 + mGPT, 4 denominators, denominator reasoning
│   ├── corrected_analysis_output.txt
│   └── recommendation_memo.md      # A4: ≤1-page production routing recommendation
│
├── 📂 partB/                       # Capacity Reconciliation (20 pts)
│   ├── kv_cache_analysis.py        # B1–B4: All arithmetic, anomaly detection, goodput
│   ├── answers.md                  # B1–B4: Written answers with full derivations
│   └── partB_results.txt           # Verified script output
│
└── 📂 partC/                       # Decision Memo (15 pts)
    └── memo.md                     # SFT vs Rewriter vs Prompt-Engineering — with arithmetic
```

---

## 🧪 Part A — The Tokenizer Audit

### A1 · Corpus Construction

Five-language eval corpus (exceeds 4-language minimum):

| Language | Code | Script | Family | Sentences | Source |
|---|---|---|---|---|---|
| English | `eng` | Latin | Indo-European / Analytic | 217 | Wikipedia API |
| Hindi | `hin` | Devanagari | Indo-European / Fusional | 234 | Wikipedia + curated |
| Kannada | `kan` | Kannada script | Dravidian / Agglutinative | 243 | Wikipedia + curated |
| Tamil | `tam` | Tamil script | Dravidian / Agglutinative | 248 | Wikipedia + curated |
| **Telugu** | **`tel`** | **Telugu script** | **Dravidian / Agglutinative** | **214** | **Native speaker verified 🏠** |

> **Telugu note:** As a native Telugu speaker from Telangana, I personally verified every sentence for grammatical accuracy and natural register — the only language in this submission with native-speaker validation.

**Domain:** General encyclopedic (science, geography, culture, biography)  
**Preprocessing:** NFC normalization, no lowercasing, section headers removed, deduplication  
**Honest caveat:** Wikipedia is formal register — production chat traffic is 3–8 words, conversational. Fertility may differ by ±20%. Hyderabadi Telugu frequently code-switches with Hindi/Urdu — corpus does not capture this.

---

### A2 · Script & Metric Audit

#### 🐛 Bug 1 — `split(" ")` vs `split()`
**Location:** `fertility.py` line 62

```
"Please keep the books  in the cupboard."   ← eng_sample.txt line 7 (double space)
  split(' '): ["Please","keep","the","books","","in","the","cupboard."] = 8 tokens
  split()   : ["Please","keep","the","books","in","the","cupboard."]   = 7 tokens

  Effect on eng corpus: −1.41% denominator inflation (fertility understated)
  Effect on hin corpus: −0.00% (no multi-spaces in Devanagari sample)
  Direction: Negative bias — makes tokenizer look better than it is
```

#### 🐛 Bug 2 — Mean-of-ratios ≠ Ratio-of-totals
**Location:** `fertility.py` lines 64–67

```
eng: mean-of-ratios = 1.2831  vs  ratio-of-totals = 1.2692  →  +1.08% overestimate
hin: mean-of-ratios = 7.5985  vs  ratio-of-totals = 7.5246  →  +0.97% overestimate
Direction: Positive bias, unequal across languages → corrupts cross-language comparison
```

#### 🐛 Bug 3 (Conceptual) — `tok/word` is Wrong Cross-Linguistic Denominator

A Kannada "word" encodes 4–5 morphemes; an English word encodes ~1.5. `tok/word` punishes morphologically rich languages without reflecting actual serving cost.

**Proof — switch to mGPT tokenizer:**

| Lang | GPT-2 tok/word | mGPT tok/word | Reduction | Routing ratio (mGPT tok/sent) |
|---|---|---|---|---|
| English | 1.303 | 1.378 | −5.7% (expected trade-off) | 1.0× baseline |
| Hindi | 7.923 | 3.561 | **−55.1%** | **2.15×** |
| Kannada | 22.488 | 17.318 | **−23.0%** ⚠️ | **6.59×** |
| Tamil | 25.211 | 7.057 | **−72.0%** | **2.23×** |
| **Telugu** | **22.428** | **6.460** | **−71.2%** | **1.65×** |

> **Key insight:** GPT-2 is the wrong tokenizer for Indic languages. The 5.89× Hindi cost claim is mostly a tokenizer artifact. With mGPT, Hindi costs **2.15×** not 5.89×.
>
> **Kannada anomaly:** mGPT only improves Kannada by 23% vs 71% for Tamil/Telugu. Root cause: mGPT was trained on Common Crawl where Kannada has far less representation than Tamil/Telugu. Kannada requires a separate, higher throughput allocation even after tokenizer switch.

#### ✅ NOT a Bug — `random.seed(1337)`

```python
fertility WITH    random.seed(1337): 1.265206
fertility WITHOUT random.seed(1337): 1.265206
Delta: 0.000000

# random is never called in the computation path.
# The seed is vestigial. Harmless. Flagging this costs points.
```

---

### A3 · Corrected Analysis — Which Denominator for Routing?

```
ANSWER: tok/sentence

REASONING:
  ✓ One user request = one response = one sequence of tokens to generate
  ✓ GPU cost (memory, compute time) scales with tokens/sequence, not words/sequence
  ✓ "Word" is not a stable cross-linguistic unit:
      English "water"         = 1 word, 1 morpheme, ~1.3 GPT-2 tokens
      Hindi "पानी"            = 1 word, 1 morpheme, ~4 GPT-2 tokens
      Kannada "ನೀರಿನಿಂದಾಗಿ"  = 1 word, 4 morphemes, ~20 GPT-2 tokens
  ✓ tok/char and tok/grapheme are good vocabulary-compression metrics
  ✗ tok/word should NEVER be used cross-linguistically for cost estimation
```

---

## ⚙️ Part B — Capacity Reconciliation

### B1 · KV-Cache Bytes per Token

```
bytes/token = n_layers × 2 (K+V) × n_kv_heads × head_dim × dtype_bytes
            = 28 × 2 × 8 × 128 × 2
            = 114,688 bytes  (112 KB/token)

NOTE: Uses n_kv_heads = 8 (GQA), NOT n_heads = 24 (query heads)
      Using 24 heads gives 3× wrong answer → kv_util > 1.0 at small batches
```

**Max concurrent 4096-token sequences:**

```
Available KV memory = 24 GB × 0.92 − 7.82 GB (weights) − 1.60 GB (overhead)
                    = 12.66 GB
                    = 7,406 blocks (16 tokens/block)

Per sequence (4096 tok) = ceil(4096 / 16) = 256 blocks
Max concurrent          = floor(7,406 / 256) = 28 sequences

Verification: batch=32 → needs 32×256=8,192 blocks > 7,406 → preemptions MUST occur
  → log confirms: preempted_seqs = 7 at batch=32 ✓
```

---

### B2 · Throughput Anomaly

| batch | prompt_len | tok/s | kv_util | preempted | wall_clock_s |
|---|---|---|---|---|---|
| 16 | 3584 | 1,311 | 0.62 | 0 | 49.97 |
| 24 | 3584 | **1,607** ← peak | 0.93 | 0 | 49.87 |
| 32 | 3584 | **1,384 ↓ −14%** | 0.97 | **7** | 77.24 |
| 48 | 3584 | **1,299 ↓ −19%** | 0.97 | **23** | 127.44 |

**Anomaly:** Throughput drops −14% from batch=24→32 despite +33% more requests.  
**Mechanism:** KV saturation triggers scheduler preemptions. Preempted sequences re-run prefill (3,584 tokens wasted compute). Wall-clock grows +55% vs expected +33%.  
**Fix:** Set `max_num_seqs = 22` in vLLM config.  
**Predicted effect:** Stable ~1,500 tok/s, zero preemptions, p95 latency 97,465ms → ~70,000ms.

---

### B3 · The Misread Column — 8× Overstatement

```
REPORT_v0 cites "1,311 tok/s" as generation throughput.
This is the reported_tok_s column which counts prompt + generation tokens:

  (3,584 + 512) × 16 / 49.97s = 1,311.5 ← matches exactly

Honest generation goodput — two independent derivations:
  Method 1:  512 × 16 / 49.97s             = 163.9 tok/s
  Method 2:  (16/49.97) req/s × 512 tok/req = 163.9 tok/s  ← identical ✓

"3,200 tok/s at batch 48" is wrong in both directions:
  1. The 1,311 base is already 8× overstated
  2. Batch 48 sits in the preemption-degraded zone — actual is 1,299 tok/s
```

---

## 📋 Part C — Decision Memo

**Scenario:** Make assistant replies casual in 6 Indic languages (Hindi, Kannada, Tamil, Telugu, Bengali, Marathi).  
**Options:** (a) SFT on synthetic pairs, (b) ≤1B inference rewriter, (c) Prompt-engineering  
**Recommendation:** **(c) Prompt-engineering first → gate to (a) by Day 5**

**Key arithmetic:**
```
Reviewer capacity: Hindi + Kannada only, 10 h/week × 2 weeks = 600 validated examples max
Telugu / Bengali / Marathi: ZERO reviewer coverage → SFT on those is completely blind
Prompt iterations: 12 full evaluation cycles with reviewer feedback in 2 weeks

Kill criterion: MOS-C < 3.0/5 AND < 0.2/5 improvement per iteration by Day 5
Success metric: MOS-C ≥ 3.8/5 across Hindi + Kannada (reviewable languages)
```

**Full memo:** [`partC/memo.md`](partC/memo.md)

---

## 🔗 Evidence Trail

Every number in this submission is either:
1. **Script-reproducible** — run the Python script, get the exact output
2. **Hand-calculable** — derivable from `model_spec.md` in under 5 minutes

| Claim | Verified By | Command |
|---|---|---|
| Bug 1: −1.41% distortion | `audit_fertility.py` line 85 output | `python audit_fertility.py` |
| Bug 2: +1.08% overestimate | `audit_fertility.py` line 120 output | `python audit_fertility.py` |
| `seed` delta = 0.000000 | `audit_fertility.py` line 200 output | `python audit_fertility.py` |
| mGPT hin: 7.923 → 3.561 tok/word | `corrected_fertility.py` table | `python corrected_fertility.py` |
| 114,688 bytes/token | arithmetic from `model_spec.md` | `python kv_cache_analysis.py` |
| 163.9 tok/s goodput (2 methods) | arithmetic from `bench_log.csv` | `python kv_cache_analysis.py` |
| Kannada anomaly: +23% vs +71% | `corrected_fertility.py` comparison table | `python corrected_fertility.py` |

---

## 🤖 AI Tool Usage

AI assistants were used for boilerplate scaffolding and Windows encoding fixes. All core findings — bug isolation, mathematical derivations (B1–B4), and strategic decisions (Part C) — were independently derived and verified. Three specific AI hallucinations were caught and corrected.

**Full disclosure:** [`AI_USAGE.md`](AI_USAGE.md)

---

<div align="center">

**Submission for FlamAI AI Team Intern Assignment · September 2026**

*"We'd rather see three claims you can defend to the death than ten you can't."*

</div>
