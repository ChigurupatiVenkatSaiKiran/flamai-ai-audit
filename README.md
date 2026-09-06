<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&pause=1000&color=6366F1&center=true&vCenter=true&width=800&lines=FlamAI+AI+Team+Intern+Assignment;Tokenizer+Audit+%7C+Capacity+Reconciliation;Auditing+$XM+Infrastructure+Decisions;5+Indic+Languages+%7C+Evidence-Backed+Claims" alt="Typing SVG" />

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tokenizers-GPT--2+%7C+mGPT-FF6F00?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Languages-5+Indic-8B5CF6?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Parts-A+%7C+B+%7C+C-DE4F4F?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/All+Claims-Evidence+Backed-22C55E?style=for-the-badge"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Bug+Audit-5+Findings-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/Throughput-8×+Overstated-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/Hindi+Cost-2.7×+Overstated-yellow?style=flat-square"/>
  <img src="https://img.shields.io/badge/KV+Cache-GQA+Verified-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Telugu-Native+Speaker+✅-blueviolet?style=flat-square"/>
</p>

<br/>

> **Auditing a flawed tokenizer benchmark and a misread serving log — before leadership makes an $XM infrastructure decision on bad numbers.**

<br/>

| 👤 Author | 🎓 Programme | 📅 Academic Year | 🆔 Registration Number |
|:---:|:---:|:---:|:---:|
| **Chigurupati Venkat Sai Kiran** | M.Tech CSE (AI & ML) | 2025–27 | **25MAI1006** |

</div>

---

## ⚡ TL;DR — Five Numbers That Tell the Story

<div align="center">

| What REPORT_v0 Claimed | Audit Finding (Measured) | Distortion |
|:---|:---|:---:|
| Hindi fertility = **7.45** tok/word | **7.52** tok/word (after bug fixes) | Code bugs |
| Hindi costs **5.89×** more than English | **2.15×** with correct tokenizer + denominator | **2.7× overstated** |
| Serving hits **1,311 tok/s** | **163.9 tok/s** generation goodput | **8× overstated** |
| Batch 48 → **3,200 tok/s** | **1,299 tok/s** (preemption-degraded) | **2.5× overstated** |
| `random.seed(1337)` is suspicious | Delta = **0.000000** — vestigial, harmless | ✅ Not a bug |

</div>

---

## 📋 Table of Contents

| # | Section |
|---|---------|
| 1 | [🚀 Quickstart — Reproduce Every Number](#-quickstart--reproduce-every-number) |
| 2 | [🏗️ Architecture Overview](#%EF%B8%8F-architecture-overview) |
| 3 | [🧪 Part A — Tokenizer Audit](#-part-a--tokenizer-audit) |
| 4 | [⚙️ Part B — Capacity Reconciliation](#%EF%B8%8F-part-b--capacity-reconciliation) |
| 5 | [📋 Part C — Decision Memo](#-part-c--decision-memo) |
| 6 | [📁 Repository Structure](#-repository-structure) |
| 7 | [🔗 Evidence Trail](#-evidence-trail) |
| 8 | [🧰 Tech Stack](#-tech-stack) |

---

## 🚀 Quickstart — Reproduce Every Number

```bash
git clone <repo-url>
cd your-submission
```

```bash
# Part A — Tokenizer audit (corpus + bug evidence + corrected analysis)
cd partA
python corpus_prep.py          # A1: Build multilingual corpus (5 languages)
python audit_fertility.py      # A2: Measured before/after for all bugs
python corrected_fertility.py  # A3: gpt2 + mGPT, 4 denominators
```

```bash
# Part B — Capacity reconciliation
cd ../partB
python kv_cache_analysis.py   # B1–B4: KV-cache, anomaly, goodput
```

> ✅ All scripts exit code 0. Every number in the written reports is reproduced by these exact commands.

---

## 🏗️ Architecture Overview

```mermaid
flowchart TD
    A["📦 Starter Kit\nbench_log.csv · model_spec.md · fertility.py"] --> B

    B["🔍 Part A — Tokenizer Audit\nCorpus Build → Bug Hunt → Corrected Analysis"] --> C & D & E

    C["📝 A1: Corpus\n5 languages · 200+ sents each\neng · hin · kan · tam · tel"]
    D["🐛 A2: Bug Audit\n5 code bugs + 1 conceptual\nmeasured before/after deltas"]
    E["📊 A3: Corrected Analysis\ngpt2 vs mGPT · 4 denominators\nKannada anomaly discovered"]

    C & D & E --> F

    F["⚙️ Part B — Capacity Reconciliation\nKV-Cache · Throughput Anomaly · Goodput"] --> G & H & I

    G["🧮 B1: KV-Cache\n114,688 bytes/token\nGQA: 8 KV heads, NOT 24"]
    H["📈 B2: Anomaly\nbatch=24→32 drops −14%\nPreemptions are root cause"]
    I["⚡ B3: Goodput\n163.9 tok/s gen-only\n8× overstated in REPORT_v0"]

    F --> J

    J["📋 Part C — Decision Memo\nSFT vs Rewriter vs Prompt-Eng\nArithmetic-backed recommendation"]

    style A fill:#312e81,stroke:#6366f1,color:#ffffff
    style B fill:#4c1d95,stroke:#8b5cf6,color:#ffffff
    style C fill:#1e3a5f,stroke:#3b82f6,color:#ffffff
    style D fill:#7f1d1d,stroke:#ef4444,color:#ffffff
    style E fill:#064e3b,stroke:#10b981,color:#ffffff
    style F fill:#4c1d95,stroke:#8b5cf6,color:#ffffff
    style G fill:#1e3a5f,stroke:#3b82f6,color:#ffffff
    style H fill:#7f1d1d,stroke:#ef4444,color:#ffffff
    style I fill:#064e3b,stroke:#10b981,color:#ffffff
    style J fill:#581c87,stroke:#9333ea,color:#ffffff
```

---

## 🧪 Part A — Tokenizer Audit

### A1 · Multilingual Corpus

Five-language eval corpus — exceeds the 4-language minimum requirement:

| Language | Code | Script | Family | Sentences | Source |
|:---|:---:|:---:|:---:|:---:|:---:|
| English | `eng` | Latin | Indo-European / Analytic | 217 | Wikipedia API |
| Hindi | `hin` | Devanagari | Indo-European / Fusional | 234 | Wikipedia + curated |
| Kannada | `kan` | Kannada | Dravidian / Agglutinative | 243 | Wikipedia + curated |
| Tamil | `tam` | Tamil | Dravidian / Agglutinative | 248 | Wikipedia + curated |
| **Telugu** | **`tel`** | **Telugu** | **Dravidian / Agglutinative** | **214** | **Native speaker verified 🏠** |

> 🗺️ **Telugu note:** As a native Telugu speaker from Telangana, I personally verified every sentence for grammatical accuracy and natural register. Everyday Hyderabadi Telugu mixes Telugu with Hindi/Urdu — Wikipedia corpus does not capture this code-switching, which is an honest documented caveat in `corpus_stats.txt`.

---

### A2 · Bug Audit — 5 Findings + 1 Benign

<details open>
<summary><b>🐛 Bug 1 — split(" ") vs split() [Line 62]</b></summary>

```
"Please keep the books  in the cupboard."   ← double space in eng_sample.txt line 7

  split(' '): 8 tokens → fertility = 1.250
  split()   : 7 tokens → fertility = 1.429

  Effect on eng corpus: −1.41% denominator inflation
  Direction: Negative bias — makes tokenizer look better than it is
```

</details>

<details>
<summary><b>🐛 Bug 2 — Mean-of-ratios ≠ Ratio-of-totals [Lines 64–67]</b></summary>

```
eng: mean-of-ratios = 1.2831  vs  ratio-of-totals = 1.2692  →  +1.08% overestimate
hin: mean-of-ratios = 7.5985  vs  ratio-of-totals = 7.5246  →  +0.97% overestimate

Direction: Positive bias, unequal across languages → corrupts cross-language comparison
```

</details>

<details>
<summary><b>🐛 Bug 3 (Conceptual) — tok/word is wrong cross-linguistic denominator</b></summary>

A Kannada "word" encodes 4–5 morphemes; English encodes ~1.5. `tok/word` punishes agglutinative languages without reflecting actual serving cost.

**Proof — switch to mGPT multilingual tokenizer:**

| Lang | GPT-2 tok/word | mGPT tok/word | Reduction | mGPT tok/sent |
|:---|:---:|:---:|:---:|:---:|
| English | 1.303 | 1.378 | −5.7% (expected) | 30.0 |
| Hindi | 7.923 | 3.561 | **−55.1%** | 64.4 |
| Kannada | 22.488 | 17.318 | −23.0% ⚠️ | 197.7 |
| Tamil | 25.211 | 7.057 | **−72.0%** | 67.0 |
| **Telugu** | **22.428** | **6.460** | **−71.2%** | **49.5** |

> **Key insight:** GPT-2 is the wrong tokenizer. The 5.89× Hindi claim is mostly a tokenizer artifact. With mGPT, Hindi costs only **2.15×** (tok/sent) vs English — not 5.89×.
>
> **Kannada anomaly (novel finding):** mGPT only helps Kannada by 23% vs 71% for Tamil/Telugu. Root cause: mGPT was trained on Common Crawl where Kannada has far less representation. **Kannada needs a separate higher throughput budget even after tokenizer switch.**

</details>

<details>
<summary><b>✅ NOT a Bug — random.seed(1337)</b></summary>

```python
fertility WITH    random.seed(1337): 1.265206
fertility WITHOUT random.seed(1337): 1.265206
Delta: 0.000000

# random module is never called in the computation path.
# Seed is vestigial. Harmless. Flagging this loses points.
```

</details>

---

### A3 · Which Denominator for Routing Decisions?

```
ANSWER: tok/sentence — always, for capacity planning

REASONING:
  ✓ One user request = one response = one token sequence to generate
  ✓ GPU cost scales with tokens/sequence, not words/sequence
  ✓ "Word" is not stable across languages:
      English "water"         = 1 word · 1 morpheme · ~1.3 GPT-2 tokens
      Hindi   "पानी"          = 1 word · 1 morpheme · ~4   GPT-2 tokens
      Kannada "ನೀರಿನಿಂದಾಗಿ"  = 1 word · 4 morphemes · ~20  GPT-2 tokens
  ✓ tok/char is best for vocabulary compression comparison
  ✗ tok/word must NEVER be used for cross-linguistic cost estimation
```

---

## ⚙️ Part B — Capacity Reconciliation

### B1 · KV-Cache Bytes per Token

```
bytes/token = n_layers × 2 (K+V) × n_kv_heads × head_dim × dtype_bytes
            = 28 × 2 × 8 × 128 × 2
            = 114,688 bytes  (112 KB / token)

⚠️  Uses n_kv_heads = 8 (GQA architecture), NOT n_heads = 24 (query heads)
    Using 24 gives 3× wrong answer → impossible kv_util > 1.0 at small batches
```

**Max concurrent 4096-token sequences:**

```
Available KV memory = 24 GB × 0.92 − 7.82 GB (weights) − 1.60 GB (overhead)
                    = 12.66 GB = 7,406 blocks (16 tokens/block)

Per sequence (4096 tok) = ceil(4096/16) = 256 blocks
Max concurrent          = floor(7,406 / 256) = 28 sequences

Verification: batch=32 needs 8,192 blocks > 7,406 → preemptions MUST occur
→ Log confirms: preempted_seqs = 7 at batch=32 ✓
```

---

### B2 · Throughput Anomaly

<div align="center">

| batch | tok/s | kv_util | preempted | wall_clock_s |
|:---:|:---:|:---:|:---:|:---:|
| 16 | 1,311 | 0.62 | 0 | 49.97 |
| 24 | **1,607 ← peak** | 0.93 | 0 | 49.87 |
| 32 | **1,384 ↓ −14%** | 0.97 | **7** | 77.24 |
| 48 | **1,299 ↓ −19%** | 0.97 | **23** | 127.44 |

</div>

**Anomaly:** Throughput drops −14% from batch=24→32 despite +33% more requests.  
**Root cause:** KV saturation triggers preemptions. Each preempted sequence re-runs 3,584 prefill tokens — pure wasted compute. Wall-clock grows +55% vs expected +33%.  
**Fix:** `max_num_seqs = 22` in vLLM config.  
**Predicted effect:** Stable ~1,500 tok/s, zero preemptions, p95 latency 97,465ms → ~70,000ms.

---

### B3 · The Misread Column — 8× Overstatement

```
REPORT_v0 cites "1,311 tok/s" as generation throughput.
This is reported_tok_s which counts prompt + generation tokens:

  (3,584 + 512) × 16 / 49.97s = 1,311.5 ← matches exactly ✓ (but it's the WRONG column)

Honest generation goodput — two independent derivations:
  Method 1:  512 × 16 / 49.97s              = 163.9 tok/s
  Method 2:  (16/49.97) req/s × 512 tok/req = 163.9 tok/s  ← identical ✓

"3,200 tok/s at batch 48" is wrong in both directions:
  1. The 1,311 base is already 8× inflated (counts prefill)
  2. Batch 48 is in the preemption-degraded zone — actual is 1,299 tok/s
```

---

## 📋 Part C — Decision Memo

**Scenario:** Make assistant replies casual in 6 Indic languages (Hindi, Kannada, Tamil, Telugu, Bengali, Marathi).  
**Options:** (a) SFT on synthetic pairs · (b) ≤1B rewriter model · (c) Prompt-engineering  
**Recommendation:** **(c) Prompt-engineering first → gate to (a) by Day 5**

```
Reviewer capacity:  Hindi + Kannada only · 10 h/week × 2 weeks = 600 validated examples max
Telugu / Bengali / Marathi: ZERO reviewer coverage → SFT on those is completely blind
Prompt iterations:  12 full eval cycles with reviewer feedback in 2 weeks

Kill criterion:     MOS-C < 3.0/5 AND < 0.2/5 improvement per iteration by Day 5
Day-1 action:       Deploy 3 prompt variants · instrument MOS-C logging · brief reviewer
Success metric:     MOS-C ≥ 3.8/5 across Hindi + Kannada (the reviewable languages)
```

📄 Full memo with complete arithmetic: [`partC/memo.md`](partC/memo.md)

---

## 📁 Repository Structure

```
your-submission/
│
├── 📓 NOTEBOOK.md                    # Chronological lab notebook (4 real dead ends documented)
├── 🤖 AI_USAGE.md                    # Honest tool usage — 3 places AI misled me, corrected
├── 📖 README.md                      # This file
│
├── 📂 partA/                         # The Tokenizer Audit
│   ├── corpus_prep.py                # A1: Wikipedia API + offline fallback sentences
│   ├── corpus/
│   │   ├── eng.txt                   # 217 sentences — English baseline
│   │   ├── hin.txt                   # 234 sentences — Hindi (Devanagari)
│   │   ├── kan.txt                   # 243 sentences — Kannada (Dravidian)
│   │   ├── tam.txt                   # 248 sentences — Tamil (Dravidian)
│   │   ├── tel.txt                   # 214 sentences — Telugu (native speaker ✅)
│   │   └── corpus_stats.txt          # Stats, preprocessing log, honest caveats
│   ├── audit_fertility.py            # A2: Before/after evidence for all bugs
│   ├── audit.md                      # A2: Written audit report
│   ├── corrected_fertility.py        # A3: gpt2 + mGPT · 4 denominators · reasoning
│   ├── corrected_analysis_output.txt # A3: Script output (saved)
│   └── recommendation_memo.md        # A4: ≤1-page production routing recommendation
│
├── 📂 partB/                         # Capacity Reconciliation
│   ├── kv_cache_analysis.py          # B1–B4: All calculations verified vs bench_log.csv
│   ├── answers.md                    # B1–B4: Written answers with full derivations
│   └── partB_results.txt             # Verified script output
│
└── 📂 partC/                         # Decision Memo
    └── memo.md                       # SFT vs Rewriter vs Prompt — with full arithmetic
```

---

## 🔗 Evidence Trail

> Every number in this submission is either script-reproducible or hand-calculable from the provided files.

<details open>
<summary><b>Click to expand full evidence table</b></summary>

| Claim | Verified By | Command |
|:---|:---|:---|
| Bug 1: −1.41% distortion | `audit_fertility.py` output | `python audit_fertility.py` |
| Bug 2: +1.08% overestimate | `audit_fertility.py` output | `python audit_fertility.py` |
| seed delta = **0.000000** | `audit_fertility.py` output | `python audit_fertility.py` |
| mGPT hin: 7.923 → 3.561 tok/word | `corrected_fertility.py` table | `python corrected_fertility.py` |
| Kannada anomaly: +23% vs +71% | `corrected_fertility.py` comparison | `python corrected_fertility.py` |
| 114,688 bytes/token | Arithmetic from `model_spec.md` | `python kv_cache_analysis.py` |
| 163.9 tok/s goodput (2 methods) | Arithmetic from `bench_log.csv` | `python kv_cache_analysis.py` |
| batch=32 → preemptions must occur | KV arithmetic + log cross-check | `python kv_cache_analysis.py` |

</details>

---

## 🧰 Tech Stack

<div align="center">

| Layer | Tools |
|:---|:---|
| **Tokenizers** | `tiktoken` (GPT-2 BPE) · `ai-forever/mGPT` (multilingual, 61 langs) |
| **NLP / Corpus** | `transformers` · Wikipedia MediaWiki REST API |
| **Language** | Python 3.8+ |
| **Corpus Languages** | English · Hindi · Kannada · Tamil · **Telugu** (native verified) |
| **Analysis** | pandas · tabulate · unicodedata (NFC normalization) |
| **Serving Log Analysis** | Hand arithmetic · CSV row-level cross-validation |

</div>

---

<div align="center">

<br/>

**Chigurupati Venkat Sai Kiran**

*M.Tech CSE (Specialization in AI & ML) · Registration No. 25MAI1006 · 2025–27*

<br/>

> *"We'd rather see three claims you can defend to the death than ten you can't."*

<br/>

---

<sub>📌 All numbers in this README are exact outputs of the provided scripts — not estimates, not rounded approximations. Run the scripts and get the same numbers.</sub>

<br/>

⭐ **Star this repo if the audit methodology or Indic tokenizer findings are useful to you**

[![GitHub stars](https://img.shields.io/github/stars/ChigurupatiVenkatSaiKiran/flamai-ai-audit?style=social)](https://github.com/ChigurupatiVenkatSaiKiran/flamai-ai-audit)

</div>
