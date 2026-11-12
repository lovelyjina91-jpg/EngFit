#!/bin/sh
# audio/emma/*.mp3 → list.js (EMMA_HAVE). 새 mp3 를 넣은 뒤 실행하고 커밋. sori.html 이 이 목록에 있는 영어만 파일로 재생한다.
cd "$(dirname "$0")"
{ echo "// 엠마(ElevenLabs Emma - Bright Kids Educator, oClOrzqamOXmtcB8iqTj) 영어 소리 목록 — build_list.sh 로 자동 생성"
  echo "var EMMA_VER=$(date +%Y%m%d%H%M);"
  printf 'var EMMA_HAVE={'
  first=1; for f in *.mp3; do [ -s "$f" ] || continue; s=${f%.mp3}; [ $first = 1 ] && first=0 || printf ','; printf '"%s":1' "$s"; done
  echo '};'; } > list.js
echo "list.js: $(ls *.mp3 2>/dev/null | wc -l) 개"
