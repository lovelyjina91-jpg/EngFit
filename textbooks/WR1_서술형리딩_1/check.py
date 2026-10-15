import json, re, sys
d = json.load(open(sys.argv[1]))
ok = True
def wc(r):
    t = " ".join(p["text"] for p in r["paragraphs"])
    t = re.sub(r"\{\d:([^}]+)\}", r"\1", t).replace("[[BLANK]]", "blank blank blank")
    return len(re.sub(r"\*\*|__|\*", "", t).split())
r1, r2 = d["readings"]
w1, w2 = wc(r1), wc(r2)
print("unit", d["unit"], "R1 words", w1, "R2 words", w2)
if not 205 <= w1 <= 240: print("  !! R1 단어 수 범위 밖 (210~235)"); ok = False
if not 150 <= w2 <= 185: print("  !! R2 단어 수 범위 밖 (155~180)"); ok = False
t2 = " ".join(p["text"] for p in r2["paragraphs"])
if t2.count("[[BLANK]]") != 1: print("  !! R2 [[BLANK]] 개수", t2.count("[[BLANK]]")); ok = False
nums = re.findall(r"\{(\d):", t2)
if nums != ["1","2","3","4","5"]: print("  !! R2 번호 밑줄", nums); ok = False
if len(r1["questions"]) != 5 or len(r2["questions"]) != 4: print("  !! 문항 수"); ok = False
for r in (r1, r2):
    for q in r["questions"]:
        if q["type"] == "mc":
            if len(q["choices"]) != 5: print("  !! 선택지 5개 아님", q["kind"]); ok = False
            missing = {str(i) for i in range(1, 6)} - {str(q["answer"])} - set(q.get("wrong", {}))
            if missing: print("  !! wrong 설명 누락", q["kind"], missing); ok = False
    if len(r["translation"]) != 3: print("  !! translation 문단 수"); ok = False
for s in d["write"]["structures"]:
    if s["en"].count(" / ") != s["ko"].count(" / "): print("  !! 끊어읽기 덩어리 수 불일치:", s["en"][:40]); ok = False
print("  OK" if ok else "  FIX NEEDED")
