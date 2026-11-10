"""영핏 인쇄물 생성기 — 데일리 10 (영핏 로고 가득 디자인, 2026-10-15~) + 종류별 색 (2026-10-26)

usage:
  python3 -I records/tools/worksheet.py <q 폴더(ws1111)> <로고 폴더> <출력.pdf> --date 2026-11-11 [--kind daily] [--order 이름,이름,...]

- q 폴더의 q_<이름>_<MMDD>.json 을 읽어 학생 1명 = A4 1장(앞면 문제 · 뒷면 그 학생 정답)으로 만든다.
- 로고 폴더: yeongpit.png(영핏), englishfit.png(English Fit), cube.png(큐브) — 노션 「영핏 데일리 수업 준비」 페이지 이미지 2개 + assets/engfit-cube.png
- q json: {"name","subtitle","memo","items":[{"no","kind","tag","inst","text","hint","answer","point"}]}
- ⭐ TOP 1: 빈칸은 `______` 하나, 답 줄은 문항마다 1줄만 (text에 빈칸이 없으면 답 줄 1줄을 그림)
- 종류별 색 (--kind): daily 남색 / homework 초록 / clinic 빨강 / naesin 보라 / study 파랑.
  데일리가 아니면 헤더 오른쪽 종류 배지 + 이름칸 위 안내 한 줄 + 쪽 둘레 종류색 테두리 2mm. 정답지도 같은 색.
- 렌더링: HTML → Playwright(Chromium) PDF. 한 쪽 넘침 검사(--check)로 꼬리말 가림 여부 확인.
"""
import argparse, base64, glob, html, json, os, re, sys, datetime

KINDS = {
    'daily':    dict(main='#1e2b55', acc='#f4a100', light='#fff6dc', label='DAILY 10', ko='영핏 데일리 10', badge=None),
    'homework': dict(main='#0b6e4f', acc='#ffcf33', light='#e6f5ee', label='HOMEWORK', ko='영핏 숙제', badge='숙제 HOMEWORK', note='★ 이건 숙제 프린트예요 (초록 테두리) · 데일리 테스트(남색 종이)와 섞지 말고 따로 제출!'),
    'clinic':   dict(main='#b3001b', acc='#ffd23f', light='#fbe4e6', label='CLINIC', ko='영핏 클리닉', badge='클리닉 CLINIC', note='★ 이건 클리닉 프린트예요 (빨강 테두리) · 데일리 테스트(남색 종이)와 섞지 말고 따로 제출!'),
    'naesin':   dict(main='#5552a5', acc='#f4a100', light='#ecebf7', label='NAESIN', ko='영핏 내신', badge='내신 NAESIN', note='★ 이건 내신 프린트예요 (보라 테두리) · 데일리 테스트(남색 종이)와 섞지 말고 따로 제출!'),
    'study':    dict(main='#0066a8', acc='#f4a100', light='#e3f0fa', label='STUDY', ko='영핏 스터디', badge='스터디 STUDY', note='★ 이건 스터디 프린트예요 (파랑 테두리) · 데일리 테스트(남색 종이)와 섞지 말고 따로 제출!'),
}
DOW = '월화수목금토일'
BLANK = '______'


def b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


def esc(s):
    return html.escape(s or '')


def fmt_text(s):
    """빈칸(언더바 3개 이상)은 모두 한 칸짜리 빈칸 하나로 — TOP 1 규칙"""
    s = esc(s)
    s = re.sub(r'_{3,}(\s*_{3,})*', '<span class="blank"></span>', s)
    return s


CSS = r"""
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Pretendard', 'Noto Sans CJK KR', 'WenQuanYi Zen Hei', sans-serif; color: #1f2433; font-size: 12px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; page-break-after: always; display: flex; flex-direction: column; background: #fff; }
.page.framed { border: 2mm solid var(--main); }
.wm { position: absolute; left: 50%; top: 52%; width: 120mm; transform: translate(-50%, -50%); opacity: .07; z-index: 0; pointer-events: none; }
.stripe { height: 3.2mm; background: repeating-linear-gradient(-45deg, var(--main) 0 4mm, var(--acc) 4mm 8mm); flex: none; }
.head { background: var(--main); color: #fff; display: flex; align-items: center; padding: 3mm 6mm; gap: 5mm; flex: none; position: relative; z-index: 1; }
.lbox { background: #fff; border-radius: 3mm; height: 17mm; display: flex; align-items: center; justify-content: center; padding: 1.2mm 2mm; flex: none; }
.lbox img { height: 14.5mm; }
.htxt { flex: 1; }
.htxt .en { color: var(--acc); font-size: 9.5px; font-weight: 800; letter-spacing: 2.6px; }
.htxt h1 { font-size: 21px; font-weight: 800; letter-spacing: -.3px; margin: .6mm 0; }
.htxt .sub { font-size: 10.5px; color: #d8def0; }
.badge { position: absolute; right: 36mm; top: 3mm; background: var(--acc); color: var(--main); font-weight: 800; font-size: 10px; padding: .8mm 2.6mm; border-radius: 9mm; }
.cubes { display: flex; justify-content: space-between; padding: 1.4mm 6mm; flex: none; position: relative; z-index: 1; }
.cubes img { height: 5.2mm; }
.cubes img:nth-child(odd) { opacity: .85; } .cubes img:nth-child(even) { opacity: .35; }
.body { flex: 1; padding: 1.5mm 8mm 0; position: relative; z-index: 1; display: flex; flex-direction: column; min-height: 0; }
.note { background: var(--light); color: var(--main); font-weight: 700; font-size: 11px; padding: 1.4mm 3mm; border-radius: 1.6mm; margin-bottom: 1.6mm; }
.namerow { display: flex; gap: 3mm; margin-bottom: 1.6mm; }
.namerow div { border: 1px solid #cfd5e3; border-radius: 1.6mm; padding: 1.6mm 3mm; font-size: 11.5px; }
.namerow .nm { flex: 1; } .namerow b { color: var(--main); font-weight: 800; margin-left: 2mm; font-size: 13px; }
.guide { font-size: 10px; color: #5a6275; margin-bottom: 1.4mm; }
.q { display: flex; gap: 2.6mm; padding: 1.55mm 0; border-bottom: 1px dashed #dfe3ec; }
.q:last-child { border-bottom: none; }
.num { flex: none; width: 6.2mm; height: 6.2mm; border-radius: 50%; background: var(--main); color: #fff; font-weight: 800; font-size: 11.5px; display: flex; align-items: center; justify-content: center; margin-top: .3mm; }
.qm { flex: 1; min-width: 0; }
.qtop { display: flex; align-items: baseline; gap: 2mm; margin-bottom: .7mm; }
.tag { flex: none; background: #fff3c4; color: #7a5a00; font-size: 9px; font-weight: 700; padding: .2mm 1.8mm; border-radius: 1.2mm; }
.inst { font-size: 12.5px; font-weight: 700; color: #1f2433; }
.txt { font-size: 12.5px; line-height: 1.5; }
.hint { font-size: 10px; color: #6b7386; margin-left: 1.2mm; }
.blank { display: inline-block; width: 26mm; border-bottom: 1.3px solid #1f2433; height: 1em; vertical-align: -2px; margin: 0 1mm; }
.aline { border-bottom: 1.2px solid #8d95a8; height: 7.2mm; margin-top: .4mm; }
.mr { flex: none; width: 13mm; text-align: center; font-size: 9px; color: #7a8296; }
.mr .box { width: 5.2mm; height: 5.2mm; border: 1.4px solid #9aa2b5; border-radius: 1.2mm; margin: .6mm auto 0; }
.foot { flex: none; position: relative; z-index: 1; }
.fband { background: var(--main); color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 2mm 6mm; }
.fband .lbox { height: 12mm; } .fband .lbox img { height: 10mm; }
.slogan { text-align: center; }
.slogan .s1 { font-size: 16px; font-weight: 800; letter-spacing: 3px; }
.slogan .s1 em { color: var(--acc); font-style: normal; }
.slogan .s2 { font-size: 9px; color: #c9d0e4; margin-top: .6mm; letter-spacing: 1px; }
table.ans { width: 100%; border-collapse: collapse; margin-top: 2mm; }
table.ans th { background: var(--main); color: #fff; font-size: 11px; padding: 1.8mm; }
table.ans td { border-bottom: 1px solid #e3e7ef; padding: 2.1mm 2mm; vertical-align: top; font-size: 11.5px; }
table.ans td.n { width: 9mm; text-align: center; font-weight: 800; color: var(--main); }
table.ans td.a { width: 64mm; font-weight: 800; color: #b87900; }
table.ans td.k { width: 26mm; font-size: 9.5px; color: #5a6275; }
table.ans td.p { font-size: 10.5px; color: #3d4457; }
.memo { margin-top: 3mm; background: #fff8e6; border-left: 1.4mm solid var(--acc); padding: 2.4mm 3mm; font-size: 10.5px; line-height: 1.55; }
.memo b { color: var(--main); }
"""


def header(K, logos, title_en, title_ko, sub):
    badge = f'<div class="badge">{esc(K["badge"])}</div>' if K.get('badge') else ''
    return f'''<div class="stripe"></div>
<div class="head"><div class="lbox"><img src="{logos['yeongpit']}"></div>
<div class="htxt"><div class="en">{esc(title_en)}</div><h1>{esc(title_ko)}</h1><div class="sub">{esc(sub)}</div></div>
{badge}<div class="lbox"><img src="{logos['englishfit']}"></div></div>
<div class="cubes">{''.join(f'<img src="{logos["cube"]}">' for _ in range(22))}</div>'''


def footer(logos):
    return f'''<div class="foot"><div class="cubes">{''.join(f'<img src="{logos["cube"]}">' for _ in range(22))}</div>
<div class="fband"><div class="lbox"><img src="{logos['yeongpit']}"></div>
<div class="slogan"><div class="s1"><em>영</em>어를 <em>핏</em>하다</div><div class="s2">영핏영어교습소 · ENGLISH FIT</div></div>
<div class="lbox"><img src="{logos['englishfit']}"></div></div><div class="stripe"></div></div>'''


def front(q, K, logos, datestr, kind):
    items = []
    for it in q['items']:
        text = it.get('text', '')
        has_blank = bool(re.search(r'_{3,}', text))
        hint = f'<span class="hint">{esc(it.get("hint"))}</span>' if it.get('hint') else ''
        line = '' if has_blank else '<div class="aline"></div>'
        tag = esc(it.get('kind', '')) + (' · ' + esc(it['tag']) if it.get('tag') else '')
        items.append(f'''<div class="q"><div class="num">{it["no"]}</div><div class="qm">
<div class="qtop"><span class="tag">{tag}</span><span class="inst">{esc(it.get("inst"))}</span></div>
<div class="txt">{fmt_text(text)}{hint}</div>{line}</div>
<div class="mr">🤔 모름<div class="box"></div></div></div>''')
    note = f'<div class="note">{esc(K["note"])}</div>' if K.get('note') else ''
    framed = ' framed' if kind != 'daily' else ''
    return f'''<section class="page{framed}"><img class="wm" src="{logos['englishfit']}">
{header(K, logos, 'ENGLISH FIT · ' + K['label'], K['ko'], q.get('subtitle', '') + ' · ' + datestr)}
<div class="body">{note}<div class="namerow"><div class="nm">이름<b>{esc(q['name'])}</b></div><div>시작 ____ : ____</div><div>점수 ______ / {len(q['items'])}</div></div>
<div class="guide">✏️ 답을 쓰고, 모르는 문제는 찍지 말고 오른쪽 🤔 모름 칸에 체크해요. 모름 체크는 감점이 아니라 다음 수업 재료예요!</div>
<div class="qs">{''.join(items)}</div></div>{footer(logos)}</section>'''


def back(q, K, logos, datestr, kind):
    rows = ''.join(f'<tr><td class="n">{it["no"]}</td><td class="a">{esc(it.get("answer"))}</td><td class="k">{esc(it.get("kind"))}<br>{esc(it.get("tag"))}</td><td class="p">{esc(it.get("point"))}</td></tr>' for it in q['items'])
    memo = f'<div class="memo"><b>선생님 메모</b> · {esc(q.get("memo"))} 🤔 모름 체크한 번호를 보면 다음 수업 출발점을 정할 수 있어요.</div>' if q.get('memo') else ''
    framed = ' framed' if kind != 'daily' else ''
    return f'''<section class="page{framed}"><img class="wm" src="{logos['englishfit']}">
{header(K, logos, 'ENGLISH FIT · ANSWER KEY', '정답 & 해설', q['name'] + ' · ' + K['ko'] + ' · ' + datestr)}
<div class="body"><table class="ans"><tr><th>번호</th><th>정답</th><th>유형</th><th>포인트</th></tr>{rows}</table>{memo}</div>{footer(logos)}</section>'''


def build_html(qs, logo_dir, datestr, kind='daily'):
    K = KINDS[kind]
    logos = {k: b64(os.path.join(logo_dir, k + '.png')) for k in ('yeongpit', 'englishfit', 'cube')}
    pages = ''.join(front(q, K, logos, datestr, kind) + back(q, K, logos, datestr, kind) for q in qs)
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>:root{{--main:{K['main']};--acc:{K['acc']};--light:{K['light']}}}{CSS}</style></head><body>{pages}</body></html>'''


NODE_RENDER = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto('file://' + src, { waitUntil: 'networkidle' });
  await pg.evaluate(() => document.fonts.ready);
  await pg.emulateMedia({ media: 'print' });
  // 문항 영역이 꼬리말에 가려지지 않는지 (body 넘침 검사)
  const bad = await pg.evaluate(() => [...document.querySelectorAll('.page')].map((p, i) => {
    const q = p.querySelector('.body'); return q.scrollHeight > q.clientHeight + 1 ? i + 1 : 0; }).filter(x => x));
  await pg.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log(JSON.stringify(bad));
})();
"""


def render(html_str, out_pdf, check=True):
    """Playwright(Node, 미리 설치된 Chromium)로 PDF 저장. 넘친 쪽 번호 목록을 돌려준다."""
    import subprocess, tempfile
    tmp = os.path.abspath(out_pdf[:-4] + '.html')
    open(tmp, 'w').write(html_str)
    js = os.path.join(tempfile.mkdtemp(), 'render.js')
    open(js, 'w').write(NODE_RENDER)
    env = dict(os.environ)
    gm = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    env['NODE_PATH'] = gm + (':' + env['NODE_PATH'] if env.get('NODE_PATH') else '')
    r = subprocess.run(['node', js, tmp, os.path.abspath(out_pdf)], capture_output=True, text=True, env=env)
    if r.returncode:
        sys.exit('렌더링 실패: ' + r.stderr[-800:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def datestr_of(d):
    dt = datetime.date.fromisoformat(d)
    return f'{dt.year}. {dt.month}. {dt.day} ({DOW[dt.weekday()]})'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('qdir'); ap.add_argument('logos'); ap.add_argument('out')
    ap.add_argument('--date', required=True)
    ap.add_argument('--kind', default='daily', choices=list(KINDS))
    ap.add_argument('--order', default='')
    a = ap.parse_args()
    files = glob.glob(os.path.join(a.qdir, 'q_*.json'))
    qs = {json.load(open(f))['name']: json.load(open(f)) for f in files}
    order = [n for n in a.order.split(',') if n] or sorted(qs)
    missing = [n for n in order if n not in qs]
    if missing:
        sys.exit(f'문항 파일 없음: {missing}')
    for n in order:
        assert len(qs[n]['items']) == 10 or a.kind != 'daily', f'{n}: 문항 {len(qs[n]["items"])}개'
        for it in qs[n]['items']:
            if re.search(r'_{3,}\s+_{3,}', it.get('text', '')):
                sys.exit(f'TOP 1 위반(빈칸 여러 개): {n} {it["no"]}번')
    bad = render(build_html([qs[n] for n in order], a.logos, datestr_of(a.date), a.kind), a.out)
    print(f'{a.out}: {len(order)}명 · {len(order)*2}쪽')
    if bad:
        print('⚠️ 넘친 쪽(꼬리말에 가려짐):', bad); sys.exit(2)
    print('넘친 쪽 없음 (문항 10개 + 모름 칸 한 장에 들어감)')


if __name__ == '__main__':
    main()
