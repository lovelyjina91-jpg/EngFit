#!/usr/bin/env python3
"""영핏 서술형 리딩 (YF-WR) 조판기 : content/*.json → out/student.html, out/teacher.html
사용: python3 build/build.py content out
"""
import json, sys, os, re, glob, html, base64

BOOK = {"code": "WR1", "name": "영핏 서술형 리딩", "level": "1", "level_name": "FOUNDATION",
        "target": "중3 ~ 고1", "subtitle": "읽고, 고르고, 직접 쓴다"}
CIRC = "①②③④⑤⑥⑦⑧⑨⑩"
HERE = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return html.escape(s, quote=False)


def inline(s):
    """마크업 → HTML. **굵게** __밑줄__ *기울임* {n:word} 번호밑줄 [[BLANK]] 빈칸"""
    s = esc(s)
    s = re.sub(r"\{(\d):([^}]+)\}", lambda m: f'<span class="num">{CIRC[int(m.group(1))-1]}</span><u class="gu">{m.group(2)}</u>', s)
    s = s.replace("[[BLANK]]", '<span class="blank"></span>').replace("[[blank]]", '<span class="blank s"></span>')
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"__(.+?)__", r'<u class="hu">\1</u>', s)
    s = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<i>\1</i>", s)
    return s


def plain(s):
    s = re.sub(r"\{(\d):([^}]+)\}", lambda m: f"{CIRC[int(m.group(1))-1]}{m.group(2)}", s)
    s = s.replace("[[BLANK]]", "________").replace("[[blank]]", "______")
    return re.sub(r"\*\*|__|\*", "", s)


def code(u, part=None):
    c = f"YF-{BOOK['code']}-U{u:02d}"
    return f"{c}-{part}" if part else c


def logo_b64():
    p = os.path.join(HERE, "..", "assets", "cube.png")
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


CUBE = None


def head(u, d, right):
    return f'''<header class="uh"><div class="uh-l"><span class="uno">UNIT {u:02d}</span>
<span class="ugen">{esc(d["genre_en"])} · {esc(d["genre_ko"])}</span><span class="ukw">{esc(d["keywords"])}</span></div>
<div class="uh-r">{right}</div></header>'''


def foot(pg):
    return f'''<footer class="pf"><img src="{CUBE}" class="fcube"><span>{BOOK["name"]} {BOOK["level"]} · {BOOK["level_name"]}</span>
<span class="sep">·</span><span>영핏영어 지나티처</span><span class="pno">{pg}</span></footer>'''


def vbadge(c):
    return f'<div class="vb"><div class="qr">QR</div><div><div class="vb-t">VIDEO</div><div class="vb-c">{c}</div></div></div>'


def passage(r):
    out = []
    for p in r["paragraphs"]:
        out.append(f'<div class="para"><span class="role">{esc(p["role"])}</span><p>{inline(p["text"])}</p></div>')
    return "".join(out)


def words(r, compact=False):
    items = "".join(f'<div class="wd"><b>{esc(g["w"])}</b><span>{esc(g["d"])}</span></div>' for g in r["glossary"])
    return f'<div class="words{" compact" if compact else ""}"><div class="wt">WORDS <small>영영 뜻으로 익힌다</small></div><div class="wg">{items}</div></div>'


def lines(n):
    return '<div class="wl"></div>' * n


def question(i, q):
    tag = '<span class="wtag">서술형</span>' if q["type"] == "write" else ""
    h = [f'<div class="q"><div class="qh"><span class="qn">{i}</span><span class="qk">{esc(q["kind"])}</span>{tag}</div>',
         f'<div class="qp">{inline(q["prompt"])}</div>']
    if q.get("box"):
        cls = "qbox hl" if q["kind"] == "함의 추론" else "qbox"
        h.append(f'<div class="{cls}">{inline(q["box"])}</div>')
    if q.get("bank"):
        h.append(f'<div class="bank"><span>보기</span>{esc(q["bank"])}</div>')
    if q.get("condition"):
        h.append(f'<div class="bank cond"><span>조건</span>{esc(q["condition"])}</div>')
    if q["type"] == "mc":
        if all(len(c) <= 2 for c in q["choices"]):
            h.append('<div class="ch inline">' + "".join(f'<span>{c}</span>' for c in q["choices"]) + "</div>")
        else:
            h.append('<ol class="ch">' + "".join(f'<li><span class="cn">{CIRC[k]}</span>{inline(c)}</li>' for k, c in enumerate(q["choices"])) + "</ol>")
    else:
        lead = f'<span class="lead">{esc(q["lead"])}</span>' if q.get("lead") else ""
        h.append(f'<div class="wa">{lead}{lines(q.get("lines", 1))}</div>')
    h.append("</div>")
    return "".join(h)


def reading_title(r, label):
    return f'''<div class="rt"><div class="rt-l">{label}</div><div class="rt-m"><div class="rt-en">{esc(r["title_en"])}</div>
<div class="rt-ko">{esc(r["title_ko"])}</div></div></div>'''


def unit_pages(d, start):
    u = d["unit"]; r1, r2 = d["readings"]; w = d["write"]; pg = start; P = []
    # p1 READING 1 지문
    P.append(f'''<section class="page">{head(u, d, "READING 1")}<div class="body">
{reading_title(r1, "READING<br>1")}{vbadge(code(u, "R1"))}<div class="psg">{passage(r1)}</div>{words(r1)}</div>{foot(pg)}</section>''')
    pg += 1
    # p2 READING 1 문제
    qs = "".join(question(i + 1, q) for i, q in enumerate(r1["questions"]))
    P.append(f'''<section class="page">{head(u, d, "READING 1 · 수능형 3 + 서술형 2")}<div class="body">
<div class="sh">읽었으면 <b>고르고, 쓴다</b></div><div class="qs">{qs}</div></div>{foot(pg)}</section>''')
    pg += 1
    # p3 READING 2 지문 + 문제
    qs = "".join(question(i + 1, q) for i, q in enumerate(r2["questions"]))
    P.append(f'''<section class="page">{head(u, d, "READING 2")}<div class="body">
{reading_title(r2, "READING<br>2")}{vbadge(code(u, "R2"))}<div class="psg sm">{passage(r2)}</div>{words(r2, True)}
<div class="qs two">{qs}</div></div>{foot(pg)}</section>''')
    pg += 1
    # p4 FIT WRITING
    st = "".join(f'''<div class="st"><div class="st-n">{k+1}</div><div class="st-b"><div class="st-en">{inline(s["en"].replace(" / ", " "))}</div>
<div class="st-i">끊어 읽기 표시 → 우리말로 옮기기 <span class="pt">{esc(s["point"])}</span></div>{lines(1)}</div></div>''' for k, s in enumerate(w["structures"]))
    tk = "".join(question(k + 1, t | {"type": "write"}) for k, t in enumerate(w["tasks"]))
    tip = w["tip"]
    P.append(f'''<section class="page">{head(u, d, "FIT WRITING")}<div class="body">
<div class="fw-top"><div class="fw-t">FIT WRITING</div><div class="fw-s">읽은 문장을 내 손으로 다시 쓴다</div>{vbadge(code(u, "W"))}</div>
<div class="blk"><div class="blk-h"><span>A</span>구문 FIT <small>두 지문에서 뽑은 핵심 문장 · 덩어리마다 / 를 긋고 해석한다</small></div>{st}</div>
<div class="blk"><div class="blk-h"><span>B</span>서술형 FIT <small>조건을 지켜야 점수가 된다</small></div><div class="qs">{tk}</div></div>
<div class="tip"><div class="tip-h">어법 FIT · {esc(tip["title"])}</div><p>{inline(tip["body"])}</p><p class="tx">{inline(tip["extra"])}</p></div>
</div>{foot(pg)}</section>''')
    pg += 1
    return P, pg


def teacher_unit(d):
    u = d["unit"]; T = [f'<section class="tunit"><h2><span>UNIT {u:02d}</span> {esc(d["genre_en"])} · {esc(d["genre_ko"])} <small>{code(u)}</small></h2>']
    for r in d["readings"]:
        lab = "READING 1" if r["label"] == "R1" else "READING 2"
        T.append(f'<h3>{lab} · {esc(r["title_en"])} <small>{esc(r["title_ko"])}</small></h3>')
        T.append(f'<div class="ans-row">' + " ".join(
            f'<span><b>{i+1}</b> {CIRC[q["answer"]-1] if q["type"]=="mc" else "서술형"}</span>' for i, q in enumerate(r["questions"])) + '</div>')
        T.append(f'<div class="sum"><b>한 줄 요약</b> {esc(r["summary_ko"])}</div>')
        for i, q in enumerate(r["questions"]):
            a = CIRC[q["answer"]-1] if q["type"] == "mc" else esc(q["answer"])
            wr = ""
            if q.get("wrong"):
                wr = '<ul class="wr">' + "".join(f'<li>{CIRC[int(k)-1]} {esc(v)}</li>' for k, v in sorted(q["wrong"].items())) + "</ul>"
            T.append(f'<div class="tq"><div class="tq-h"><b>{i+1}. {esc(q["kind"])}</b> <span class="tans">정답 {a}</span></div><p>{esc(q["why"])}</p>{wr}</div>')
        T.append('<div class="tr"><div class="tr-h">전문 해석</div>')
        for p, ko in zip(r["paragraphs"], r["translation"]):
            T.append(f'<div class="trp"><span class="role">{esc(p["role"])}</span><p>{esc(ko)}</p></div>')
        T.append('</div><div class="ks"><div class="tr-h">핵심 구문</div>')
        for s in r["structures"]:
            T.append(f'<div class="ksi"><div class="ks-en">{inline(s["en"])}</div><div class="ks-n">{esc(s["note"])}</div></div>')
        T.append("</div>")
    w = d["write"]
    T.append('<h3>FIT WRITING</h3><div class="tq"><div class="tq-h"><b>A. 구문 FIT</b></div>')
    for k, s in enumerate(w["structures"]):
        T.append(f'<div class="ksi"><div class="ks-en">{k+1}. {esc(s["en"])}</div><div class="ks-n">{esc(s["ko"])}<br><i>{esc(s["point"])}</i></div></div>')
    T.append('</div><div class="tq"><div class="tq-h"><b>B. 서술형 FIT</b></div>')
    for k, t in enumerate(w["tasks"]):
        T.append(f'<div class="ksi"><div class="ks-en">{k+1}. {esc(t["kind"])}</div><div class="ks-n">{esc(t["answer"])}</div></div>')
    T.append("</div>")
    v = d["video"]
    T.append('<h3 class="vg">영상 촬영 가이드</h3>')
    for part, name in (("R1", "READING 1"), ("R2", "READING 2"), ("W", "FIT WRITING")):
        g = v[part]
        T.append(f'''<div class="vgb"><div class="vg-h"><b>{code(u, part)}</b> {name} <small>{"7~10분" if part=="W" else "10~15분"}</small></div>
<div class="vg-r"><span>오프닝 훅</span><p>“{esc(g["hook"])}”</p></div>
<div class="vg-r"><span>진행 순서</span><ol>{"".join(f"<li>{esc(x)}</li>" for x in g["flow"])}</ol></div>
<div class="vg-r"><span>판서</span><ul>{"".join(f"<li>{esc(x)}</li>" for x in g["board"])}</ul></div>
<div class="vg-r"><span>오답 함정</span><ul>{"".join(f"<li>{esc(x)}</li>" for x in g["traps"])}</ul></div>
<div class="vg-r"><span>마무리</span><p>“{esc(g["wrap"])}”</p></div></div>''')
    T.append("</section>")
    return "".join(T)


def cover(kind, units):
    t = "선생님용 정답 · 해설 · 촬영 가이드" if kind == "t" else "학생용"
    return f'''<section class="page cover"><div class="cv-bar"></div><div class="cv-gold"></div>
<div class="cv-top"><img src="{CUBE}"><div><b>영핏영어</b><small>YoungFit English · 지나티처</small></div></div>
<div class="cv-main"><div class="cv-ser">YF-{BOOK["code"]}</div><h1>영핏<br>서술형 리딩</h1><div class="cv-en">READING FOR WRITING</div>
<div class="cv-lv"><span>BOOK {BOOK["level"]}</span>{BOOK["level_name"]}</div>
<p class="cv-d">{BOOK["target"]} · {BOOK["subtitle"]}<br>스무 갈래 · 지문 {len(units)*2}편 · 단원마다 영상 3편</p>
<div class="cv-kind">{t}</div></div><img src="{CUBE}" class="cv-cube"><div class="cv-lines"></div></section>'''


def intro_pages(units, start):
    rows = "".join(f'<tr><td class="tn">{d["unit"]:02d}</td><td><b>{esc(d["genre_en"])}</b><small>{esc(d["genre_ko"])} — {esc(d["keywords"])}</small></td>'
                   f'<td>{esc(d["readings"][0]["title_ko"])} / {esc(d["readings"][1]["title_ko"])}</td><td class="tp">{start + 2 + i*4}</td></tr>'
                   for i, d in enumerate(units))
    howto = f'''<section class="page">{'<header class="uh"><div class="uh-l"><span class="uno">GUIDE</span><span class="ugen">이 책은 이렇게 공부합니다</span></div></header>'}<div class="body guide">
<h2 class="gh">한 단원 = 4쪽 · 영상 3편</h2>
<div class="gg"><div><b>1쪽 READING 1</b><p>도입 → 전개 → 결론, 글의 자리를 보며 읽는다. 굵은 문장은 시험에 다시 나오는 핵심 구문.</p></div>
<div><b>2쪽 수능형 3 + 서술형 2</b><p>요지·함의·일치로 이해를 확인하고, 요약문과 배열 영작은 직접 쓴다.</p></div>
<div><b>3쪽 READING 2</b><p>빈칸 추론과 어법을 고른 뒤, 틀린 어법을 고쳐 쓰고 이유까지 적는다.</p></div>
<div><b>4쪽 FIT WRITING</b><p>두 지문의 핵심 문장을 끊어 읽고, 조건 영작 · 요약 · 내 생각 쓰기로 마무리.</p></div></div>
<h2 class="gh">혼자 공부하는 순서</h2>
<ol class="gs"><li><b>QR 영상 보기</b> — 페이지 오른쪽 위 코드(예: {code(1,"R1")})가 영상 제목과 같다.</li>
<li><b>교재에 표시하기</b> — 끊어 읽기 / , 근거 문장 밑줄, 모르는 단어 동그라미.</li>
<li><b>문제 풀기</b> — 영상에서 “일시정지” 나오면 멈추고 먼저 푼다.</li>
<li><b>오답 다시 보기</b> — 틀린 문제는 정답 근거 문장을 찾아 노트에 옮겨 쓴다.</li></ol>
<h2 class="gh">기호</h2><div class="gk"><span><b>굵은 글씨</b> 핵심 구문</span><span><u>밑줄</u> 문제 대상</span><span class="wtag">서술형</span> 직접 쓰는 문항</div>
</div>{foot(start)}</section>'''
    toc = f'''<section class="page"><header class="uh"><div class="uh-l"><span class="uno">CONTENTS</span><span class="ugen">차례</span></div></header><div class="body">
<table class="toc"><thead><tr><th>UNIT</th><th>갈래</th><th>READING 1 / 2</th><th>쪽</th></tr></thead><tbody>{rows}</tbody></table></div>{foot(start+1)}</section>'''
    return [howto, toc], start + 2


def doc(title, css, body, fit=True):
    js = open(os.path.join(HERE, "fit.js")).read() if fit else ""
    return f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>{body}<script>{js}</script></body></html>'


def main(src, out):
    global CUBE
    CUBE = logo_b64()
    os.makedirs(out, exist_ok=True)
    units = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(src, "unit*.json")))]
    css = open(os.path.join(HERE, "book.css")).read()
    fonts = os.path.join(HERE, "..", "fonts")
    css = css.replace("FONTDIR", "file://" + os.path.abspath(fonts))
    pages = [cover("s", units)]
    intro, pg = intro_pages(units, 2)
    pages += intro
    for d in units:
        P, pg = unit_pages(d, pg)
        pages += P
    open(os.path.join(out, "student.html"), "w").write(doc("영핏 서술형 리딩 1 학생용", css, "".join(pages)))
    tb = f'<div class="tcv"><img src="{CUBE}"><div><b>영핏 서술형 리딩 {BOOK["level"]} · {BOOK["level_name"]}</b><small>선생님용 정답 · 해설 · 영상 촬영 가이드 · YF-{BOOK["code"]}</small></div></div>' + "".join(teacher_unit(d) for d in units)
    open(os.path.join(out, "teacher.html"), "w").write(doc("영핏 서술형 리딩 1 선생님용", css + "@page{size:A4;margin:13mm 17mm 16mm}", f'<div class="teacher">{tb}</div>', fit=False))
    open(os.path.join(out, "teacher_cover.html"), "w").write(doc("선생님용 표지", css, cover("t", units), fit=False))
    print(f"units={len(units)} student_pages={len(pages)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
