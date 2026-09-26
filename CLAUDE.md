# EngFit (영핏영어) 저장소 안내

- 이 저장소는 **공개 GitHub Pages**예요. 학생용 퀴즈·클리닉 HTML이 루트에 있어요.
- **학생 데이터(명단, 연락처, 점수, 분석 결과)는 절대 커밋하지 않아요.** 노션·구글 드라이브에만 둬요.
- 퀴즈 제작 규칙: `GUIDELINES.md` + `engfit-quiz-results` 스킬.
- 학생 누적 학습 기록 시스템(학생 ID, 노션 DB, 분석, 테스트 요청, 백업): `records/README.md`
- 자동 동기화·테스트 생성 절차: `records/RUNBOOK.md`

## 새 퀴즈를 만들 때 (학습 기록 분석용)
1. quizId: `<종류>-<학생코드>-<MMDD>-p<영역>` — 학생코드는 노션 「학생 리스트」의 `퀴즈코드` 첫 값
2. quizTitle에 학생 이름과 **개념 이름**을 넣기 (예: `김영광 to부정사 오답 클리닉 9/23`)
3. detail 문항마다 `tag`(개념 이름) 넣기 — `records/tools/engfit_records.py`의 `CONCEPTS` 이름 사용
4. 오답 클리닉은 원본 quizId 뒤에 `-clinic`을 붙이기
5. **🤔 모름 버튼을 항상 넣기** (선생님 지시, 예외 없음) — 누르면 `chosen:"모름", unknown:true` 로 기록, 키보드 0. 자세한 규칙: `GUIDELINES.md` 「모름 버튼」, 기준 구현: `test-hte-0924.html`
