"""영핏 등원 브리핑 PDF — 첫 쪽 전체 요약표 + 학생 1명당 1쪽 (영핏 로고 디자인, worksheet.py와 같은 위·아래 모양)

usage:
  python3 -I records/tools/daily_brief.py <brief.json> <로고 폴더> <출력.pdf> --date 2026-11-11 [--qdir ws1111]

brief.json (스크래치 폴더에만 둔다 — 학생 데이터):
  [{"name","grade","time","out","seen":"4/4","fixed":"정해진 시간표…","book":"교재","progress":"교재 진도",
    "weak":["개념 정답률",…], "improving":[…], "recent":"최근 틀린 문항 요약", "note":"선생님 참고", "daily":true}]
--qdir 를 주면 그 학생의 오늘 데일리 10 구성(번호·유형·개념)을 쪽마다 붙인다.
"""
import argparse, json, os, sys, glob, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worksheet as ws

CSS2 = r"""
.sum { width: 100%; border-collapse: collapse; margin-top: 2mm; }
.sum th { background: var(--main); color: #fff; font-size: 10.5px; padding: 1.6mm; }
.sum td { border-bottom: 1px solid #e3e7ef; padding: 1.5mm 1.8mm; font-size: 10.5px; vertical-align: top; }
.sum td.t { font-weight: 800; color: var(--main); white-space: nowrap; }
.sec { margin-top: 3mm; }
.sec h3 { font-size: 13.5px; color: var(--main); border-left: 1.4mm solid var(--acc); padding-left: 2mm; margin-bottom: 1.4mm; }
.kv { display: grid; grid-template-columns: 30mm 1fr; gap: 1.2mm 3mm; font-size: 12px; }
.kv b { color: #5a6275; font-weight: 700; }
.chips span { display: inline-block; margin: .6mm 1mm .6mm 0; padding: .6mm 2.4mm; border-radius: 9mm; font-size: 11px; }
.chips.w span { background: #fde6ea; color: #a3122a; } .chips.i span { background: #fff3c4; color: #7a5a00; }
.rec { font-size: 11.5px; line-height: 1.65; background: #f6f7fb; padding: 2.4mm 3mm; border-radius: 1.6mm; }
.dl { font-size: 11px; line-height: 1.7; } .dl li { margin-left: 5mm; }
.big { font-size: 20px; font-weight: 800; color: var(--main); }
"""


def esc(s):
    return html.escape(s or '')


def page(inner, K, logos, title_en, title_ko, sub):
    return f'''<section class="page"><img class="wm" src="{logos['englishfit']}">{ws.header(K, logos, title_en, title_ko, sub)}
<div class="body">{inner}</div>{ws.footer(logos)}</section>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('brief'); ap.add_argument('logos'); ap.add_argument('out')
    ap.add_argument('--date', required=True); ap.add_argument('--qdir', default='')
    a = ap.parse_args()
    S = json.load(open(a.brief))
    K = ws.KINDS['daily']
    logos = {k: ws.b64(os.path.join(a.logos, k + '.png')) for k in ('yeongpit', 'englishfit', 'cube')}
    ds = ws.datestr_of(a.date)
    qs = {}
    if a.qdir:
        for f in glob.glob(os.path.join(a.qdir, 'q_*.json')):
            q = json.load(open(f)); qs[q['name']] = q
    rows = ''.join(f'''<tr><td class="t">{esc(s['time'])}{('–' + esc(s['out'])) if s.get('out') else ''}</td><td><b>{esc(s['name'])}</b> <small>{esc(s.get('grade'))}</small></td>
<td>{esc(', '.join(s.get('weak', [])[:3]) or '—')}</td><td>{'데일리 10 ✔' if s.get('daily', True) else '브리핑만'}</td></tr>''' for s in S)
    first = f'''<div class="sec"><span class="big">오늘 {len(S)}명</span> · 데일리 10 {sum(1 for s in S if s.get('daily', True))}장 (앞면 문제 · 뒷면 정답)</div>
<table class="sum"><tr><th>평소 등원</th><th>학생</th><th>먼저 볼 취약 개념</th><th>프린트</th></tr>{rows}</table>
<div class="memo"><b>명단 기준</b> · 「📍 등원 기록」 최근 같은 요일 4번의 등원 중앙값 + 등원 스케줄 정해진 시간표. 반만 와도 넣었어요.</div>'''
    pages = [page(first, K, logos, 'ENGLISH FIT · DAILY BRIEFING', '등원 브리핑', ds + ' · 전체 요약')]
    for s in S:
        q = qs.get(s['name'])
        dl = ''
        if q:
            dl = '<div class="sec"><h3>오늘 데일리 10 구성</h3><ol class="dl">' + ''.join(
                f'<li>{esc(it.get("kind"))} · {esc(it.get("tag"))} — 정답 {esc(it.get("answer"))}</li>' for it in q['items']) + '</ol></div>'
        inner = f'''<div class="sec"><span class="big">{esc(s['name'])}</span> <small>{esc(s.get('grade'))}</small></div>
<div class="sec"><h3>등원 · 교재</h3><div class="kv"><b>평소 등원</b><span>{esc(s['time'])}{(' – ' + esc(s['out'])) if s.get('out') else ''} {('(최근 같은 요일 ' + esc(s['seen']) + ')') if s.get('seen') else ''} {esc(s.get('fixed'))}</span>
<b>교재</b><span>{esc(s.get('book') or '—')}</span><b>교재 진도</b><span>{esc(s.get('progress') or '학생 리스트 「교재 진도」 칸이 비어 있어요')}</span></div></div>
<div class="sec"><h3>취약 개념</h3><div class="chips w">{''.join(f'<span>{esc(x)}</span>' for x in s.get('weak', [])) or '—'}</div></div>
<div class="sec"><h3>개선중 개념</h3><div class="chips i">{''.join(f'<span>{esc(x)}</span>' for x in s.get('improving', [])) or '—'}</div></div>
<div class="sec"><h3>최근 틀린 문항</h3><div class="rec">{esc(s.get('recent') or '—')}</div></div>{dl}
{('<div class="memo"><b>참고</b> · ' + esc(s['note']) + '</div>') if s.get('note') else ''}'''
        pages.append(page(inner, K, logos, 'ENGLISH FIT · DAILY BRIEFING', '등원 브리핑', s['name'] + ' · ' + ds))
    doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>:root{{--main:{K['main']};--acc:{K['acc']};--light:{K['light']}}}{ws.CSS}{CSS2}</style></head><body>{''.join(pages)}</body></html>'''
    bad = ws.render(doc, a.out)
    print(f'{a.out}: {len(pages)}쪽 (요약 1 + 학생 {len(S)})')
    if bad:
        print('⚠️ 넘친 쪽:', bad); sys.exit(2)


if __name__ == '__main__':
    main()
