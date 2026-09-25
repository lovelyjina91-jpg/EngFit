# RUNBOOK — Claude 자동 실행 절차

Claude 루틴(예약 실행)과 채팅 요청이 따르는 절차예요. 사람이 읽어도 되지만 주 독자는 Claude예요.

## 고정 정보

| 이름 | 값 |
|---|---|
| 구글시트 「영핏 결과기록」 | Drive 파일 ID `1IqHhnAKif3czodLPat2qO-1Z0SrFgzg81uAyj3vjzU8` |
| 드라이브 백업 폴더 「영핏 학습기록 백업」 | 폴더 ID `1QyBYwwPGB9VgY4zrpizu_iAfJZ2QQXU9` |
| 노션 「원생 관리」 페이지 | `eebba2b59d4c43198edc0ba229a0d200` |
| 학생 리스트 | `collection://7c2b6978-cf28-4fcf-aeea-422872d66b7d` |
| 📊 학습 기록 (누적) | `collection://d7c0e0cd-6406-4590-9bf7-e8ff159311f3` |
| 🧩 강점·약점 추적 | `collection://8d04e348-abf3-4ed1-860e-6e963d173c95` |
| 📈 학생 분석 리포트 | `collection://199a8be1-0b8c-42ff-b90b-7ad9073d9457` |
| 📝 테스트 요청 | `collection://be60c1e6-3487-4460-9fac-d3b564c0427e` |
| 퀴즈 결과 전송 URL | `engfit-quiz-results` 스킬의 URL 그대로 (변경 금지) |

## 절대 규칙

1. **학생 데이터를 저장소에 커밋하지 않는다.** 작업 파일은 전부 스크래치 폴더(`$WORK`)에 둔다.
2. 구글시트는 **읽기만** 한다. 지우거나 고치지 않는다.
3. 노션 「📊 학습 기록」은 **추가만** 한다. `고유키`가 이미 있으면 다시 넣지 않는다.
4. 학생 이름을 추정한 기록은 `확인 필요`를 체크한다. 추측으로 확정하지 않는다.
5. 실패하면 멈추고 무엇이 실패했는지 보고한다. 절반만 넣고 조용히 끝내지 않는다.

## A. 매일 동기화 (밤 11시 30분)

`WORK` = 스크래치 폴더. `T` = `records/tools/engfit_records.py`.

1. **도구 준비**: 저장소에 `records/tools/engfit_records.py`가 없으면
   `git fetch origin claude/student-learning-record-repo-5hhxm2 && git checkout FETCH_HEAD -- records/`
2. **시트 읽기**: Drive `read_file_content(fileId=위 시트)`. 결과가 커서 파일로 저장되면 그 파일 경로를 그대로 쓴다 (`{fileContent: ...}` JSON도 도구가 읽을 수 있음) → `$WORK/sheet.txt`
   - ⚠️ 결과가 표 **요약(Table Sample Data)**만 오거나 기록 수가 이상하게 적으면(9/25에 가운데 153건이 빠진 적 있음): `download_file_content(fileId=시트, exportMimeType="text/csv")` → 저장된 JSON의 `content`(base64)를 풀어 `$WORK/sheet.csv`로 저장. 도구가 CSV도 읽는다. **CSV가 가장 확실하니 기본으로 써도 된다.**
3. **명단 만들기**: 학생 리스트에서
   `SELECT url, "이름", "학생 ID", "퀴즈코드", "별칭" FROM 학생리스트 WHERE "학생 ID" IS NOT NULL`
   → `$WORK/roster.json` = `[{"name", "id", "page"(url 끝 32자리), "codes"(퀴즈코드 쉼표 분리), "aliases"(별칭 쉼표 분리)}]`
4. **정리·분석**:
   ```bash
   python3 $T normalize $WORK/sheet.txt $WORK/roster.json $WORK/records.json
   python3 $T analyze $WORK/records.json $WORK/analysis.json
   ```
5. **이미 있는 고유키**: 학습 기록에서 `SELECT "고유키" FROM 학습기록` (여러 번 나눠 읽어도 됨) → `$WORK/keys.json` (문자열 배열)
6. **노션 행 만들기**: `python3 $T notion records.json analysis.json roster.json keys.json <오늘 날짜> $WORK/out`
7. **새 기록 넣기**: `out/new_records_*.json` 각각을 학습 기록 data source에 `create-pages` (100건 이하씩, 내용 그대로).
7-1. **반드시 검증**: 노션에 들어간 값을 다시 읽어 원본과 비교한다 — 한글을 옮겨 적다 오타가 난 사고가 있었다 (반정욱→반정익, 낱말→냱말).
   - 학습 기록을 100건씩 SQL로 읽는다. 결과가 파일로 저장되도록 긴 열을 이어 붙인 pad 열을 함께 SELECT 한다:
     `SELECT url, "고유키" AS k, "기록" AS f0, "학생 ID" AS f1, "퀴즈ID" AS f2, "원래 입력 이름" AS f3, "틀린문항" AS f4, "원본퀴즈ID" AS f5, "프로젝트" AS f6, "상세" AS f7, "점수" AS n0, "총문항" AS n1, "정답률" AS n2, "시도" AS n3, "중복 전송" AS d, "학생" AS rel, "상세"||"상세"||"상세"||"상세"||"기록"||…(기록 20번) AS pad FROM 학습기록 ORDER BY url LIMIT 100 OFFSET n`
     (결과가 작아 화면에 바로 나오면 pad를 더 길게 해서 다시 읽는다 — 화면 결과를 옮겨 적지 않는다)
   - `python3 $T verify $WORK/records.json $WORK/verify <저장된 파일들…>` → 종료코드 0이면 끝.
   - 아니면 `fix_updates.json`을 update-page로 반영(문자 하나도 바꾸지 말고 그대로), `missing_rows.json`은 create, `extra_pages.json`(원본에 없는 페이지)은 「삭제 대기 (학습 기록 오류본)」 페이지로 move-pages. 그리고 **다시 검증** — 0이 나올 때까지 반복.
8. **강점·약점 갱신**: `out/tracks.json`의 각 줄을 제목(`개념` = "이름 · 개념")으로 기존 행과 맞춰
   - 있으면 `상태, 최근 확인, 시도 수, 최근 정답률, 근거`만 update (값이 바뀐 것만)
   - 없으면 create
9. **리포트**:
   - **일요일**: `out/reports.json` 전체를 새 리포트로 create (주간 기록이 쌓여 발전 과정을 볼 수 있음)
   - **다른 요일**: 오늘 새 기록이 생긴 학생만, 그 학생의 가장 최근 리포트를 `reports.json` 내용으로 update (속성 + 본문 replace)
10. **일요일 백업**: `records.json`에서 `time, studentId, rawName, quizId, title, project, score, total, pct, wrong, sec, attempt, dup, origin, unsure` 열로 CSV를 만들어 드라이브 백업 폴더에 `학습기록_백업_YYYY-MM-DD`로 create_file (text/csv).
11. **보고**: 새 기록 수, 확인 필요 수, 상태가 `취약`으로 새로 바뀐 개념, 찍기 의심이 새로 생긴 학생을 한 문단으로 요약. 새 학생 이름(명단에 없는 이름)이 보이면 "새 학생 등록 필요"로 알린다.

## B. 테스트 요청 처리 (15~22시 매시)

1. 테스트 요청에서 `상태 = 대기` 인 행을 읽는다. 없으면 **바로 끝낸다** (아무것도 쓰지 않음).
2. 행을 `제작중`으로 바꾼다.
3. 학생의 🧩 강점·약점(취약·개선중 우선), 최근 📊 학습 기록의 `상세`(틀린 문항: 고른 답→정답), 📈 최신 리포트를 읽는다. `범위`·`세부 내용`을 우선 따른다.
4. `engfit-quiz-results` 스킬 표준으로 퀴즈 HTML을 만든다.
   - quizId: `test-<학생코드>-<MMDD>-<HHmm>` · 제목: `<이름> <개념> 맞춤 테스트 <M/D>`
   - 문항 수: `문항 수` 값, 없으면 10개. 취약 개념 60% · 개선중 30% · 강점 확인 10%
   - **detail 문항마다 `tag`(개념 이름)를 넣는다** (분석 정확도용)
   - **🤔 모름 버튼을 반드시 넣는다** (GUIDELINES.md 「모름 버튼」, 기준 구현 `test-hte-0924.html`)
   - 학생에게 '모름' 문항이 있으면 그 개념은 설명형 문항(개념 확인)부터 다시 낸다
   - 스킬의 배포 전 체크리스트를 모두 통과시킨다.
5. 저장소 루트에 `test-<학생코드>-<MMDD>.html`로 커밋·푸시 → GitHub Pages 주소를 `퀴즈 링크`에, quizId를 `퀴즈ID`에 넣고 `완료`로 바꾼다. 무엇을 넣었는지 `처리 메모`에 한 줄.
6. 만들 수 없으면 `보류` + `처리 메모`에 이유.

## C. 채팅에서 바로 요청받았을 때

- "○○ 테스트 만들어줘" → B의 3~5단계를 바로 실행하고 링크를 답한다 (테스트 요청 DB에도 `완료` 행으로 남긴다).
- "○○ 분석해줘" → A의 2~4단계 후 그 학생의 analysis를 설명하고, 필요하면 리포트를 갱신한다.
- "새 학생 ○○ 등록" → 학생 리스트에 `이름, 학년, 학교, 상태=재원, 학생 ID=입학연도-이름, 퀴즈코드, 입학일` 추가. 같은 ID가 있으면 `-2`를 붙인다.
