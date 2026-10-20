"""데일리 10 중복 검사: 오늘 q 파일을 같은 학생의 지난 모든 데일리 10과 비교
usage: python3 -I records/tools/daily10_dupcheck.py ws1020 $WORK   → 겹치는 문항 목록 (종료코드 1이면 중복 있음)
중복 기준: 정답이 같음 / 문제 문장(정답 제외 영어 부분)이 70% 이상 비슷함 / 같은 날 안에서 서로 겹침"""
import json, glob, os, re, sys, difflib
W = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('WORK', '.')
today = sys.argv[1]

def name_of(f):
    b = os.path.basename(f)[2:-5]
    return re.sub(r'_\d{4}$', '', b)

def norm(s):
    s = re.sub(r'\([^)]*[가-힣][^)]*\)', ' ', s or '')   # 한국어 뜻 괄호 제거
    s = re.sub(r'[가-힣]+', ' ', s)
    s = re.sub(r'[^a-z ]', ' ', s.lower())
    return ' '.join(s.split())

past = {}
for f in glob.glob(f'{W}/ws*/q_*.json'):
    if f'/{today}/' in f:
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    past.setdefault(name_of(f), []).extend((f, it) for it in d['items'])

bad = 0
for f in sorted(glob.glob(f'{W}/{today}/q_*.json')):
    n = name_of(f)
    items = json.load(open(f))['items']
    old = past.get(n, [])
    for i, it in enumerate(items):
        t, a = norm(it.get('text')), norm(it.get('answer'))
        hits = []
        for src, o in old + [(f'오늘 {x["no"]}번', x) for x in items[:i]]:
            ot, oa = norm(o.get('text')), norm(o.get('answer'))
            r = difflib.SequenceMatcher(None, t, ot).ratio() if t and ot else 0
            ra = difflib.SequenceMatcher(None, a, oa).ratio() if a and oa else 0
            if (a and a == oa and len(a) > 3) or r >= 0.7 or (ra >= 0.85 and len(a) > 12):
                hits.append(f'{os.path.relpath(src, W) if src.startswith("/") else src}: {o.get("text")} → {o.get("answer")}')
        if hits:
            bad += 1
            print(f'[{n} {it["no"]}번] {it.get("text")} → {it.get("answer")}')
            for h in hits[:3]:
                print('    겹침:', h)
print('중복 문항 수:', bad)
sys.exit(1 if bad else 0)
