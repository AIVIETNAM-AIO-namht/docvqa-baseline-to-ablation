"""Phép kiểm hợp lệ của dự án: đổi tên file nhãn rồi chạy lại.

    "Pipeline suy luận chỉ được đọc manifest.jsonl, questions.jsonl, images/,
     ocr/ — tuyệt đối không được chạm labels.jsonl và cell_annotations.jsonl.
     Cách tự kiểm: đổi tên hai file nhãn rồi chạy lại, nếu pipeline vẫn chạy
     được thì mới hợp lệ."

Harness trần oracle là NGOẠI LỆ có chủ ý: nó phải đọc labels.jsonl để lấy ô
vàng — đó là định nghĩa của trần oracle ("điểm tối đa khi biết trước ô đúng").
Nó chỉ không được đọc cell_annotations.jsonl. Nên ở đây ẩn đúng file đó.

    python check_validity.py oracle_ceiling.py
    python check_validity.py config_b.py --hide labels.jsonl cell_annotations.jsonl
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).resolve().parents[3] / "data" / "training_set"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--hide", nargs="+", default=["cell_annotations.jsonl"])
    args = ap.parse_args()

    targets = [DATA / name for name in args.hide]
    for t in targets:
        assert t.exists(), f"không thấy file để ẩn: {t}"

    hidden = [t.with_suffix(t.suffix + ".hidden") for t in targets]
    try:
        for t, h in zip(targets, hidden):
            t.rename(h)
        print(f"đã ẩn: {', '.join(args.hide)}\n")
        r = subprocess.run([sys.executable, args.script], capture_output=True, text=True, encoding="utf-8")
        print(r.stdout[-2000:] if r.stdout else "(không có stdout)")
        if r.returncode != 0:
            print(r.stderr[-2000:])
    finally:
        for t, h in zip(targets, hidden):
            if h.exists():
                h.rename(t)
        print(f"\nđã trả tên lại: {', '.join(args.hide)}")

    assert r.returncode == 0, f"{args.script} KHÔNG chạy được khi thiếu file nhãn -> không hợp lệ"
    print(f"HỢP LỆ: {args.script} chạy được mà không cần {', '.join(args.hide)}")


if __name__ == "__main__":
    main()
