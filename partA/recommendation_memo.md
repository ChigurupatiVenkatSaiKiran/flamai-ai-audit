# A4 Recommendation Memo

**To**: FlamAI Leadership  
**From**: AI Team Intern Candidate  
**Re**: Indic language serving cost — correcting REPORT_v0  
**Date**: September 2026  

---

## Bottom Line

REPORT_v0's "Hindi costs 6× more to serve than English" is wrong. The correct evidence-based figure, with a proper multilingual tokenizer and the right metric, is **~2.1× for Hindi and Tamil, ~6.5× for Kannada** (the latter is real — Kannada is highly agglutinative and needs a specialized model). The 6× number for Hindi is mostly a tokenizer artifact.

## What REPORT_v0 Got Wrong

Three compounding bugs in `fertility.py` (all measured in `audit_fertility.py`):

| Error | Measured Impact |
|-------|----------------|
| `split(" ")` instead of `split()` | +1.41% inflation on eng, +2.01% on hin |
| Mean-of-ratios aggregation | ~1% overestimate, biases cross-language ratio |
| GPT-2 tokenizer for Indic scripts | Wastes 55% extra tokens on Hindi, 72% on Tamil |
| tok/word as cross-language denominator | "word" encodes 3-5× more meaning in Indic — denominator is not comparable |

**Corrected numbers** (from `corrected_fertility.py` on 200-250 sentences per language):

| lang | GPT-2 tok/sent | mGPT tok/sent | Cost ratio vs eng (mGPT) |
|------|---------------|--------------|--------------------------|
| eng  | 28.4          | 30.0         | 1.0× baseline            |
| hin  | 143.3         | 64.4         | **2.15×**                |
| kan  | 253.5         | 195.3        | **6.51×** (real — needs specialized model) |
| tam  | 239.4         | 67.0         | **2.23×**                |

*Caveat: Wikipedia corpus (formal register, long sentences). Production chat traffic will have lower absolute values but similar ratios.*

## Recommendations

1. **Switch tokenizer immediately**: Replace GPT-2 with mGPT or ai4bharat/IndicBERT before any Indic traffic analysis. This alone reduces Hindi token overhead by 55% and Tamil by 72%.

2. **Use tok/sentence for routing budget**: One user turn = one response = one sequence. tok/sentence directly maps to GPU cost per request. tok/word must never be used cross-linguistically.

3. **Budget 2.1–2.2× for Hindi/Tamil serving, ~6.5× for Kannada**: The 6× estimate in REPORT_v0 applies to Kannada specifically (due to high agglutination) — not to Hindi. Over-provisioning Hindi by 3× wastes infrastructure budget.

4. **Instrument 1% live traffic**: Wikipedia sentences average 18-30 words; production chat averages 3-8 words. Get real production fertility before procurement decisions.

5. **Fix the throughput number**: REPORT_v0's "1,600 tok/s per L4" counts prefill tokens. True generation-only goodput at peak (batch=24, long prompts) = **~201 tok/s**. Fleet sizing should use generation tok/s.

6. **Retract the deck's conclusions before action**: The 5.89× and "scale linearly" claims will lead to 8× underprovisioning on serving capacity if acted upon.
