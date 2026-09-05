/**
 * 데니쌤 단어시험 결과 수집 스크립트
 * ------------------------------------------------------------------
 * 사용법
 *  1. 구글 드라이브에서 새 스프레드시트를 만든다. (예: "데니쌤 결과기록")
 *  2. 확장 프로그램 → Apps Script 를 연다.
 *  3. 기본으로 있는 코드를 지우고 이 파일 내용을 통째로 붙여넣는다.
 *  4. 배포 → 새 배포 → 유형 "웹 앱"
 *       - 실행 사용자      : 나
 *       - 액세스 권한 있는 사용자 : 모든 사용자
 *  5. 배포 후 나오는 /exec 로 끝나는 주소를 복사해서 알려주면
 *     denny/quiz.html 의 SUBMIT_URL 을 그 주소로 바꾼다.
 *
 * 주의
 *  - 코드를 고친 뒤에는 "배포 관리 → 기존 배포 → 새 버전"으로만 다시 배포한다.
 *    새 배포를 만들면 주소가 바뀌어서 이미 나간 시험 링크가 전송 불능이 된다.
 */

var ALL_SHEET = '전체기록';
var HEADERS = ['시각', 'quizId', '시험명', '학생', '점수', '총문항', '정답률(%)',
               '소요시간(초)', '틀린문항', '상세'];

function doPost(e) {
  try {
    var r = JSON.parse(e.postData.contents);
    var row = buildRow(r);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    appendRow(ss, ALL_SHEET, row);
    if (r.quizId) appendRow(ss, String(r.quizId).slice(0, 90), row);
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

/* 브라우저로 열었을 때 배포가 살아 있는지 확인용 */
function doGet() {
  return json({ ok: true, service: '데니쌤 단어시험 결과 수집' });
}

function buildRow(r) {
  var total = Number(r.total) || 0;
  var score = Number(r.score) || 0;
  return [
    new Date(),
    r.quizId || '',
    r.quizTitle || '',
    r.student || '',
    score,
    total,
    total ? Math.round(score / total * 100) : '',
    Number(r.durationSec) || '',
    (r.wrong || []).join(', '),
    JSON.stringify(r.detail || [])
  ];
}

function appendRow(ss, name, row) {
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  sh.appendRow(row);
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
