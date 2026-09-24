#!/usr/bin/env python3
"""영핏 학습 기록 정리·분석 도구.

구글시트 「영핏 결과기록」 내용(Drive 읽기 결과 텍스트)과 학생 명단(JSON)을 받아
  1) normalize : 제출 기록을 학생 ID에 연결하고 프로젝트·영역·개념을 붙인다
  2) analyze   : 학생별 강점·약점·발전 추세·오답 개선율을 계산한다

⚠️ 이 저장소는 공개(GitHub Pages)이므로 학생 데이터(명단·기록·분석 결과)는
   절대 커밋하지 않는다. 입력·출력 파일은 저장소 밖(스크래치 폴더)에 둔다.

사용법:
  python3 engfit_records.py normalize SHEET.txt ROSTER.json OUT_records.json
  python3 engfit_records.py analyze OUT_records.json OUT_analysis.json
  python3 engfit_records.py notion records.json analysis.json ROSTER.json EXISTING_KEYS.json YYYY-MM-DD OUTDIR
    → OUTDIR/new_records_N.json (노션에 없는 기록만, 100건씩), reports.json, tracks.json
      (모두 노션 create-pages 의 pages 형식)
  python3 engfit_records.py verify records.json OUTDIR NOTION_DUMP.txt [...]
    → 노션에 실제로 저장된 값과 원본을 비교. OUTDIR/fix_updates.json(고칠 것),
      extra_pages.json(원본에 없는 페이지), missing_rows.json(빠진 기록). 문제 없으면 종료코드 0

ROSTER.json 형식 (노션 「학생 리스트」에서 만든다):
  [{"name": "김영광", "id": "2026-김영광", "page": "<노션 page id>",
    "codes": ["kyk", "younggwang"], "aliases": ["영광"]}, ...]
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime

# 선생님·테스트용 이름: 학습 기록에서 제외
TEST_NAMES = {"테스트학생", "테스트", "지나테스트", "김진아", "김진아 테스팅", "ㅋㅋ",
              "지나띵", "지나티처", "진아", "데니쌤"}
TEST_QUIZ_IDS = {"test-quiz", "submit-test", "clinic-demo-0702"}

# 개념 사전: (개념명, 영역, 제목에서 찾을 정규식)
CONCEPTS = [
    ("be동사", "어법", r"be동사|There is|There are"),
    ("일반동사·do/does", "어법", r"일반동사|do·does|do/does|does"),
    ("3인칭 단수", "어법", r"3인칭|s/es|-ed/-s"),
    ("현재시제·현재진행", "어법", r"현재시제|현재형|현재진행"),
    ("과거시제", "어법", r"과거시제|과거형|과거동사|과거 동사"),
    ("미래표현", "어법", r"미래|\bwill\b"),
    ("현재완료", "어법", r"현재완료"),
    ("과거완료", "어법", r"과거완료|past.perfect"),
    ("시제 종합", "어법", r"(?<![현과])시제"),
    ("조동사", "어법", r"조동사|\bcan\b|modal"),
    ("to부정사", "어법", r"to부정사|to.infinitive|toinf"),
    ("동명사", "어법", r"동명사|동사원형\+ing"),
    ("분사", "어법", r"분사"),
    ("수동태", "어법", r"수동태|passive"),
    ("관계대명사", "어법", r"관계대명사|관계사"),
    ("명사절·접속사 that", "어법", r"명사절|접속사 that|that절|whether"),
    ("접속사", "어법", r"(?<!관계)접속사"),
    ("비교급", "어법", r"비교"),
    ("전치사", "어법", r"전치사|preposition"),
    ("명사·복수형", "어법", r"복수형|(?<![대])명사(?!절)|셀 수 있는"),
    ("관사 a/an/the", "어법", r"관사|a/an"),
    ("수량 표현", "어법", r"수량"),
    ("대명사", "어법", r"대명사(?<!관계대명사)|this/that|재귀"),
    ("의문사·의문문", "어법", r"의문사|의문문"),
    ("주어 찾기", "어법", r"주어"),
    ("형용사·보어", "어법", r"형용사|보어|make.adjective"),
    ("부사·빈도부사", "어법", r"부사"),
    ("동사 변화형", "어법", r"동사변화|3단 변화|불규칙"),
    ("어순·문장 만들기", "서술형", r"어순|문장 만들기"),
    ("구동사", "어휘", r"구동사"),
    ("문법 종합", "어법", r"문법|GRAMMAR|어법"),
    ("단어·철자", "어휘", r"단어|어휘|vocab|철자|낱말|받아쓰기|딕테이션|DAY \d+|Step\d"),
    ("독해 유형", "독해", r"독해|지문|내용일치|지칭|본문|READ IT|Read It|리딩|reading|변형|도표|안내문|단원평가"),
    ("대화문", "대화문", r"대화|dialogue"),
    ("영작·배열", "서술형", r"영작|배열|서술형"),
    ("파닉스", "파닉스", r"파닉스|phonics"),
]


def unescape_md(s):
    """Drive 읽기 결과는 마크다운이라 기호 앞에 \\ 가 붙어 온다 (예: \\~, \\>, \\[). 원래 글자로 되돌린다."""
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!|~<>&=^\"'])", r"\1", s)


def parse_sheet(text):
    """Drive 읽기 결과(마크다운 표 여러 개)에서 제출 기록만 뽑아 중복 제거."""
    seen = {}
    for line in text.split("\n"):
        if not re.match(r"\| 20\d\d-", line):
            continue
        cells = [unescape_md(c.strip()) for c in re.split(r"(?<!\\) \| ", line.strip().strip("|"))]
        if len(cells) < 10:
            continue
        seen[(cells[0], cells[1], cells[3])] = cells
    def when(k):
        return datetime.strptime(k[0], "%Y-%m-%d %H:%M:%S")
    return [seen[k] for k in sorted(seen, key=when)]


def build_matchers(roster):
    by_name, by_code = {}, {}
    for s in roster:
        by_name[s["name"]] = s
        for a in s.get("aliases", []):
            by_name[a] = s
        for c in s.get("codes", []):
            by_code[c.lower()] = s
    return by_name, by_code


def quiz_codes(quiz_id):
    """quizId 안의 영문 조각들. 예) clinic-kdy-0808-p1 → [clinic, kdy, 0808, p1]"""
    base = quiz_id.split("--")[0]
    return [p for p in re.split(r"[-_]", base.lower()) if p]


def match_student(raw, quiz_id, by_name, by_code):
    """(학생 or None, 확인필요 여부)"""
    name = re.sub(r"[\\<>^ㅡ\-]+", " ", raw).strip()
    if raw.strip() in by_name:
        return by_name[raw.strip()], False
    # 이름 안에 한글 이름이 섞여 있는 경우 (예: "Kim ye chan 김예찬")
    for token in name.split():
        if token in by_name:
            return by_name[token], False
    # 클리닉 파생 퀴즈: clinic-<원본>--이름--시각
    m = re.search(r"--([^-]+)--", quiz_id)
    if m and m.group(1) in by_name:
        return by_name[m.group(1)], True
    for code in quiz_codes(quiz_id):
        if code in by_code:
            return by_code[code], True
    return None, True


def classify_project(qid, title):
    q = qid.lower()
    if q.startswith("basic-"):
        return "기초클리닉"
    if q.startswith("concept-") or "개념 확인" in title or "개념확인" in title:
        return "개념확인"
    if "vocab" in q or q.startswith("daily-"):
        return "단어시험"
    if q.startswith(("retest", "checkup")) or "재클리닉" in title:
        return "재시험"
    if "sci" in q or "과학" in title or "도덕" in title:
        return "타과목"
    if "mock" in q or "모의고사" in title:
        return "모의고사"
    if "naesin" in q or "내신" in title or "기말" in title or "중간" in title:
        return "내신대비"
    if q.startswith("clinic-"):
        return "오답클리닉"
    return "수업퀴즈"


def origin_quiz(qid):
    """클리닉이면 원본 퀴즈 ID."""
    m = re.match(r"clinic-(.+?)--", qid)
    if m:
        return m.group(1)
    if qid.endswith("-clinic"):
        return qid[: -len("-clinic")]
    return ""


def concepts_of(title):
    found = []
    for name, area, pat in CONCEPTS:
        if re.search(pat, title, re.I):
            found.append((name, area))
    return found


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def normalize(sheet_text, roster):
    by_name, by_code = build_matchers(roster)
    out, attempts, sent = [], defaultdict(int), set()
    for c in parse_sheet(sheet_text):
        ts, qid, title, raw = c[0], c[1], c[2], c[3]
        if raw.strip() in TEST_NAMES or qid in TEST_QUIZ_IDS:
            continue
        stu, unsure = match_student(raw, qid, by_name, by_code)
        score, total = to_int(c[4]), to_int(c[5])
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        key_sid = stu["id"] if stu else "?" + raw
        # 같은 풀이 결과가 다시 전송된 경우(점수·오답·소요시간 동일) → 중복
        sig = (key_sid, qid, c[4], c[7], c[8])
        dup = sig in sent
        sent.add(sig)
        if not dup:
            attempts[(key_sid, qid)] += 1
        cons = concepts_of(title.replace("\\", ""))
        detail = c[9].replace("\\[", "[").replace("\\]", "]")
        out.append({
            "key": f"{ts}|{qid}|{raw}",
            "time": dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "quizId": qid,
            "title": title.replace("\\", ""),
            "rawName": raw,
            "studentId": stu["id"] if stu else None,
            "studentPage": stu.get("page") if stu else None,
            "unsure": unsure,
            "score": score,
            "total": total,
            "pct": round(score * 100 / total, 1) if score is not None and total else None,
            "wrong": c[7],
            "sec": to_int(c[8]),
            "project": classify_project(qid, title),
            "origin": origin_quiz(qid),
            "attempt": attempts[(key_sid, qid)],
            "dup": dup,
            "areas": sorted({a for _, a in cons}) or ["기타"],
            "concepts": [n for n, _ in cons],
            "detail": detail,
        })
    # 제목에 개념이 없는 클리닉은 원본 퀴즈의 개념을 물려받는다
    by_quiz = {}
    for r in out:
        if r["concepts"]:
            by_quiz.setdefault(r["quizId"], r)
    for r in out:
        src = by_quiz.get(r["origin"])
        if not r["concepts"] and src:
            r["concepts"], r["areas"] = list(src["concepts"]), list(src["areas"])
    return out


def question_tags(detail):
    """detail 문항에 "tag"(개념명)가 있으면 {개념: (맞힌 수, 문항 수)}."""
    try:
        items = json.loads(detail)
    except (TypeError, ValueError):
        return {}
    out = defaultdict(lambda: [0, 0])
    for it in items if isinstance(items, list) else []:
        tag = isinstance(it, dict) and it.get("tag")
        if tag:
            out[tag][0] += 1 if it.get("ok") else 0
            out[tag][1] += 1
    return {k: tuple(v) for k, v in out.items()}


def trend(pcts):
    if len(pcts) < 4:
        return "데이터 부족"
    half = len(pcts) // 2
    early = sum(pcts[:half]) / half
    late = sum(pcts[half:]) / (len(pcts) - half)
    if late - early >= 5:
        return "상승"
    if early - late >= 5:
        return "하락"
    return "유지"


def analyze(records):
    per = defaultdict(list)
    for r in records:
        if r["studentId"] and r["pct"] is not None and not r.get("dup"):
            per[r["studentId"]].append(r)
    result = {}
    for sid, rs in per.items():
        rs.sort(key=lambda r: r["time"])
        pcts = [r["pct"] for r in rs]
        # 개념별 정답률 흐름
        concept = defaultdict(list)
        for r in rs:
            tagged = question_tags(r["detail"])
            if tagged:
                # 문항에 tag가 있으면 문항 단위로 개념 정답률을 계산 (제목보다 정확)
                for name, (ok, n) in tagged.items():
                    concept[name].append((r["time"][:10], round(ok * 100 / n, 1), r["quizId"]))
                continue
            for name in r["concepts"]:
                concept[name].append((r["time"][:10], r["pct"], r["quizId"]))
        concept_stats = {}
        for name, hist in concept.items():
            ps = [p for _, p, _ in hist]
            recent = ps[-3:]
            recent_avg = sum(recent) / len(recent)
            first = ps[0]
            if recent_avg >= 85 and len(ps) >= 2 and first < 70:
                status = "극복"
            elif recent_avg >= 85:
                status = "강점"
            elif recent_avg < 65:
                status = "취약"
            else:
                status = "개선중"
            concept_stats[name] = {
                "n": len(ps), "first": first, "recentAvg": round(recent_avg, 1),
                "firstDate": hist[0][0], "lastDate": hist[-1][0], "status": status,
                "evidence": [f"{d} {q} {p}%" for d, p, q in hist[-5:]],
            }
        # 오답 개선율: 원본 퀴즈 → 클리닉/재도전 점수 비교
        by_quiz = defaultdict(list)
        for r in rs:
            by_quiz[r["quizId"]].append(r)
        # 클리닉·재도전에서 맞힌 문항 비율 (문항 수로 가중)
        fix_ok = fix_all = 0
        for r in rs:
            if (r["origin"] and r["origin"] in by_quiz) or r["attempt"] > 1:
                fix_ok += r["score"] or 0
                fix_all += r["total"] or 0
        # 찍기 의심: 문항당 3초 미만으로 풀고 정답률 50% 미만
        rushed = [r for r in rs if r["sec"] and r["total"]
                  and r["sec"] / r["total"] < 3 and r["pct"] < 50]
        projects = defaultdict(list)
        areas = defaultdict(lambda: [0, 0])
        for r in rs:
            projects[r["project"]].append(r["pct"])
            for a in r["areas"]:
                areas[a][0] += r["score"] or 0
                areas[a][1] += r["total"] or 0
        result[sid] = {
            "areas": {k: v for k, v in areas.items() if v[1]},
            "count": len(rs),
            "period": f"{rs[0]['time'][:10]} ~ {rs[-1]['time'][:10]}",
            "avg": round(sum(pcts) / len(pcts), 1),
            "recent5": round(sum(pcts[-5:]) / len(pcts[-5:]), 1),
            "trend": trend(pcts),
            "fixRate": round(fix_ok * 100 / fix_all, 1) if fix_all >= 5 else None,
            "rushed": [f"{r['time'][:10]} {r['quizId']} {r['pct']}% ({r['sec']}초)" for r in rushed],
            "projects": {k: {"n": len(v), "avg": round(sum(v) / len(v), 1)}
                         for k, v in projects.items()},
            "concepts": concept_stats,
            "totalSec": sum(r["sec"] or 0 for r in rs),
        }
    return result


# ---------------------------------------------------------------- 노션 행 만들기
# 노션 create-pages 도구의 pages 형식(JSON)으로 만든다. 속성 이름은 노션 DB와 같아야 한다.

AREA_OF = {name: area for name, area, _ in CONCEPTS}


def wrong_summary(detail):
    try:
        items = json.loads(detail)
    except (TypeError, ValueError):
        return (detail or "")[:300]
    parts = [f"{i.get('no')}번 {str(i.get('chosen'))[:40]}→{str(i.get('answer'))[:40]}"
             for i in items if isinstance(i, dict) and not i.get("ok")]
    return " / ".join(parts)[:1900]


def page_url(page_id):
    return "https://www.notion.so/" + page_id.replace("-", "")


def notion_record_rows(records, existing_keys):
    """📊 학습 기록: 아직 노션에 없는 기록만."""
    rows = []
    for x in records:
        if x["key"] in existing_keys:
            continue
        p = {"기록": x["title"][:200], "학생 ID": x["studentId"] or "",
             "date:제출시각:start": x["time"] + "+09:00", "date:제출시각:is_datetime": 1,
             "프로젝트": x["project"], "영역": json.dumps(x["areas"], ensure_ascii=False),
             "틀린문항": x["wrong"], "퀴즈ID": x["quizId"], "원본퀴즈ID": x["origin"],
             "시도": x["attempt"], "원래 입력 이름": x["rawName"],
             "확인 필요": "__YES__" if x["unsure"] or not x["studentId"] else "__NO__",
             "중복 전송": "__YES__" if x.get("dup") else "__NO__",
             "상세": wrong_summary(x["detail"]), "출처": "구글시트", "고유키": x["key"]}
        for k, n in (("score", "점수"), ("total", "총문항"), ("pct", "정답률"), ("sec", "소요시간(초)")):
            if x[k] is not None:
                p[n] = x[k]
        if x["studentPage"]:
            p["학생"] = json.dumps([page_url(x["studentPage"])])
        rows.append({"properties": {k: v for k, v in p.items() if v != ""}})
    return rows


def recommendations(v):
    cs = v["concepts"]
    weak = sorted([k for k, s in cs.items() if s["status"] == "취약"], key=lambda k: cs[k]["recentAvg"])
    mid = sorted([k for k, s in cs.items() if s["status"] == "개선중"], key=lambda k: cs[k]["recentAvg"])
    rec = []
    if weak:
        rec.append(f"취약 개념 집중 테스트: {', '.join(weak[:3])}")
    if mid:
        rec.append(f"개선중 개념 한 번 더 확인: {', '.join(mid[:3])}")
    if len(v["rushed"]) >= 3:
        rec.append(f"찍기 의심 {len(v['rushed'])}회 — 천천히 읽고 풀도록 지도")
    if v["trend"] == "하락":
        rec.append("최근 정답률이 앞선 기록보다 낮음 — 최근 범위 복습 필요")
    if v["count"] < 5:
        rec.append("기록이 적어 판단이 어려움 — 실력 점검 퀴즈 1회 권장")
    return rec or ["현재 수준 유지 — 다음 단계 개념으로 진도 확장"], weak, mid


def notion_report_page(sid, name, page_id, v, records, today):
    """📈 학생 분석 리포트 1장 (속성 + 본문)."""
    cs = v["concepts"]
    rec, weak, mid = recommendations(v)
    strong = sorted([k for k, s in cs.items() if s["status"] in ("강점", "극복")], key=lambda k: -cs[k]["n"])
    over = [k for k, s in cs.items() if s["status"] == "극복"]
    fmt = lambda ks: ", ".join(f"{k}({cs[k]['recentAvg']:.0f}%)" for k in ks) or "-"
    rs = [r for r in records if r["studentId"] == sid and r["pct"] is not None and not r.get("dup")]
    rs.sort(key=lambda r: r["time"])
    concept_rows = "\n".join(
        f"| {k} | {AREA_OF.get(k, '')} | {s['status']} | {s['n']} | {s['first']:.0f}% | {s['recentAvg']:.0f}% | {s['firstDate']} ~ {s['lastDate']} |"
        for k, s in sorted(cs.items(), key=lambda x: x[1]["recentAvg"]))
    area_rows = "\n".join(f"| {k} | {a[0]}/{a[1]} | {a[0] * 100 / a[1]:.0f}% |" for k, a in sorted(v["areas"].items()))
    proj_rows = "\n".join(f"| {k} | {x['n']} | {x['avg']:.0f}% |"
                          for k, x in sorted(v["projects"].items(), key=lambda y: -y[1]["n"]))
    timeline = "\n".join(f"- {r['time'][:10]} · {r['title'][:50]} · **{r['pct']:.0f}%** ({r['score']}/{r['total']})"
                         for r in rs[-12:])
    rushed = "\n".join(f"- {x}" for x in v["rushed"]) or "- 없음"
    fix = f"{v['fixRate']:.0f}%" if v["fixRate"] is not None else "데이터 부족"
    over_txt = ("\n- 처음엔 약했지만 **극복한 개념**: " + ", ".join(over)) if over else ""
    content = f"""## 한눈에 보기
- 분석 기간: {v['period']} · 기록 {v['count']}건 · 총 풀이 시간 약 {v['totalSec'] // 60}분
- 평균 정답률 **{v['avg']:.0f}%** → 최근 5건 **{v['recent5']:.0f}%** (추세: {v['trend']})
- 오답 개선율 (클리닉·재도전에서 맞힌 비율): {fix}{over_txt}

## 영어 시험 대비 영역별 실력
| 영역 | 맞힌 문항/전체 | 정답률 |
|---|---|---|
{area_rows}

## 개념별 발전 과정 (낮은 순)
| 개념 | 영역 | 상태 | 횟수 | 처음 | 최근 | 기간 |
|---|---|---|---|---|---|---|
{concept_rows}

## 프로젝트별
| 프로젝트 | 횟수 | 평균 |
|---|---|---|
{proj_rows}

## 찍기 의심 기록 (문항당 3초 미만 + 50% 미만)
{rushed}

## 최근 기록
{timeline}

## 다음 추천
""" + "\n".join(f"- {x}" for x in rec) + (
        "\n\n> Claude가 「📊 학습 기록」을 자동 분석해 만든 리포트예요. 개념은 퀴즈 제목(또는 문항 tag)으로 분류해요.")
    props = {"리포트": f"{name} 학습 분석 · {today}", "학생": json.dumps([page_url(page_id)]),
             "학생 ID": sid, "date:작성일:start": today, "분석 기간": v["period"], "기록 수": v["count"],
             "평균 정답률": v["avg"], "최근 정답률": v["recent5"], "추세": v["trend"],
             "강점": fmt(strong)[:1900], "약점": fmt(weak + mid)[:1900], "다음 추천": " / ".join(rec)[:1900]}
    if v["fixRate"] is not None:
        props["오답 개선율"] = v["fixRate"]
    return {"properties": props, "content": content}


def notion_track_rows(sid, name, page_id, v):
    """🧩 강점·약점 추적: 학생 × 개념 1줄씩. 제목 "이름 · 개념"으로 기존 줄을 찾아 갱신한다."""
    rows = []
    for k, s in v["concepts"].items():
        rows.append({"properties": {
            "개념": f"{name} · {k}", "학생": json.dumps([page_url(page_id)]), "학생 ID": sid,
            "영역": AREA_OF.get(k, "기타"), "상태": s["status"],
            "date:처음 발견:start": s["firstDate"], "date:최근 확인:start": s["lastDate"],
            "시도 수": s["n"], "최근 정답률": s["recentAvg"],
            "근거": (f"처음 {s['first']:.0f}% → 최근 {s['recentAvg']:.0f}% | " + " / ".join(s["evidence"]))[:1900]}})
    return rows


# ---------------------------------------------------------------- 저장 후 검증
# 노션에 쓴 값은 반드시 다시 읽어서 원본과 비교한다. (도우미가 한글을 옮겨 적다가
# 반정욱→반정익 같은 오타를 낸 적이 있다.) 노션 SQL 결과를 파일로 받으려면
# 결과가 커지도록 긴 열을 몇 번 이어 붙인 pad 열을 함께 SELECT 한다 (RUNBOOK 참고).

VERIFY_TEXT = {"f0": "기록", "f1": "학생 ID", "f2": "퀴즈ID", "f3": "원래 입력 이름",
               "f4": "틀린문항", "f5": "원본퀴즈ID", "f6": "프로젝트", "f7": "상세"}
VERIFY_NUM = {"n0": "점수", "n1": "총문항", "n2": "정답률", "n3": "시도"}


def verify_records(actual_rows, expected_rows):
    """actual_rows: 노션 SQL 결과(url, k=고유키, f0..f7, n0..n3, d=중복 전송, rel=학생).
    expected_rows: notion_record_rows() 결과. 고쳐야 할 update 목록과 요약을 돌려준다."""
    exp = {r["properties"]["고유키"]: r["properties"] for r in expected_rows}
    seen, fixes, extra = set(), [], []
    for a in actual_rows:
        p = exp.get(a["k"])
        if p is None:
            extra.append(a["url"])
            continue
        seen.add(a["k"])
        diff = {}
        for c, name in VERIFY_TEXT.items():
            if (a.get(c) or "") != p.get(name, ""):
                diff[name] = p.get(name)
        for c, name in VERIFY_NUM.items():
            ev, av = p.get(name), a.get(c)
            if (ev is None) != (av is None) or (ev is not None and abs(float(ev) - float(av)) > 1e-6):
                diff[name] = ev
        if (a.get("d") or "__NO__") != p.get("중복 전송", "__NO__"):
            diff["중복 전송"] = p.get("중복 전송", "__NO__")
        want = json.loads(p["학생"])[0].rsplit("/", 1)[-1] if "학생" in p else None
        rel = json.loads(a.get("rel") or "[]")
        have = rel[0].rsplit("/", 1)[-1].replace("-", "") if rel else None
        if want != have:
            diff["학생"] = p.get("학생")
        if diff:
            fixes.append({"page_id": a["url"].rsplit("/", 1)[-1], "properties": diff})
    missing = [r for k, r in exp.items() if k not in seen]
    return fixes, extra, missing


def build_notion(records, analysis, roster, existing_keys, today, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    rows = notion_record_rows(records, existing_keys)
    for i in range(0, len(rows), 100):
        json.dump(rows[i:i + 100], open(f"{outdir}/new_records_{i // 100}.json", "w", encoding="utf-8"),
                  ensure_ascii=False)
    by_id = {s["id"]: s for s in roster}
    reports, tracks = [], []
    for sid, v in sorted(analysis.items()):
        s = by_id.get(sid)
        if not s:
            continue
        reports.append(notion_report_page(sid, s["name"], s["page"], v, records, today))
        tracks += notion_track_rows(sid, s["name"], s["page"], v)
    json.dump(reports, open(f"{outdir}/reports.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(tracks, open(f"{outdir}/tracks.json", "w", encoding="utf-8"), ensure_ascii=False)
    return len(rows), len(reports), len(tracks)


def main(argv):
    if len(argv) >= 5 and argv[1] == "normalize":
        text = open(argv[2], encoding="utf-8").read()
        if text.lstrip().startswith("{"):
            text = json.loads(text).get("fileContent", text)
        roster = json.load(open(argv[3], encoding="utf-8"))
        recs = normalize(text, roster)
        json.dump(recs, open(argv[4], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        miss = sum(1 for r in recs if not r["studentId"])
        unsure = sum(1 for r in recs if r["unsure"])
        print(f"records={len(recs)} unmatched={miss} unsure={unsure}")
    elif len(argv) >= 4 and argv[1] == "analyze":
        recs = json.load(open(argv[2], encoding="utf-8"))
        res = analyze(recs)
        json.dump(res, open(argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"students={len(res)}")
    elif len(argv) >= 8 and argv[1] == "notion":
        recs = json.load(open(argv[2], encoding="utf-8"))
        ana = json.load(open(argv[3], encoding="utf-8"))
        roster = json.load(open(argv[4], encoding="utf-8"))
        keys = set(json.load(open(argv[5], encoding="utf-8")))
        n = build_notion(recs, ana, roster, keys, argv[6], argv[7])
        print("new_records=%d reports=%d tracks=%d" % n)
    elif len(argv) >= 5 and argv[1] == "verify":
        # verify records.json OUTDIR DUMP1.txt [DUMP2.txt ...]
        recs = json.load(open(argv[2], encoding="utf-8"))
        actual = []
        for path in argv[4:]:
            txt = open(path, encoding="utf-8").read()
            actual += json.loads(txt)["results"]
        fixes, extra, missing = verify_records(actual, notion_record_rows(recs, set()))
        import os
        os.makedirs(argv[3], exist_ok=True)
        json.dump(fixes, open(f"{argv[3]}/fix_updates.json", "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(extra, open(f"{argv[3]}/extra_pages.json", "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(missing, open(f"{argv[3]}/missing_rows.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"notion_rows={len(actual)} to_fix={len(fixes)} extra={len(extra)} missing={len(missing)}")
        return 0 if not (fixes or extra or missing) else 2
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
