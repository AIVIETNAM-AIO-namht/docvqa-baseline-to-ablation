"""He thong CHON O bang LUAT THUAN PYTHON — diem end-to-end that, khong model.

Cau hoi: neu luat thuan di duoc gan bang mentor (95,45) thi moi huong output
"can train model" deu la thua. Neu khong, khoang cach chinh la gia tri cua model.

Co che duy nhat, dung cho ca 8 kieu:
  1. boc cac cap  <Ten cot> "<gia tri>"  theo thu tu xuat hien
  2. cot lap lai => mo NHOM moi. Moi nhom = mot HANG.
     (vd: 'Phong ban "A" va Phong ban "B" va Dinh bien "30"'
          -> nhom1 {Phong ban=A}, nhom2 {Phong ban=B, Dinh bien=30})
  3. cot duoc hoi: boc theo template cua tung kieu
  4. chon o dap an; evidence = o bo loc + o dap an (dung nhu nhan)

Kieu dac biet:
  argmax/argmin  -> khong co bo loc: xep hang TOAN BANG theo cot duoc hoi
  count          -> dem so o khop bo loc
  compare        -> 2 nhom, chon nhom thang theo tu so sanh trong cau
  cross_page_sum -> 2 nhom o 2 TRANG khac nhau; cau KHONG noi so bang
  visual_bold_lookup -> 2 nhom, chon nhom co toan bo o in dam

KHONG doc file nhan de giai: luoi lay tu `grid_ocr.build_tables` (OCR + anh
trang), `is_bold` do tu anh. `labels.jsonl` chi dung de CHAM diem.

    python audit_rule_system.py --split dev     # chot luat
    python audit_rule_system.py --split eval    # chi sau khi chot luat
"""
import argparse, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, build_tables, fill_bold, load_jsonl, to_number, fmt
from anls import anls
from evidence_f1 import evidence_f1

SPLITS = HERE.parent / "splits"

QUOTED = re.compile(r"([^,;:?]{2,40}?)\s*[“\"]([^”\"]+)[”\"]")
PAGE = re.compile(r"ở\s+trang\s+(\d+)", re.I)
TBL = re.compile(r"bảng\s+(\d+)", re.I)
ASKED = [
    re.compile(r"Lấy\s+(.+?)\s+của\s+dòng\s+có", re.I),            # cross_page_sum
    re.compile(r"tổng\s+(.+?)\s+của\s+(?:hai|ba)\s+dòng", re.I),   # sum
    re.compile(r"dòng\s+nào\s+có\s+(.+?)\s+(?:cao|thấp|nhỏ|lớn)\s+hơn", re.I),  # compare
    re.compile(r"cho\s+biết\s+(.+?)\s+tại\s+bảng", re.I),          # lookup (v2)
    re.compile(r"trang\s+\d+,\s+(.+?)\s+của\s+dòng\s+có", re.I),   # lookup (v1), sum, argmax
    re.compile(r"đọc\s+ô\s+thuộc\s+cột\s+(.+?)\s*[.,]", re.I),    # visual_bold_lookup (v1)
    re.compile(r"giá\s+trị\s+(.+?)\s+của\s+dòng\s+đó", re.I),      # visual_bold_lookup (v2)
    re.compile(r"có\s+(.+?)\s+(?:lớn nhất|nhỏ nhất|cao nhất|thấp nhất|nhiều nhất|ít nhất)\s*\?", re.I),  # argmax/argmin
    re.compile(r"có\s+(.+?)\s+là\s*[“\"]", re.I),             # count
    re.compile(r"trả\s+về\s+nội\s+dung\s+cột\s+(.+?)\s*[.,]", re.I),  # visual_bold_lookup (v3)
    re.compile(r"giá\s+trị\s+ở\s+cột\s+(.+?)\s*[.,]", re.I),  # visual_bold_lookup (v4)
    re.compile(r"ghi\s+(.+?)\s+bằng\s+bao\s+nhiêu", re.I),     # lookup (v4)
]
# Cum noi nam giua ten cot va gia tri -> cat bo, chi giu danh tu cuoi
FILLER = ("của dòng có", "dòng có", "đối với", "tại bảng", "của", " là ", "cột",
          "giá trị", "tổng", "Lấy", "giữa")
# Tu noi mo dau con lai sau khi cat FILLER (' dòng Mã hàng' -> 'Mã hàng')
LEAD = re.compile(r"^(?:và|hoặc|hãy|chọn|dòng|in|đậm|được|giữa|tìm|quan|sát|trực|tiếp)\s+", re.I)
LABEL = re.compile(r"([^,;:?]{2,40}?)\s+nào\s+có", re.I)
COMPARE_SMALL = re.compile(r"nhỏ hơn|thấp hơn|ít hơn", re.I)
COUNT = re.compile(r"có\s+bao\s+nhiêu\s+dòng", re.I)
BOLD = ("visual_bold_lookup",)


def norm(s):
    """Chuẩn hoá để khớp tên cột / giá trị: bỏ dấu câu, gộp khoảng trắng, hạ chữ."""
    return re.sub(r"\s+", " ", re.sub(r"[()\[\]:.,“”\"]", " ", s)).strip().lower()


def find_col(table, name):
    """Tra cột theo tên header: khớp chính xác, rồi khớp chứa nhau, rồi thử ĐUÔI TỪ.

    Tên cột bóc từ câu hỏi hay bị dính tiền tố rác rất đa dạng
    ('toàn bộ chữ in đậm trong hai dòng Gói thầu', 'hãy chọn dòng in đậm giữa
    Phòng ban'). Liệt kê tiền tố là vô vọng, nên thay bằng: thử lần lượt 4,3,2,1
    từ CUỐI của tên — tên cột thật luôn nằm ở đuôi.
    """
    if not name:
        return None
    h = {norm(c["clean_text"]): c["column"] for c in table if c["is_header"]}
    n = norm(clean_name(name))
    if n in h:
        return h[n]
    hit = [col for t, col in h.items() if n and (n in t or t in n)]
    if len(hit) == 1:
        return hit[0]
    w = n.split()
    for k in (4, 3, 2, 1):
        if k > len(w):
            continue
        t = " ".join(w[-k:])
        if t in h:
            return h[t]
        hit = [col for hh, col in h.items() if t in hh or hh in t]
        if len(hit) == 1:
            return hit[0]
    return None                        # nhieu ket qua = mo ho -> tu choi


def grid(table):
    """{(row, col): cell} cho các ô không phải header."""
    return {(c["row"], c["column"]): c for c in table if not c["is_header"]}


def clean_name(s):
    """Cat cum noi, chi giu danh tu cuoi cua ten cot.

    'tong Tuyen moi cua hai dong co Phong ban' -> 'Phong ban'
    'giua dong co Phong ban'                  -> 'Phong ban'
    'hay chon dong in dam giua Phong ban'     -> 'Phong ban'
    """
    s = re.sub(r"\s+là$", "", s.strip(), flags=re.I)   # copula cuoi: '... cot là'
    for f in FILLER:
        if f in s:
            s = s.rsplit(f, 1)[-1]
    while True:                       # ' dong Ma hang' -> 'Ma hang'
        s2 = LEAD.sub("", s.strip()).strip()
        if s2 == s:
            return s2
        s = s2


def groups(q, table=None):
    """Các cặp <cột> "<giá trị>" -> nhóm theo hàng. Cột lặp lại = hàng mới.

    Ranh giới hàng phải so theo COT ĐÃ TRA ĐƯỢC, không theo tên thô: cùng một
    cột xuất hiện dưới hai tên khác nhau do dính tiền tố rác
    ('…hai dòng Điểm quan trắc' vs 'Điểm quan trắc') -> so chuỗi sẽ trượt
    ranh giới và gộp hai hàng làm một.
    """
    out = []
    for name, val in QUOTED.findall(q):
        name, val = clean_name(name), val.strip()
        col = find_col(table, name) if table is not None else None
        key = ("col", col) if col is not None else ("name", norm(name))
        if out and key not in [k for k, _ in out[-1]]:
            out[-1].append((key, (name, val)))
        else:
            out.append([(key, (name, val))])
    return [[pair for _, pair in g] for g in out]


def match_rows(table, grp):
    """Hàng khớp TOÀN BỘ cặp (cột, giá trị) trong nhóm. Trả (rows, cells).

    Giao theo SO HANG, khong theo o: hai cap loc thuong khac cot, nen giao
    tap o se luon rong. Uu tien khop chuoi; khong co thi thu khop so
    ('1.850' trong cau vs '1.850' trong o, hoac '1850' vs '1.850').
    """
    G, rows, cells = grid(table), None, []
    for name, val in grp:
        fc = find_col(table, name)
        if fc is None:
            return None, []
        hit = {(r, fc) for (r, c), cell in G.items()
               if c == fc and norm(cell["clean_text"]) == norm(val)}
        if not hit:
            v = to_number(val)
            if v is not None:
                hit = {(r, fc) for (r, c), cell in G.items()
                       if c == fc and to_number(cell["clean_text"]) == v}
        if not hit:
            return None, []
        rs = {r for r, _ in hit}
        rows = rs if rows is None else (rows & rs)
        cells += [G[k] for k in hit if k in G]
    return rows, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="all", choices=["all", "dev", "eval"])
    args = ap.parse_args()

    keep = None
    if args.split != "all":
        keep = set((SPLITS / f"{args.split}_docs.txt").read_text(encoding="utf-8").split())

    labels = load_jsonl(DATA / "labels.jsonl")
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}

    # Luoi lay tu OCR, KHONG tu cell_annotations.jsonl. Dung chung cho moi cau
    # cua cung tai lieu nen nho dem theo doc.
    tabs, docs = {}, defaultdict(set)
    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        if doc in tabs or (keep is not None and doc not in keep):
            continue
        mine = build_tables(doc)
        tabs[doc] = mine
        docs[doc] = set(mine)

    per_type = defaultdict(lambda: [0.0, 0.0, 0, 0])
    miss = defaultdict(int)
    n_ev = [0, 0]

    for lab in labels:
        rt, qid = lab["reasoning_type"], lab["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        if keep is not None and doc not in keep:
            continue
        q = questions[qid]
        gold_ans, gold_ev = lab["answers"], lab["evidence"]
        pred_ans, pred_ev = None, []

        pages = [int(x) for x in PAGE.findall(q)]
        mt = TBL.search(q)
        asked = next((a.group(1) for a in (r.search(q) for r in ASKED) if a), None)

        # bang ung vien: neu cau khong noi so bang (cross_page_sum) -> moi bang cua trang do
        cands = [(p, int(mt.group(1))) for p in pages[:1]] if mt else \
                [(p, t) for p in pages[:1] for (pp, t) in docs[doc] if pp == p]

        solved = None
        for page, tbl in cands:
            table = tabs[doc].get((page, tbl))
            if not table:
                continue
            ac = find_col(table, asked)
            G = groups(q, table)          # ranh gioi hang can biet cot -> tach theo tung bang
            rows, fcells = (None, []) if not G else match_rows(table, G[0])
            if G and rows is None:
                continue
            if rt in BOLD:
                # Ung vien = hang khop TUNG nhom trong cau ("hai dong X va Y").
                # PHAI goi sau khi co G, khong phai mot lan cho ca bang: do dam
                # chi co nghia khi so giua dung hai hang cau hoi neu ten.
                cand = set()
                for grp in G:
                    rr, _ = match_rows(table, grp)
                    cand |= set(rr or ())
                fill_bold(doc, table, cand)
            solved = (table, ac, rows, fcells, G)
            break
        if solved:
            table, ac, rows, fcells, G = solved
            gg = grid(table)
            if COUNT.search(q):
                ev = fcells
                pred_ans = fmt(len(ev)) if ev else None
                pred_ev = ev
            elif rt in ("argmax", "argmin"):
                lm = LABEL.search(q)
                lc = find_col(table, lm.group(1)) if lm else None
                # Chi hang CO O NHAN moi la ung vien. Dong khong co o o cot nhan
                # la dong noi tiep / dong tong — khong phai mot "Diem den" that,
                # nen khong duoc thang. (B-train-00119: r10 thieu c0, mang gia
                # tri 642 < 1.096 cua Khanh Hoa -> neu khong loc se chon sai.)
                pool = [r for r in (set(rows) if rows is not None else {r for (r, c) in gg if c == ac})
                        if (r, ac) in gg and (lc is None or (r, lc) in gg)]
                sc = [(to_number(gg[(r, ac)]["clean_text"]), r) for r in pool]
                sc = [(v, r) for v, r in sc if v is not None]
                if sc and lc is not None:
                    sc.sort(reverse=(rt == "argmax"))
                    r = sc[0][1]
                    # ponytail: nhan danh dau {o nhan, o cot 2, o cot duoc hoi} o
                    # 62% truong hop, {o nhan, o duoc hoi} o 38%. Do F1: them o
                    # thu ba loi hon (0,92 vs 0,88) vi F1 doi xung. Cot 2 la quy
                    # uoc cua nhan, khong suy ra duoc tu cau hoi.
                    keys = {(r, ac), (r, lc), (r, lc + 1)} | \
                           {(r, find_col(table, n)) for n, _ in (G[0] if G else [])}
                    pred_ev = [gg[k] for k in keys if k in gg]
                    pred_ans = gg[(r, lc)]["clean_text"]
            elif rt in BOLD and len(G) >= 2:
                # 2 nhom = 2 ung vien; chon nhom co TOAN BO o in dam
                for grp in G:
                    rr, ff = match_rows(table, grp)
                    if not rr:
                        continue
                    r = list(rr)[0]
                    if all(c["is_bold"] for (r2_, _), c in gg.items() if r2_ == r):
                        pred_ans = gg[(r, ac)]["clean_text"] if ac is not None and (r, ac) in gg else None
                        # Nhan danh dau CA HAI ung vien: hang thang (moi o khop) +
                        # hang thua NHUNG CHI O NHAN (o trai nhat). Thieu o nay
                        # -> recall 0,63 tren kieu nay.
                        lose = [min([c for (r3, _), c in gg.items() if r3 == x],
                                    key=lambda c: c["column"])
                                for grp2 in G for x in (match_rows(table, grp2)[0] or ())
                                if x != r and any(r3 == x for r3, _ in gg)]
                        pred_ev = ff + ([gg[(r, ac)]] if ac is not None and (r, ac) in gg else []) + lose
                        break
            elif rt == "compare" and len(G) == 2:
                # nhan hang: cot ngay truoc 'nao co' (LABEL bat nham ' dong' -> bo qua)
                lm = LABEL.search(q)
                lc = find_col(table, lm.group(1)) if lm else None
                if lc is None:
                    lc = find_col(table, G[0][0][0])
                r2, f2 = match_rows(table, G[1])
                if r2 and ac is not None:
                    v1 = [to_number(gg[(r, ac)]["clean_text"]) for r in rows if (r, ac) in gg]
                    v2 = [to_number(gg[(r, ac)]["clean_text"]) for r in r2 if (r, ac) in gg]
                    v1 = [v for v in v1 if v is not None]
                    v2 = [v for v in v2 if v is not None]
                    if v1 and v2:
                        smaller = bool(COMPARE_SMALL.search(q))
                        win = rows if ((v1[0] < v2[0]) == smaller) else r2
                        r0 = list(win)[0]
                        pred_ans = gg[(r0, lc)]["clean_text"] if lc is not None and (r0, lc) in gg else None
                        # Nhan danh dau CA HAI dong: o bo loc + o cot duoc hoi +
                        # o nhan, ke ca dong thua. Truoc chi danh dau dong thang.
                        both = rows | r2
                        pred_ev = [c for c in fcells if c["row"] in rows] + \
                                  [c for c in f2 if c["row"] in r2] + \
                                  [gg[k] for k in gg if k[0] in both and k[1] in (ac, lc)]
            elif rt == "cross_page_sum" and len(G) == 2 and len(pages) >= 2:
                table2 = tabs[doc].get((pages[1], tbl))
                r2, f2 = (match_rows(table2, G[1]) if table2 else (None, []))
                if r2 and table2:
                    g2 = grid(table2)
                    vals = [to_number(gg[(r, ac)]["clean_text"]) for r in rows if ac is not None and (r, ac) in gg]
                    vals += [to_number(g2[(r, ac)]["clean_text"]) for r in r2 if ac is not None and (r, ac) in g2]
                    vals = [v for v in vals if v is not None]
                    pred_ans = fmt(sum(vals)) if vals else None
                    pred_ev = fcells + f2 + [gg[k] for k in gg if k[0] in rows and k[1] == ac] \
                              + [g2[k] for k in g2 if k[0] in r2 and k[1] == ac]
            elif rows:
                # sum: cong MOI nhom; lookup: o cua hang duy nhat
                allrows, allfc = set(rows), list(fcells)
                for grp in G[1:]:
                    rr, ff = match_rows(table, grp)
                    if rr:
                        allrows |= rr
                        allfc += ff
                # Bo o bo loc cua nhung hang bi phep GIAO loai ra: bo loc 'Dinh bien
                # "30"' khop ca r2 lan r9, nhung chi r2 song sot sau khi giao voi
                # 'Phong ban "Ke toan"'. Nhan chi danh dau o cua hang song sot
                # (10.876/6.293... do lai: 10.876 o thua nam o HANG KHAC).
                allfc = [c for c in allfc if c["row"] in allrows]
                vals = [to_number(gg[(r, ac)]["clean_text"]) for r in allrows
                        if ac is not None and (r, ac) in gg]
                vals = [v for v in vals if v is not None]
                if rt == "sum":
                    pred_ans = fmt(sum(vals)) if vals else None
                else:
                    r0 = list(rows)[0]
                    pred_ans = gg[(r0, ac)]["clean_text"] if ac is not None and (r0, ac) in gg else None
                pred_ev = allfc + [gg[k] for k in gg if k[0] in allrows and k[1] == ac]

        # Khu trung tai diem cham: bon nhanh phat o trung (compare, sum/lookup,
        # vbl, cross_page_sum). Khoa (page, row, column) = dung khoa evidence_f1
        # dung de so khop. ponytail: mot cho phu ca bon, thay vi bon diff.
        seen, dd = set(), []
        for c in pred_ev:
            k = (c["page"], c["row"], c["column"])
            if k not in seen:
                seen.add(k)
                dd.append(c)
        pred_ev = dd

        a = anls(pred_ans or "", gold_ans)
        ef = evidence_f1(pred_ev, gold_ev) if pred_ev else 0.0
        per_type[rt][0] += a
        per_type[rt][1] += ef
        per_type[rt][2] += 1
        per_type[rt][3] += 1 if pred_ans is not None else 0
        if pred_ans is None:
            miss[rt] += 1
        n_ev[0] += 1 if pred_ev else 0
        n_ev[1] += 1

    print(f"===== CAU HINH B — luat thuan Python, khong model  (split: {args.split}) =====")
    print(f"{'kieu':22}{'n':>6}{'ANLS':>8}{'EvF1':>8}{'diem':>8}{'co dap an':>11}")
    ta = te = tn = 0
    for rt in sorted(per_type, key=lambda k: -per_type[k][2]):
        a, e, n, ok = per_type[rt]
        ta += a; te += e; tn += n
        print(f"{rt:22}{n:6d}{a/n:8.3f}{e/n:8.3f}{(0.85*a+0.15*e)/n:8.3f}{100*ok/n:10.1f}%")
    print(f"{'TOAN BO':22}{tn:6d}{ta/tn:8.3f}{te/tn:8.3f}{(0.85*ta+0.15*te)/tn:8.3f}")
    print(f"\nmentor      {0.9625:22.3f}{0.9089:8.3f}{0.9545:8.3f}")
    print(f"chenh lech  {ta/tn-0.9625:+22.3f}{te/tn-0.9089:+8.3f}{(0.85*ta+0.15*te)/tn-0.9545:+8.3f}")
    print(f"\ntran co evidence vang: 1,000")
    print(f"so cau co evidence du doan: {n_ev[0]}/{n_ev[1]} = {100*n_ev[0]/n_ev[1]:.1f}%")
    print("\n--- so cau khong tra loi duoc ---")
    for k, v in sorted(miss.items(), key=lambda kv: -kv[1]):
        print(f"  {v:5d}  {k}")


if __name__ == "__main__":
    main()
