# Part C — Decision Memo: Casual/Conversational Indic Replies

**To**: FlamAI Product & Engineering  
**Recommendation**: Option (c) Prompt-engineering first, gate to (a) SFT if it fails  
**Constraint summary**: 1× A100-80GB, 2 weeks, 1 reviewer (Hindi+Kannada only, 10h/week), launch in 3 weeks, no external API budget

---

## Assumptions

1. The main model is FLM-4B-Instruct (from bench/model_spec.md), already deployed.
2. "Casual" means reduced formality register — fewer Sanskrit/Urdu loanwords, shorter sentences, colloquial particles (e.g. "yaar", "na", "re") — not dialect shift.
3. The reviewer can label "formal / acceptable / casual" at ~30 examples/hour (conservative for nuanced register judgment).
4. A "casual" SFT dataset requires roughly 500–2,000 high-quality examples per language to move register at 4B scale (literature: MiniChat, Orca, etc.).
5. Telugu, Bengali, Marathi cannot be reviewer-validated (reviewer covers Hindi+Kannada only) — those languages would ship with prompt-only or be delayed.

---

## Back-of-Envelope Arithmetic

### Option (a) — SFT on synthetic "casualized" pairs

**Data**: Generate ~1,000 (formal, casual) pairs per language × 6 languages = 6,000 examples. Use the main model to generate formals, prompt-engineer casuals, reviewer validates Hindi+Kannada only.

- Reviewer capacity: 10h/week × 2 weeks = 20h total × 30 examples/hour = **600 validated examples** (Hindi+Kannada only). The other 4 languages are unreviewed synthetic — **a quality risk**.
- Training: FLM-4B on A100-80GB. LoRA fine-tune at batch=32, 3 epochs over 6,000 examples ≈ **~2–3 hours** of A100 time. Technically fast.
- Iteration: 1 training run + eval + reviewer review = ~3 days. You get ~3–4 iterations in 2 weeks.
- **Risk**: 4 out of 6 languages have no human review. Synthetic-to-synthetic training risks register collapse ("the model learns to sound like what it thinks casual is"). Telugu/Bengali/Marathi not coverable by reviewer = blind deployment.

### Option (b) — Small (≤1B) rewriter model

- Need to train or fine-tune a 1B rewriter on FLM-4B outputs → casual rewrites.
- Same data bottleneck as (a) but adds inference-time latency (~150–300ms on A100 for 1B model per response) and doubles serving complexity.
- A100-80GB can run both FLM-4B (7.82 GB fp16) and a 1B rewriter (2 GB fp16) simultaneously — technically feasible.
- But: rewriter trained on same synthetic data = same quality risk as (a), with added latency. Dominated by (a) on quality and (c) on simplicity.
- **Skip unless (a) produces strong results first.**

### Option (c) — Prompt-engineering only

- Zero training cost. Iteration time: write prompt → generate 50 examples → reviewer rates → refine → repeat.
- Reviewer rates 30/hour: 50 examples = ~1.7h per iteration. 10h/week = ~6 iterations/week.
- In 2 weeks: **~12 prompt iterations** with full Hindi+Kannada reviewer feedback.
- For Telugu/Bengali/Marathi: can be deployed based on prompt transfer + automated n-gram register metrics (no reviewer needed).
- **Risk**: prompt-only may not shift register strongly enough for deeply formal base models. Risk is measurable on day 1.

---

## Recommendation: Start (c), Gate to (a) by Day 5

| Day | Action |
|-----|--------|
| 1–2 | Write and test 3 system prompt variants for casual Hindi+Kannada. Reviewer scores 50 examples each (150 total, ~5h). |
| 3 | Measure success metric. If prompt passes threshold → scale to all 6 languages with prompt. |
| 4–5 | **Kill criterion check** (see below). If prompt fails → pivot to (a): begin synthetic data generation. |
| 6–14 | If pivoting to SFT: 2 LoRA runs with reviewer validation on Hindi+Kannada. Deploy Telugu/Bengali/Marathi with prompt-only pending future reviewer. |

**Why (c) first**: 2 weeks to launch means no time to recover from a bad SFT run. Prompt-engineering gives feedback in hours, not days. If it works — ship in week 1. If it fails — you have evidence to justify the SFT cost AND you've already collected 150 reviewer-labeled examples useful for SFT training.

---

## Success Metric

**Primary**: Reviewer casual-register score ≥ 3.5/5 on a 5-point scale ("1=very formal, 5=very casual") on a held-out 50-example set, for both Hindi and Kannada independently.

**Secondary** (automated, for Telugu/Bengali/Marathi): Formality classifier score — fraction of responses containing ≥1 colloquial marker per language (language-specific list, maintainable without reviewer).

**Threshold**: ≥ 3.5/5 on reviewer scale AND ≤ 10% degradation on existing task-accuracy benchmark (to confirm casualizing doesn't break helpfulness).

---

## Kill Criterion

> **By end of Day 5**: If the best prompt variant scores < 3.0/5 on reviewer scale across all 3 prompt iterations tested, AND the score improvement per iteration is < 0.2/5 (plateau signal), **abandon prompt-only and pivot to SFT (option a)**.

Rationale: a plateau at < 3.0 means the base model's formal training distribution cannot be overridden with system prompts alone. This is detectable in 5 days — leaving 9 days for a LoRA SFT run.

---

## Day-1 Experiment

**Experiment**: Write a 3-way A/B/C prompt test:
- (A) Baseline: no system prompt modification
- (B) Explicit register instruction: "Reply in casual, everyday Hindi. Use common spoken words, avoid formal Sanskrit terms. Sound like you're texting a friend."
- (C) Few-shot: same instruction + 3 example (formal → casual) in-context pairs

Generate 20 Hindi + 20 Kannada responses per variant (120 total) on a fixed set of 20 user queries. Reviewer rates all 120 in ~4h (their first session). This gives a signal on whether register shift is achievable with prompts before committing to any compute.

**Expected result**: (C) > (B) > (A) by ≥0.5 points. If (C) < 3.0, trigger kill criterion planning immediately.

---

## The One Production Monitor

**Metric to watch**: Human CSIM (casual similarity) score on 10 randomly sampled live responses per language per day, reviewed by the native speaker on an ongoing basis. Threshold: maintain ≥ 3.5/5 rolling 7-day average. If it drops below 3.0 on any language, investigate prompt drift (model update, context window overflow) before assuming the approach has failed.
