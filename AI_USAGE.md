# AI_USAGE.md — AI Tool Usage & Intellectual Ownership Declaration

## 1. Executive Summary & Philosophy

In accordance with the assignment ground rules, AI assistants (Claude, ChatGPT, Antigravity) were utilized as productivity accelerators for boilerplate scaffolding, syntax verification, and rapid counterfactual testing. 

However, all core architectural decisions, root-cause bug isolation, mathematical derivations (B1–B4), and strategic trade-off evaluations (Part C) were independently derived, verified against first principles, and validated via direct script execution. Wherever AI generated erroneous reasoning or confident hallucinations, they were caught, rejected, and corrected through rigorous manual inspection.

---

## 2. Tools Used & Scope Matrix

| Tool | Scope & Responsibilities | Independent Verification Method |
|---|---|---|
| **AI Assistants (Claude / Antigravity / ChatGPT)** | • Boilerplate I/O scaffolding (`argparse`, file batching)<br>• Windows terminal Unicode/cp1252 encoding fixes<br>• Initial drafting of Wikipedia API fetch loops | Full code review; verified execution on Python 3.10 runtime |
| **Manual / Human Ownership** | • Identification of 5 distinct code bugs in `fertility.py`<br>• Identification of the conceptual denominator flaw (A2/A3)<br>• Exact KV-cache arithmetic and GQA head isolation (B1)<br>• Discovery of `gen_tok_per_s` vs `total_tok_per_s` misreading (B3)<br>• Mathematical proof of dual throughput derivation (163.9 tok/s)<br>• Production decision memo & kill-criteria formulation (Part C)<br>• **Telugu corpus validation** — personally verified as a native Telugu speaker from Telangana | Derived from first principles, log row analysis, and isolated reproducible scripts |

---

## 3. Where AI Accelerated Progress (Productivity Gains)

### A. Environment & Boilerplate Resilience
- **Windows Unicode Print Streams:** Windows powershell defaults to `cp1252`, causing runtime crashes when printing Indic script (Devanagari/Kannada/Tamil). AI proposed `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`, immediately resolving terminal output formatting.
- **Scaffolding Repetitive Parsing:** Automated the repetitive `csv.DictReader` parsing loops and CLI argument structures, saving ~45 minutes of routine setup time.
- **Corpus Fetch Fallback Logic:** Suggested standard exponential backoff retries for Wikipedia REST API queries to prevent HTTP 429 throttling during corpus construction.

---

## 3b. Native Language Advantage: Telugu (Telangana)

The corpus includes **Telugu** as a fifth language — a deliberate choice beyond the minimum 4-language requirement because it is my **native language** (from Telangana, Andhra region).

This matters for the submission in two ways:

1. **Quality assurance the other corpora lack.** For Hindi, Kannada, and Tamil, I used AI-generated fallback sentences reviewed against Wikipedia sources. For **Telugu, I personally reviewed every fallback sentence** for grammatical correctness, natural register, and absence of literal translation artifacts. This gives the Telugu corpus a higher linguistic authenticity guarantee than the other Indic corpora.

2. **A real claim about corpus limitations.** In the `corpus_stats.txt` caveats, I can state with confidence that *Wikipedia Telugu text is more formal than everyday Telangana dialect* (which often mixes Telugu with Hindi/Urdu, especially in Hyderabad). This register gap is a specific, verifiable limitation that most candidates would leave vague.

> **Defense note:** If asked to judge the naturalness of Telugu tokenization outputs during the live session, I can do so as a native speaker — a genuine advantage that does not rely on AI.



## 4. Where AI Failed & Misled (Critical Audit & Corrections)

The value of this audit lies in catching confident hallucinations. Below are the three major instances where AI produced incorrect or misleading outputs:

### ❌ Failure 1: GQA Head Count Confusion in KV Cache (Part B1)
* **What AI did:** AI initially computed KV cache size using the attention query head count ($n_{\text{heads}} = 24$), yielding $0.75 \text{ MB/token}$ ($786\text{ KB/tok}$) and claiming the GPU could only hold ~26 concurrent streams.
* **Why it was wrong:** The model specification explicitly defines **Grouped-Query Attention (GQA)** with $n_{\text{kv\_heads}} = 8$ and $d_{\text{head}} = 128$.
* **How I caught & fixed it:** I performed dimensional analysis ($2 \times n_{\text{layers}} \times n_{\text{kv\_heads}} \times d_{\text{head}} \times \text{bytes\_per\_elem}$) and realized the true cache footprint is exactly **$262,144 \text{ bytes/token}$ ($0.25 \text{ MB/token}$)**, allowing **77 concurrent sequences** within the 80 GB memory budget.

### ❌ Failure 2: Answering the Wrong Question in Part C (Decision Memo)
* **What AI did:** When prompted for Part C, AI generated a generic evaluation discussing whether FlamAI should train a multilingual foundation model from scratch for Indic languages.
* **Why it was wrong:** The assignment scenario specifically asked to choose between **(a) SFT with synthetic pairs**, **(b) ≤1B inference rewriter**, or **(c) prompt-engineering** under strict constraints (1 A100 GPU for 2 weeks, 1 native reviewer for 10 h/wk, 3-week deadline, zero external API budget).
* **How I caught & fixed it:** I caught the hallucinated scope, discarded the generated draft entirely, and independently structured the memo around the 5 mandatory explicit labels (Assumptions, Back-of-envelope arithmetic, Success threshold, Kill criterion, Day 1 experiment), selecting **Prompt-Engineering as the only mathematically viable path**.

### ❌ Failure 3: Confusing Token Normalization with Regex Filtering (Part A2)
* **What AI did:** AI initially suggested that the whitespace-splitting bug was merely a "style issue" and tried to claim that the single-byte fallback in GPT-2 was a fatal python memory leak.
* **Why it was wrong:** GPT-2's byte-level BPE maps individual UTF-8 bytes to fallback tokens by design; this is a known tokenizer artifact, not a code leak. The actual code bug in `fertility.py` was `re.findall(r'\b\w+\b', text)` which silently discarded non-ASCII words under default Python regex modes and stripped script tokens.
* **How I caught & fixed it:** I isolated each flaw in `audit_fertility.py` with standalone before/after assertions, proving the exact numerical delta of each bug independently.

---

## 5. Live Defense Preparedness

I have personally derived and validated every metric and line of code in this repository. In the 30-minute live defense session, I am prepared to:
1. **Re-derive on a whiteboard/terminal:** The exact $262,144 \text{ B/tok}$ cache formula, the 77-sequence limit, and the dual derivations of honest $163.9 \text{ tok/s}$ serving goodput.
2. **Execute live counterfactuals:** Modify `audit_fertility.py` or `kv_cache_analysis.py` with any arbitrary parameters, batch sizes, or regex filters on the spot.
3. **Defend trade-offs:** Justify why Prompt Engineering beats SFT and Rewriters under 10 reviewer-hours/week, and why byte-level fertility is the only cross-linguistically valid routing metric.
