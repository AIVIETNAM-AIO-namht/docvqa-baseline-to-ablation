"""Trần của MỌI bộ lọc hàng tĩnh, cho `argmax`/`argmin` — đo giới hạn trên của
Cấu hình C trước khi bỏ công dựng model.

Câu hỏi: nếu cho phép lọc bớt hàng của bảng (một tập hàng dùng chung cho mọi
câu hỏi trên bảng đó) thì chọn hàng của Cấu hình B lên được tới đâu? Đây là
đúng bài toán mà LayoutLMv3 được kỳ vọng giải ("tái dựng hàng logic"), nên con
số này là TRẦN của cả nhánh C, không chỉ của một luật cụ thể nào.

Harness này BIẾT TRƯỚC hàng vàng (đọc `labels.jsonl`) — cùng loại với
`oracle_ceiling.py`. Nó không phải solver, nó đo giới hạn trên. Vì vậy kết quả
là CẦN, không phải ĐỦ: một luật thật phải suy ra được tập hàng từ OCR, không
được nhìn đáp án.

Không đọc `cell_annotations.jsonl`: lưới lấy từ `grid_ocr.build_tables`.

Cơ chế đếm (không vét cạn 2^số_hàng × số_bộ_lọc, dùng điều kiện tương đương):

    Bộ lọc là một tập hàng của TOÀN BẢNG, dùng chung cho mọi câu của bảng đó.
    Hàng ngoài pool_j (hàng ứng viên của câu j) KHÔNG ảnh hưởng câu j. Nên thứ
    chặn câu j chỉ là:

        blocked[j] = {r trong pool_j : khoá(r) TỐT HƠN khoá(hàng vàng j)}

    Tập câu T khả thi  <=>  với mọi i,j thuộc T:  gold_i KHÔNG thuộc blocked[j]
                            (lấy S = {gold_i : i thuộc T})
    trần[bảng] = max |T|

    Bất biến kiểm được: T = tập câu Cấu hình B đúng luôn khả thi, vì bộ lọc
    S = pool_j khi đó chính là solver ⇒ trần >= số câu B đúng. Vi phạm = bug.

    python row_filter_ceiling.py --split dev
    python row_filter_ceiling.py --split eval
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, build_tables, load_jsonl, to_number
from audit_rule_system import ASKED, LABEL, PAGE, TBL, find_col, groups, match_rows

SPLITS = HERE.parent / "splits"
BBOX_TOL = 1e-6


def same_bbox(a, b):
    return all(abs(x - y) <= BBOX_TOL for x, y in zip(a, b))


def gold_row_of(table, gold_ev, lc):
    """Hàng vàng = hàng chứa ô nhãn (cột `lc`) trong evidence vàng.

    `lc` là cột mà solver trả lời; nếu evidence vàng không có ô ở cột đó thì
    lùi về hàng của ô evidence đầu tiên (dùng để chẩn đoán, không để chọn).
    """
    hit = [c for c in table if any(same_bbox(c["bbox"], e["bbox"]) and c["page"] == e["page"]
                                   for e in gold_ev)]
    for c in hit:
        if c["column"] == lc:
            return c["row"]
    return hit[0]["row"] if hit else None


def resolve(doc, q, docs, tabs):
    """Tái hiện khâu chọn bảng của solver -> (table, ac, rows, G) hoặc None."""
    pages = [int(x) for x in PAGE.findall(q)]
    mt = TBL.search(q)
    asked = next((a.group(1) for a in (r.search(q) for r in ASKED) if a), None)
    cands = [(pages[0], int(mt.group(1)))] if (mt and pages) else \
            [(p, t) for p in pages[:1] for (pp, t) in docs[doc] if pp == p]
    for page, tbl in cands:
        table = tabs.get((page, tbl))
        if not table:
            continue
        ac = find_col(table, asked)
        G = groups(q, table)
        rows, _ = (None, []) if not G else match_rows(table, G[0])
        if G and rows is None:
            continue
        return table, ac, rows, G
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="all", choices=["all", "dev", "eval"])
    args = ap.parse_args()

    keep = None if args.split == "all" else \
        set((SPLITS / f"{args.split}_docs.txt").read_text(encoding="utf-8").split())

    labels = load_jsonl(DATA / "labels.jsonl")
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}

    tabs, docs = {}, defaultdict(set)
    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        if doc in tabs or (keep is not None and doc not in keep):
            continue
        mine = build_tables(doc)
        tabs[doc] = mine
        docs[doc] = set(mine)

    # Mỗi câu -> một phiếu trên bảng của nó.
    per_table = defaultdict(list)      # (doc, page, tbl) -> [phiếu]
    unfixable = defaultdict(int)       # lý do câu KHÔNG bộ lọc hàng nào cứu được
    n = ok = 0

    for lab in labels:
        rt, qid = lab["reasoning_type"], lab["question_id"]
        if rt not in ("argmax", "argmin"):
            continue
        doc = qid.rsplit("-q", 1)[0]
        if keep is not None and doc not in keep:
            continue
        n += 1

        sol = resolve(doc, questions[qid], docs, tabs[doc])
        if sol is None:
            unfixable["khong chon duoc bang"] += 1
            continue
        table, ac, rows, G = sol
        lm = LABEL.search(questions[qid])
        lc = find_col(table, lm.group(1)) if lm else None
        if ac is None or lc is None:
            unfixable["khong tra duoc cot"] += 1
            continue

        gg = {(c["row"], c["column"]): c for c in table if not c["is_header"]}
        pool = [r for r in (set(rows) if rows is not None else {r for (r, c) in gg if c == ac})
                if (r, ac) in gg and (r, lc) in gg]
        sc = [(to_number(gg[(r, ac)]["clean_text"]), r) for r in pool]
        sc = [(v, r) for v, r in sc if v is not None]
        if not sc:
            unfixable["khong co so trong cot duoc hoi"] += 1
            continue

        grow = gold_row_of(table, lab["evidence"], lc)
        if grow is None or grow not in pool:
            unfixable["hang vang khong nam trong pool"] += 1
            continue

        reverse = (rt == "argmax")
        win = sorted(sc, reverse=reverse)[0][1]
        val = dict((r, v) for v, r in sc)
        if grow not in val:
            unfixable["hang vang khong co so o cot duoc hoi"] += 1
            continue
        # khoá sắp xếp là TUPLE (giá trị, chỉ số hàng) — đúng như solver. Hàng
        # không có số không bao giờ thắng nên không nằm trong `val`.
        #
        # Bộ lọc là một tập hàng của TOÀN BẢNG, còn pool (hàng ứng viên) khác
        # nhau theo từng câu: hàng ngoài `pool_j` không ảnh hưởng câu j. Nên thứ
        # chặn câu j là tập `blocked[j]` = hàng trong pool_j có khoá TỐT HƠN hàng
        # vàng; chọn chúng vào bộ lọc là câu j mất đáp án.
        key = lambda r: (val[r], r)
        kg = key(grow)
        blocked = {r for r in val if (key(r) > kg if reverse else key(r) < kg)}

        # Harness này chỉ đếm số câu nên không dựng ô; evidence của solver dùng
        # bộ khoá {(r, ac), (r, lc), (r, lc+1)} | {(r, cột bộ lọc)} — xem `keys`
        # trong audit_rule_system.py.
        tk = (doc, table[0]["page"], table[0]["table"])
        per_table[tk].append((grow, blocked, win == grow))
        ok += (win == grow)

    # Trần: tập con lớn nhất T các câu mà MỘT bộ lọc hàng chung làm tất cả cùng
    # đúng. Câu j hỏng khi bộ lọc chứa một hàng trong `blocked[j]` (hàng ứng viên
    # có khoá tốt hơn hàng vàng); hàng ngoài pool_j vô hại. Nên
    #   T khả thi  <=>  với mọi i,j thuộc T:  gold_i KHÔNG thuộc blocked[j]
    # (lấy S = {gold_i : i thuộc T}: mọi câu trong T vẫn đúng, và nếu điều kiện
    #  trên đúng thì không bộ lọc nào làm tốt hơn được nữa).
    # ponytail: m <= ~10 nên vét cạn 2^m là đủ; đừng dựng max-clique.
    ceil = 0
    n_tables = n_consistent = 0
    bad = []                           # bảng vi phạm bất biến (phải rỗng)
    for tk, votes in per_table.items():
        n_tables += 1
        m = len(votes)
        compat = [sum(1 << i for i in range(m) if votes[i][0] not in votes[j][1])
                  for j in range(m)]
        best = 0
        for mask in range(1 << m):
            k = bin(mask).count("1")
            if k <= best:
                continue
            if all(mask & ~compat[j] == 0 for j in range(m) if mask >> j & 1):
                best = k
        ceil += best
        n_consistent += (best == m)
        k_ok = sum(v[2] for v in votes)     # câu B đúng trong bảng này
        if best < k_ok:                     # bất khả: tập câu B-đúng luôn khả thi
            bad.append((tk, best, k_ok, m))
    assert not bad, f"bất biến vỡ ở {len(bad)} bảng: {bad[:5]}"

    print(f"===== TRẦN BỘ LỌC HÀNG TĨNH — argmax/argmin  (split: {args.split}) =====")
    print(f"câu argmax/argmin                : {n}")
    print(f"Cấu hình B đúng                  : {ok}/{n} = {100*ok/n:.2f}%")
    print(f"trần (biết trước hàng vàng)      : {ceil}/{n} = {100*ceil/n:.2f}%")
    print(f"dư địa của nhánh C               : +{ceil-ok} câu = "
          f"+{100*(ceil-ok)/n:.2f} điểm % trên kiểu này")
    print(f"bảng có tập con nhất quán        : {n_consistent}/{n_tables} "
          f"= {100*n_consistent/n_tables:.1f}%")
    print("\n--- câu mà bộ lọc hàng KHÔNG cứu được ---")
    for k, v in sorted(unfixable.items(), key=lambda kv: -kv[1]):
        print(f"  {v:5d}  {k}")
    print(f"  {n-ceil-sum(unfixable.values()):5d}  còn lại: bảng tự mâu thuẫn "
          f"(hai câu đòi hai tập hàng khác nhau)")

    # Chặn trên điểm cuộc thi. Bộ lọc tĩnh THAY tập câu đúng của B: câu B-đúng
    # mà không nằm trong T sẽ thành sai, nên chênh thật là `ceil - ok`, không
    # phải số câu B-sai được cứu. Mỗi câu đổi trạng thái coi như đi từ 0 lên 1
    # (ANLS/EvF1 tuyệt đối) — chặn trên, không phải trần chặt.
    #
    # Ngoại suy về toàn bộ 11.000 câu: tỉ lệ sửa được của kiểu này × tỉ trọng
    # của kiểu này trong cuộc thi. Chia thẳng cho 11.000 là SAI khi chạy --split
    # dev/eval (tử số đo trên split, mẫu số của cả cuộc thi).
    # ponytail: `gain` chỉ là CHẶN TRÊN vì bộ lọc ở đây biết hàng vàng. Muốn biết
    # chặn chặt phải chỉ ra một luật suy được từ OCR chọn đúng tập hàng đó — xem
    # Bước 2 của kế hoạch. Nếu không có luật nào thì con số này không triển khai được.
    gain = ceil - ok
    n_arg_all = sum(1 for lab in labels if lab["reasoning_type"] in ("argmax", "argmin"))
    share = n_arg_all / len(labels)
    print(f"\nchặn trên điểm cuộc thi: {gain} câu = {100*gain/n:.2f}% câu kiểu này "
          f"=> ngoại suy toàn bộ: {gain/n*share:+.5f} điểm")


if __name__ == "__main__":
    main()
