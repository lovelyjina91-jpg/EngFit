#!/usr/bin/env python3
"""영핏 서술형 리딩 영상 슬라이드 생성기
사용: python3 gen_slides.py <content_dir> <out_dir> <BOOKCODE e.g. WR1>
단원 JSON 하나당 R1 / R2 / W 슬라이드 HTML 3개 생성 (SR1 슬라이드와 같은 엔진·디자인)
"""
import json, sys, os, re, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = open(os.path.join(HERE, "head.txt")).read()
SCRIPT = open(os.path.join(HERE, "script.txt")).read()
LOGO = open(os.path.join(HERE, "logo.txt")).read()
CIRC = "①②③④⑤"
LEVEL = {"WR1": ("1", "FOUNDATION"), "WR2": ("2", "CORE"), "WR3": ("3", "ADVANCED")}

EXTRA_CSS = """
/* ---------- 영핏 서술형 리딩 추가 ---------- */
.prow .rl{display:inline-block; text-indent:0; font-size:1.45rem; font-weight:800; color:var(--c1); border:.14rem solid var(--c1); border-radius:.5rem; padding:0 .6rem; margin-right:.8rem; vertical-align:.3rem;}
.pbox.wr .prow{font-size:2.15rem; line-height:1.42; padding-left:0; text-indent:0; margin-bottom:.55rem;}
.pbox.wr.s .prow{font-size:1.95rem; line-height:1.36; margin-bottom:.4rem;}
.pbox.wr b{color:var(--sV); font-weight:800;}
.pbox.wr .ul,.qbox .ul{text-decoration:underline; text-underline-offset:.35rem; text-decoration-thickness:.16rem; text-decoration-color:var(--ink);}
.mkn{display:inline-block; font-size:1.5rem; font-weight:900; color:#fff; background:var(--purple); border-radius:50%; width:2.2rem; height:2.2rem; line-height:2.2rem; text-align:center; margin:0 .3rem 0 .1rem; vertical-align:.25rem; text-indent:0;}
.blank{width:16rem;}
.given2{font-size:2.15rem; font-weight:700; border:.16rem solid var(--gold); background:#FFF8E8; border-radius:.9rem; padding:.8rem 1.4rem; margin-bottom:.9rem; max-width:86rem; line-height:1.45;}
.given2 .lb2{display:inline-block; font-size:1.6rem; font-weight:800; color:#fff; background:var(--navy); border-radius:.5rem; padding:.1rem .7rem; margin-right:.8rem; vertical-align:.15rem;}
.wline{height:3.4rem; border-bottom:.16rem dashed #AEB6C6; max-width:86rem; margin-bottom:.4rem;}
.answer .why{display:block; margin-top:.4rem; font-size:1.9rem; color:var(--dim); font-weight:600;}
.wronglist{max-width:86rem; margin-top:.8rem;}
.wronglist div{font-size:1.85rem; font-weight:600; color:var(--dim); line-height:1.38; margin-bottom:.25rem;}
.wronglist div b{color:var(--coral);}
.trbox{max-width:86rem; background:#fff; border:.14rem solid var(--line); border-left:.55rem solid var(--teal); border-radius:1.2rem; padding:1rem 1.6rem; margin-top:.7rem;}
.trbox .tr{font-size:1.95rem; font-weight:600; line-height:1.42; color:var(--ink2);}
.hook{font-size:3.4rem; font-weight:800; line-height:1.38; color:var(--navy); max-width:80rem; background:#fff; border:.16rem solid var(--gold); border-radius:1.4rem; padding:2rem 2.4rem; box-shadow:0 .8rem 2rem rgba(27,41,112,.08);}
.chunkrow{display:flex; flex-wrap:wrap; gap:.6rem; max-width:86rem; margin-bottom:.6rem;}
.chunkrow .ck{background:#fff; border:.14rem solid var(--line); border-bottom:.4rem solid var(--c1); border-radius:.8rem; padding:.45rem .9rem; font-size:2.2rem; font-weight:700; color:var(--ink);}
.chunkrow.ko .ck{border-bottom-color:var(--gold); font-size:1.95rem; color:var(--ink2);}
"""


def esc(s):
    return html.escape(s, quote=False)


def mark(s):
    s = esc(s)
    s = re.sub(r"\{(\d):([^}]+)\}", lambda m: f'<span class="mkn">{m.group(1)}</span><span class="ul">{m.group(2)}</span>', s)
    s = s.replace("[[BLANK]]", '<span class="blank"></span>').replace("[[blank]]", '<span class="blank" style="width:10rem"></span>')
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"__(.+?)__", r'<span class="ul">\1</span>', s)
    s = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<i>\1</i>", s)
    return s


def plain(s):
    s = re.sub(r"\{(\d):([^}]+)\}", lambda m: m.group(2), s)
    return re.sub(r"\*\*|__|\*|\[\[BLANK\]\]|\[\[blank\]\]", "", s)


def sentences(text):
    # 마크업 안에서는 자르지 않도록 단순 분리 후 bold 균형 맞추기
    parts, last = [], 0
    for m in re.finditer(r'[.!?]["”]?(?:\*\*|__)?(\s+)(?=["“*_A-Z(])', text):
        parts.append(text[last:m.start(1)]); last = m.end(1)
    parts.append(text[last:])
    out, buf = [], ""
    for p in parts:
        buf = (buf + " " + p).strip() if buf else p
        if buf.count("**") % 2 == 0 and buf.count("__") % 2 == 0:
            out.append(buf); buf = ""
    if buf: out.append(buf)
    return out


def slide(inner, accent="read", cls=""):
    return f'<section class="slide {cls}" data-accent="{accent}"><div class="wrap">{inner}</div></section>'


def idhead(track):
    return f'<div class="idhead"><img class="logo" alt="영핏영어" src="{LOGO}"><div><div class="brandline">영핏영어 · 지나티처</div><div class="trackline">{track}</div></div></div>'


def page(title, slides):
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)} | 영핏영어</title>", HEAD)
    body = "".join(slides)
    return f'{head}{EXTRA_CSS}</style></head><body><div id="stage">{body}<div id="zoneL"></div><div id="zoneR"></div><div id="bar"></div><div id="num">1 / {len(slides)}</div></div>{SCRIPT}'


def q_slides(tagbase, i, q, passage_hint=None):
    S = []
    tag = f'<div class="tag">{tagbase} · {i}번 {esc(q["kind"])}</div>'
    head = f'<div class="qbox"><div class="q">{i}. {mark(q["prompt"])}</div></div>'
    if q.get("box"):
        head += f'<div class="given2 r">{mark(q["box"])}</div>'
    if passage_hint and q["kind"] in ("어법", "빈칸 추론"):
        key = "{" if q["kind"] == "어법" else "[[BLANK]]"
        ctx = [x for p in passage_hint for x in sentences(p["text"]) if key in x]
        if ctx:
            head += '<div class="pbox wr s r">' + "".join(f'<div class="prow">{mark(x)}</div>' for x in ctx) + '</div><div style="height:.8rem"></div>'
    if q.get("bank"):
        head += f'<div class="given2 r"><span class="lb2">보기</span>{esc(q["bank"])}</div>'
    if q.get("condition"):
        head += f'<div class="given2 r"><span class="lb2">조건</span>{esc(q["condition"])}</div>'
    if q["type"] == "mc":
        if all(len(c) <= 2 for c in q["choices"]):
            chs = '<div class="chs" style="grid-template-columns:repeat(5,1fr)">' + "".join(f'<div class="ch r" style="text-align:center"><span class="cn">{c}</span></div>' for c in q["choices"]) + "</div>"
        else:
            one = " one" if max(len(c) for c in q["choices"]) > 34 else ""
            chs = f'<div class="chs{one}">' + "".join(f'<div class="ch r"><span class="cn">{CIRC[k]}</span>{mark(c)}</div>' for k, c in enumerate(q["choices"])) + "</div>"
        pause = '<div class="point r"><span class="lb">일시정지</span>영상을 멈추고 먼저 풀어 보세요!</div>'
        S.append(slide(tag + head + chs + pause, "gram", "tight"))
        ans = f'<div class="answer r"><span class="lb">정답 {CIRC[q["answer"]-1]}</span>{esc(q["why"])}</div>'
        wr = ""
        if q.get("wrong"):
            wr = '<div class="wronglist">' + "".join(f'<div class="r"><b>{CIRC[int(k)-1]}</b> {esc(v)}</div>' for k, v in sorted(q["wrong"].items())) + "</div>"
        S.append(slide(f'<div class="tag">{tagbase} · {i}번 해설</div><h2>정답 <em>근거</em> 확인</h2>' + ans + wr, "gram", "tight"))
    else:
        lines = '<div class="wline"></div>' * min(q.get("lines", 1), 2)
        pause = '<div class="point r"><span class="lb">일시정지</span>교재에 직접 써 보고 넘어가세요!</div>'
        S.append(slide(tag + head + lines + pause, "gram", "tight"))
        S.append(slide(f'<div class="tag">{tagbase} · {i}번 모범 답안</div><h2>이렇게 <em>씁니다</em></h2>'
                       f'<div class="answer r"><span class="lb">답안</span>{esc(q["answer"])}<span class="why">{esc(q.get("why",""))}</span></div>', "gram", "tight"))
    return S


def reading_video(d, r, part, book, nxt):
    u = d["unit"]; code = f"YF-{book}-U{u:02d}-{part}"
    lv, ln = LEVEL[book]
    track = f"영핏 서술형 리딩 {lv} · {code}"
    lab = "READING 1" if part == "R1" else "READING 2"
    v = d["video"][part]
    S = []
    S.append(slide(idhead(track) + f'<h1>Unit {u:02d} {esc(d["genre_en"])}<br><span>{lab}</span></h1>'
                   f'<div class="h1sub r">{esc(r["title_en"])} — {esc(r["title_ko"])}</div>'
                   f'<div class="pills"><div class="pill on1 r">{esc(d["genre_ko"])} · {esc(d["keywords"])}</div><div class="pill on2 r">도입 → 전개 → 결론</div></div>', "read", "intro"))
    S.append(slide(f'<div class="tag">오프닝</div><div class="hook r">“{esc(v["hook"])}”</div>', "know"))
    kinds = " · ".join(q["kind"] for q in r["questions"])
    S.append(slide('<div class="tag">오늘의 목표</div><h2>이 3 가지만 <em>가져갑시다</em></h2>'
                   f'<div class="goal r"><div class="gn">1</div><div class="gt">문제를 먼저 읽고 <b>무엇을 찾는지</b> 정한다 <span style="color:var(--dim);font-size:2rem">({esc(kinds)})</span></div></div>'
                   '<div class="goal r"><div class="gn">2</div><div class="gt"><b>도입 · 전개 · 결론</b>의 자리를 나누어 읽는다</div></div>'
                   '<div class="goal r"><div class="gn">3</div><div class="gt">정답 <b>근거 문장</b>에 밑줄을 긋고, 서술형은 <b>직접 쓴다</b></div></div>'))
    small = " s" if part == "R2" else ""
    for p, ko in zip(r["paragraphs"], r["translation"]):
        rows = "".join(f'<div class="prow r">{mark(s)}</div>' for s in sentences(p["text"]))
        S.append(slide(f'<div class="tag">{lab} · {esc(p["role"])}</div><div class="pbox wr{small}"><div class="prow"><span class="rl">{esc(p["role"])}</span></div>{rows}</div>'
                       f'<div class="trbox r"><div class="tr">{esc(ko)}</div></div>', "read", "tight"))
    sent = "".join(f'<div class="sent r"><div class="line en">{mark(s["en"])}</div><div class="verdict">{esc(s["note"])}</div></div>' for s in r["structures"])
    S.append(slide(f'<div class="tag">{lab} · 핵심 구문</div><h2>굵은 문장 <em>다시 보기</em></h2>{sent}', "gram", "tight chunk"))
    for i, q in enumerate(r["questions"]):
        S += q_slides(lab, i + 1, q, r["paragraphs"])
    board = "".join(f'<li class="r">{esc(x)}</li>' for x in v["board"])
    traps = "".join(f'<li class="r">{esc(x)}</li>' for x in v["traps"])
    S.append(slide('<div class="tag">오늘의 정리</div><h2>판서와 <em>오답 함정</em></h2>'
                   f'<div class="sumwrap"><div class="sumcol a"><h3>판서</h3><ul>{board}</ul></div><div class="sumcol b"><h3>오답 함정</h3><ul>{traps}</ul></div></div>', "sum"))
    kw = "".join(f'<span><b class="en">{esc(g["w"])}</b> {esc(g["d"])}</span>' for g in r["glossary"])
    S.append(slide(f'<div class="tag">WORDS</div><h2>지문 속 <em>핵심 단어</em></h2><div class="kw r">{kw}</div><div class="closing r">{esc(d["readings"][0 if part=="R1" else 1]["summary_ko"])}</div>', "sum"))
    nxtxt = "READING 2" if part == "R1" else "FIT WRITING"
    S.append(slide(idhead(track) + f'<div class="obig">{esc(v["wrap"])}</div>'
                   f'<div class="hw"><div class="hwcard r"><div class="ht">HOMEWORK</div><div class="hb">틀린 문제 근거 문장 다시 찾기<br>WORDS 영영 뜻 암기</div></div>'
                   f'<div class="hwcard r"><div class="ht">NEXT</div><div class="hb">Unit {u:02d} {nxtxt}</div></div></div>', "read", "outro"))
    return code, f"Unit {u:02d} {d['genre_en']} · {d['genre_ko']} · {lab} {r['title_ko']}", page(f"{code} {lab}", S)


def write_video(d, book, nxt):
    u = d["unit"]; code = f"YF-{book}-U{u:02d}-W"
    lv, ln = LEVEL[book]
    track = f"영핏 서술형 리딩 {lv} · {code}"
    w = d["write"]; v = d["video"]["W"]
    S = []
    S.append(slide(idhead(track) + f'<h1>Unit {u:02d} {esc(d["genre_en"])}<br><span>FIT WRITING</span></h1>'
                   f'<div class="h1sub r">읽은 문장을 내 손으로 다시 쓴다</div>'
                   f'<div class="pills"><div class="pill on1 r">구문 FIT · 서술형 FIT</div><div class="pill on2 r">어법 FIT · {esc(w["tip"]["title"].split("—")[0].strip())}</div></div>', "read", "intro"))
    S.append(slide(f'<div class="tag">오프닝</div><div class="hook r">“{esc(v["hook"])}”</div>', "know"))
    for k, s in enumerate(w["structures"]):
        en = [c.strip() for c in s["en"].split(" / ")]
        ko = [c.strip() for c in s["ko"].split(" / ")]
        S.append(slide(f'<div class="tag">A. 구문 FIT {k+1}</div><h2>끊어 읽고 <em>옮기기</em></h2>'
                       f'<div class="sent"><div class="line en">{mark(" ".join(en))}</div></div>'
                       '<div class="point r"><span class="lb">일시정지</span>덩어리마다 / 를 긋고 해석해 보세요!</div>'
                       f'<div class="chunkrow r">' + "".join(f'<span class="ck">{mark(c)}</span>' for c in en) + "</div>"
                       f'<div class="chunkrow ko r">' + "".join(f'<span class="ck">{esc(c)}</span>' for c in ko) + "</div>"
                       f'<div class="answer r"><span class="lb">포인트</span>{esc(s["point"])}</div>', "gram", "tight"))
    for k, t in enumerate(w["tasks"]):
        S += q_slides("B. 서술형 FIT", k + 1, dict(t, type="write"))
    tip = w["tip"]
    S.append(slide(f'<div class="tag">C. 어법 FIT</div><h2>{esc(tip["title"])}</h2>'
                   f'<div class="card r">{mark(tip["body"])}</div><div class="warn r">{mark(tip["extra"])}</div>', "gram", "tight"))
    board = "".join(f'<li class="r">{esc(x)}</li>' for x in v["board"])
    traps = "".join(f'<li class="r">{esc(x)}</li>' for x in v["traps"])
    S.append(slide('<div class="tag">오늘의 정리</div><h2>판서와 <em>감점 함정</em></h2>'
                   f'<div class="sumwrap"><div class="sumcol a"><h3>판서</h3><ul>{board}</ul></div><div class="sumcol b"><h3>감점 함정</h3><ul>{traps}</ul></div></div>', "sum"))
    nx = f"Unit {nxt['unit']:02d} {nxt['genre_en']} READING 1" if nxt else "교재 완주! 틀린 문제 총정리"
    S.append(slide(idhead(track) + f'<div class="obig">{esc(v["wrap"])}</div>'
                   f'<div class="hw"><div class="hwcard r"><div class="ht">HOMEWORK</div><div class="hb">서술형 FIT 다시 쓰기<br>어법 FIT 예문 2개 만들기</div></div>'
                   f'<div class="hwcard r"><div class="ht">NEXT</div><div class="hb">{esc(nx)}</div></div></div>', "read", "outro"))
    return code, f"Unit {u:02d} {d['genre_en']} · {d['genre_ko']} · FIT WRITING", page(f"{code} FIT WRITING", S)


def main(src, out, book):
    os.makedirs(out, exist_ok=True)
    units = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(src, "unit*.json")))]
    rows = []
    for i, d in enumerate(units):
        nxt = units[i + 1] if i + 1 < len(units) else None
        for part, r in (("R1", d["readings"][0]), ("R2", d["readings"][1])):
            code, label, h = reading_video(d, r, part, book, nxt)
            open(os.path.join(out, code + ".html"), "w").write(h); rows.append((code, label))
        code, label, h = write_video(d, book, nxt)
        open(os.path.join(out, code + ".html"), "w").write(h); rows.append((code, label))
    json.dump(rows, open(os.path.join(out, "_index.json"), "w"), ensure_ascii=False, indent=0)
    print(book, len(rows), "files")


if __name__ == "__main__":
    main(*sys.argv[1:4])
