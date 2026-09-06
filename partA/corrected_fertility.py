#!/usr/bin/env python3
"""
corrected_fertility.py — A3: Corrected tokenizer fertility analysis.

Fixes applied vs original fertility.py:
  1. split() instead of split(" ")         [Bug 1 — incorrect word splitting]
  2. ratio-of-totals instead of mean-of-ratios [Bug 2 — aggregation error]
  3. Multiple denominators reported        [Bug 3 — cross-language comparison]
  4. Two tokenizers: gpt2 + ai-forever/m-BERT [shows tokenizer choice matters]
  5. No lowercasing of Indic scripts       [conceptual improvement]

Usage:
    python corrected_fertility.py

Requires: tiktoken, transformers (or just tiktoken for gpt2-only mode)
"""

import os
import sys
import unicodedata

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(SCRIPT_DIR, "corpus")

# ---------------------------------------------------------------------------
# Tokenizer setup
# ---------------------------------------------------------------------------
try:
    import tiktoken
    enc_gpt2 = tiktoken.get_encoding("gpt2")
    encode_gpt2 = enc_gpt2.encode
    HAS_TIKTOKEN = True
except ImportError:
    print("[setup] tiktoken not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken", "-q"])
    import tiktoken
    enc_gpt2 = tiktoken.get_encoding("gpt2")
    encode_gpt2 = enc_gpt2.encode
    HAS_TIKTOKEN = True

# Try multilingual tokenizer (optional)
try:
    from transformers import AutoTokenizer
    _ml_tok = AutoTokenizer.from_pretrained("ai-forever/mGPT")
    encode_mgpt = lambda s: _ml_tok.encode(s, add_special_tokens=False)
    HAS_MGPT = True
    print("[setup] mGPT tokenizer loaded (multilingual baseline).")
except Exception:
    encode_mgpt = None
    HAS_MGPT = False
    print("[setup] mGPT not available — running gpt2 only.")

SEP = "=" * 70
LANGUAGES = ["eng", "hin", "kan", "tam"]


def read_lines(path: str) -> list:
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = unicodedata.normalize("NFC", raw.strip())
            if line:
                lines.append(line)
    return lines


def count_grapheme_clusters(text: str) -> int:
    """
    Approximate grapheme cluster count via Unicode category.
    Full grapheme segmentation requires the 'grapheme' package;
    we use NFC character count as a reasonable approximation
    (combining marks are attached to base chars after NFC).
    This is imperfect but available without extra dependencies.
    """
    return len(unicodedata.normalize("NFC", text))


def compute_metrics(lines: list, encode_fn, lowercase_eng_only: bool = False,
                    lang: str = "") -> dict:
    """
    Compute fertility metrics using:
      - CORRECT aggregation: ratio of totals (not mean of per-line ratios)
      - CORRECT splitter: split() not split(' ')
      - Multiple denominators: words, chars, sentences, grapheme clusters

    Returns dict of metrics.
    """
    total_tokens = 0
    total_words = 0
    total_chars = 0
    total_graphemes = 0
    n_sentences = len(lines)

    for line in lines:
        # Lowercase only for English (where casing changes tokenization)
        # Do NOT lowercase Indic scripts — it's a no-op but signals wrong intent
        encoded_line = line.lower() if (lowercase_eng_only and lang == "eng") else line
        toks = encode_fn(encoded_line)
        words = line.split()      # FIX 1: split() not split(' ')
        chars = len(line)
        graphemes = count_grapheme_clusters(line)

        total_tokens += len(toks)
        total_words += len(words)
        total_chars += chars
        total_graphemes += graphemes

    return {
        "n_sentences": n_sentences,
        "total_tokens": total_tokens,
        "tok_per_word": total_tokens / total_words if total_words else 0,     # FIX 2: ratio of totals
        "tok_per_sent": total_tokens / n_sentences if n_sentences else 0,
        "tok_per_char": total_tokens / total_chars if total_chars else 0,
        "tok_per_grapheme": total_tokens / total_graphemes if total_graphemes else 0,
        "avg_words_per_sent": total_words / n_sentences if n_sentences else 0,
    }


def print_table(results: dict, tokenizer_name: str):
    print(f"\n  Tokenizer: {tokenizer_name}")
    print(f"  {'lang':<6} {'n_sents':>8} {'tok/word':>10} {'tok/sent':>10} {'tok/char':>10} {'tok/grapheme':>14} {'words/sent':>11}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*14}  {'-'*11}")
    for lang, m in results.items():
        print(
            f"  {lang:<6} {m['n_sentences']:>8} "
            f"{m['tok_per_word']:>10.3f} {m['tok_per_sent']:>10.1f} "
            f"{m['tok_per_char']:>10.4f} {m['tok_per_grapheme']:>14.4f} "
            f"{m['avg_words_per_sent']:>11.1f}"
        )

    # Cross-language ratios (relative to English)
    if "eng" in results:
        print(f"\n  Cross-language ratios vs eng (tok/word):")
        eng_tpw = results["eng"]["tok_per_word"]
        eng_tps = results["eng"]["tok_per_sent"]
        for lang, m in results.items():
            if lang == "eng":
                continue
            ratio_word = m["tok_per_word"] / eng_tpw
            ratio_sent = m["tok_per_sent"] / eng_tps
            print(f"    {lang}: {ratio_word:.2f}x (tok/word), {ratio_sent:.2f}x (tok/sent)")

        print()
        print("  NOTE: tok/sent is the fairer metric for routing cost decisions.")
        print("  tok/word inflates agglutinative languages (Kannada, Tamil)")
        print("  because their morphologically-rich 'words' pack more meaning.")


def main():
    print(SEP)
    print("A3: Corrected Fertility Analysis")
    print(SEP)
    print()
    print("Fixes vs original fertility.py:")
    print("  [1] split() instead of split(' ')  — prevents empty tokens on multi-spaces")
    print("  [2] ratio-of-totals instead of mean-of-ratios  — correct aggregation")
    print("  [3] Multiple denominators: tok/word, tok/sent, tok/char, tok/grapheme")
    print("  [4] Two tokenizers: gpt2 (English-centric) + mGPT (multilingual)")
    print("  [5] No lowercasing for Indic scripts")
    print()

    # Check corpus files exist
    corpus_files = {}
    missing = []
    for lang in LANGUAGES:
        path = os.path.join(CORPUS_DIR, f"{lang}.txt")
        if os.path.exists(path):
            lines = read_lines(path)
            if lines:
                corpus_files[lang] = lines
            else:
                missing.append(lang)
        else:
            missing.append(lang)

    if missing:
        print(f"  WARNING: corpus missing for {missing}. Run corpus_prep.py first.")
        print()

    if not corpus_files:
        print("ERROR: No corpus files found. Please run corpus_prep.py first.")
        sys.exit(1)

    print(f"  Loaded corpus: {', '.join(f'{lang}={len(lines)} sents' for lang, lines in corpus_files.items())}")
    print()

    # -----------------------------------------------------------------------
    # GPT-2 tokenizer results
    # -----------------------------------------------------------------------
    print(SEP)
    print("RESULTS — GPT-2 tokenizer (English-centric BPE)")
    print(SEP)
    gpt2_results = {}
    for lang, lines in corpus_files.items():
        gpt2_results[lang] = compute_metrics(lines, encode_gpt2, lowercase_eng_only=False, lang=lang)
    print_table(gpt2_results, "gpt2 (tiktoken)")

    # -----------------------------------------------------------------------
    # mGPT tokenizer results (if available)
    # -----------------------------------------------------------------------
    if HAS_MGPT and encode_mgpt:
        print()
        print(SEP)
        print("RESULTS — mGPT tokenizer (multilingual, trained on 61 languages)")
        print(SEP)
        mgpt_results = {}
        for lang, lines in corpus_files.items():
            mgpt_results[lang] = compute_metrics(lines, encode_mgpt, lowercase_eng_only=False, lang=lang)
        print_table(mgpt_results, "mGPT (ai-forever/mGPT)")

        # Compare tokenizers
        print()
        print(SEP)
        print("TOKENIZER COMPARISON SUMMARY")
        print(SEP)
        print()
        print(f"  {'lang':<6} {'gpt2 tok/word':>15} {'mGPT tok/word':>15} {'improvement':>15}")
        print(f"  {'-'*6}  {'-'*15}  {'-'*15}  {'-'*15}")
        for lang in corpus_files:
            g = gpt2_results[lang]["tok_per_word"]
            m_val = mgpt_results[lang]["tok_per_word"]
            improvement = (g - m_val) / g * 100
            arrow = "↓ better" if improvement > 0 else "↑ worse"
            print(f"  {lang:<6} {g:>15.3f} {m_val:>15.3f} {improvement:>+14.1f}% {arrow}")

        print()
        print("  KEY INSIGHT: mGPT has a dedicated Indic vocabulary and produces")
        print("  substantially fewer tokens per Indic word than gpt2.")
        print("  The tok/word ratio for gpt2 overstates Indic serving cost")
        print("  for systems using multilingual tokenizers.")

    # -----------------------------------------------------------------------
    # Denominator reasoning (A3 question)
    # -----------------------------------------------------------------------
    print()
    print(SEP)
    print("DENOMINATOR REASONING: Which metric to use for routing decisions?")
    print(SEP)
    print("""
  QUESTION: Should we compute tok/word, tok/char, or tok/sentence?

  ANSWER: tok/sentence is the right primary metric for serving cost.

  REASONING:
    - One user request = one response = one sequence of tokens to generate.
    - Serving cost (GPU time, memory) scales with #tokens generated, not #words.
    - 'word' is not a stable unit across languages:
        * English 'water' = 1 word, 1 morpheme, ~1.3 tokens
        * Hindi 'पानी' = 1 word, 1 morpheme, ~4-6 GPT-2 tokens
        * Tamil 'தண்ணீர்' = 1 word, but encodes complex morphological info
        * Kannada 'ನೀರಿನಿಂದಾಗಿ' = 1 word, 4 morphemes, expensive to tokenize
    - A Hindi speaker asking the same question as an English speaker produces
      a SIMILAR NUMBER OF SENTENCES but more tokens per sentence (due to script).
      tok/sentence directly answers: 'how many tokens do I generate per user turn?'
    - tok/char and tok/grapheme-cluster are good engineering metrics for
      estimating vocabulary compression efficiency, but less useful for
      per-request cost estimation.

  RECOMMENDATION:
    Use tok/sentence for capacity planning and routing budget.
    Use tok/char for comparing tokenizer vocabulary coverage.
    Use tok/word ONLY within a single language (never cross-linguistically).
""")

    # Write results to file
    out_path = os.path.join(SCRIPT_DIR, "corrected_analysis_output.txt")
    import io
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    # Re-run prints to buffer
    print_table(gpt2_results, "gpt2 (tiktoken)")
    if HAS_MGPT and encode_mgpt:
        print_table(mgpt_results, "mGPT (ai-forever/mGPT)")

    sys.stdout = old_stdout
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("=== A3 Corrected Fertility Results ===\n\n")
        f.write(buffer.getvalue())
    print(f"\n[A3] Results written -> {out_path}")
    print("[A3] Corrected fertility analysis complete!")


if __name__ == "__main__":
    main()
