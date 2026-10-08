"""Tách training_set theo TÀI LIỆU thành dev (880) / eval (220).

Chia theo tài liệu, không theo câu hỏi: 10 câu hỏi dùng chung một tài liệu,
chia theo câu sẽ rò rỉ layout giữa hai phần.

    python split_docs.py

Ghi ra Working Files/splits/dev_docs.txt + eval_docs.txt (mỗi dòng một document_id).
Chỉ đọc manifest.jsonl — không chạm labels.jsonl / cell_annotations.jsonl.
"""
import json
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[3]
MANIFEST = BASE / "data" / "training_set" / "manifest.jsonl"
OUT = Path(__file__).resolve().parent.parent / "splits"

N_EVAL = 220
SEED = 20260921  # cố định để tái lập


def main():
    docs = [json.loads(l)["id"] for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l.strip()]

    shuffled = docs[:]
    random.Random(SEED).shuffle(shuffled)
    eval_docs = sorted(shuffled[:N_EVAL])
    dev_docs = sorted(shuffled[N_EVAL:])

    assert len(dev_docs) == 880 and len(eval_docs) == 220, (len(dev_docs), len(eval_docs))
    assert not set(dev_docs) & set(eval_docs)
    assert set(dev_docs) | set(eval_docs) == set(docs)

    OUT.mkdir(exist_ok=True)
    (OUT / "dev_docs.txt").write_text("\n".join(dev_docs) + "\n", encoding="utf-8")
    (OUT / "eval_docs.txt").write_text("\n".join(eval_docs) + "\n", encoding="utf-8")

    print(f"OK  {len(dev_docs)} dev / {len(eval_docs)} eval  (seed {SEED})")
    print(f"    {OUT / 'dev_docs.txt'}")
    print(f"    {OUT / 'eval_docs.txt'}")


def load(split):
    """Đọc lại danh sách tài liệu của một phần: load('dev') -> list[str]."""
    path = OUT / f"{split}_docs.txt"
    return [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


if __name__ == "__main__":
    main()
