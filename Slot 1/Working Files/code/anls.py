"""ANLS for TACVU2 — 85% of the score.

    s(a, o) = 1 - NL(a, o)   if NL(a, o) < tau
            = 0              otherwise

tau applies to the NORMALISED LEVENSHTEIN DISTANCE, not to the similarity.
Writing `if sim > 0.5` instead of `if dist < 0.5` is a silent bug that inflates
every score — see WEEK01 §3.2.

Source: ST-VQA §3.4, arXiv 1905.13648. DocVQA reused it; it did not define it.

Multiple gold answers: the dataset gives a list, take the best-matching one.
"""
import re
from collections import deque

TAU = 0.5


def normalize(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def to_number(s):
    """'1.850' -> 1850.0 (vi-VN groups thousands with '.'), '3,5' -> 3.5.

    ponytail: only used for the equal-as-numbers shortcut. The levenshtein
    fallback still scores near-miss digits the ordinary way.
    """
    s = s.strip().replace(" ", "")
    if re.fullmatch(r"[+-]?\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", "").replace("+", ""))
    s2 = s.replace(",", ".")
    return float(s2) if re.fullmatch(r"[+-]?\d+(\.\d+)?", s2) else None


def levenshtein(a, b):
    """Iterative DP, O(min(len)) memory. Strings here are short (<= ~60 chars)."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def anls_single(pred, gold, tau=TAU):
    p, g = normalize(pred), normalize(gold)
    if not p or not g:
        return 0.0
    if p == g:
        return 1.0
    np_, ng_ = to_number(p), to_number(g)
    if np_ is not None and ng_ is not None:
        # Numbers that differ only in grouping are the same answer.
        return 1.0 if abs(np_ - ng_) < 1e-9 else 0.0
    dist = levenshtein(p, g)
    nl = dist / max(len(p), len(g))
    return 1.0 - nl if nl < tau else 0.0


def anls(pred, golds, tau=TAU):
    """golds is the label's `answers` list; best match wins."""
    if isinstance(golds, str):
        golds = [golds]
    return max((anls_single(pred, g, tau) for g in golds), default=0.0)


if __name__ == "__main__":
    # tau bites on DISTANCE: these two must land on opposite sides of 0.5.
    assert anls("hoa don", ["Hóa đơn"]) > 0.5, "1 edit / 7 chars -> dist .14 -> keep"
    assert anls("abcdef", ["xyz"]) == 0.0, "dist 1.0 -> zeroed"
    assert anls("7", ["7"]) == 1.0
    assert anls("1.850", ["1850"]) == 1.0, "vi-VN grouping is the same number"
    assert anls("1.851", ["1850"]) == 0.0, "numbers differ -> 0, not partial"
    assert anls("", ["a"]) == 0.0
    # the classic: a wrong answer must not score like a right one
    assert anls("Nguyễn Văn B", ["Nguyễn Văn A"]) > 0.5
    print("anls.py self-check OK")
