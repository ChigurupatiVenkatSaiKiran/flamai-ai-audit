# AI_USAGE.md — AI Tool Usage Declaration

## Tools Used

| Tool | Role in this submission |
|------|------------------------|
| AI coding assistant (Antigravity/Claude) | Code scaffolding, boilerplate, Windows encoding fixes |
| Claude (reasoning) | Stress-testing arguments, especially Bug 3 denominator logic |
| AI text generation | Curated fallback sentences for Hindi, Kannada, Tamil corpora |

---

## Where AI Helped

### Code
- **Boilerplate I/O**: `argparse`, file read/write loops, `subprocess.check_call` for auto-installing `tiktoken`. I could have written these but AI saved ~30 minutes.
- **Windows encoding**: AI suggested `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` to fix cp1252 crashes on Unicode print statements. I would have eventually found this; AI got me there in 30 seconds.
- **Retry/backoff logic**: The exponential backoff pattern in `corpus_prep.py` came from an AI suggestion, reviewed and adapted by me.

### Reasoning (used carefully)
- I asked AI to steelman my Bug 3 argument ("tok/word is wrong denominator"). It pointed out that my first tok/sentence numbers (hin=143 vs eng=28) actually looked *worse* than tok/word, not better — which helped me sharpen the argument to correctly emphasize the tokenizer artifact (GPT-2 vs mGPT) rather than just the denominator.

### Indic Language Sentences
- The 70-80 curated fallback sentences per language (Hindi, Kannada, Tamil) were generated with AI assistance. I reviewed them against Wikipedia sources and they are grammatically standard prose, but I am not a native speaker of any Indic language. **This is a real limitation of my submission** — the sentences may not capture colloquial register variation correctly.

---

## Where AI Misled Me

### Part C — Wrong Question (Biggest Failure)
AI wrote my initial Part C memo as "should FlamAI deploy FLM-4B for Indic languages" — answering the wrong question entirely. The actual Part C asks about casualizing Indic replies (SFT vs rewriter vs prompt-engineering). I caught this on a re-read of the assignment, but only after the memo was written. **I rewrote Part C from scratch without AI involvement.** Lesson: AI confidently answers *a* question, not necessarily *your* question.

### KV Head Count
AI initially calculated KV cache using Q heads (24) instead of KV heads (8). I caught this when the kv_util numbers came out impossibly large (>1.0 for small batches). The model_spec.md explicitly lists them separately — the bug was in not carefully reading which row to use.

### Bug 3 Initial Framing
AI initially framed Bug 3 as "tok/sentence is fairer than tok/word" — but when I ran the numbers, Indic tok/sentence ratios were still very high (143×, 253×) due to the formal Wikipedia corpus. This would have undermined the argument in the audit. I revised to correctly emphasize (a) GPT-2 is the wrong tokenizer, and (b) mGPT reduces the ratio by 55-72%.

---

## What I Can Defend Fully

Every number in the submission is either:
1. Directly reproduced by running a script (`python audit_fertility.py`, `python kv_cache_analysis.py`)
2. Hand-calculated arithmetic that I can rederive in the defense from model_spec.md

I can re-run any script live, modify it for counterfactuals, and explain the derivation of every number. The one area I'd flag in defense: the Indic curated sentences — I used AI to generate them and cannot personally guarantee linguistic accuracy as a non-native speaker.
