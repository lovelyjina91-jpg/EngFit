/* 영핏 웹 클리닉 「읽어 주기」 (2026-11-13 원장님 요청)
   - 시작: 지나쌤 한글 인사 (g.mp3: "○○아~ 안녕! 오늘도 지나티처랑 클리닉 시작해 보자!! 화이팅!")
   - 문제마다: 한국어 지시문(k) → 영어 문제(q)를 끝까지 읽어 줄 때까지 보기·🤔 모름 버튼 잠금 (막 누르기 방지)
   - 답을 고르면: 맞았는지 + 정답 문장(a, 지나티처 영어)을 읽어 주고, 다 들은 뒤에 「넘어가기 ▶」
   - 소리: audio/clinic/<quizId>/{g,kN,qN,aN}.mp3 , 목록: audio/clinic/<quizId>/voice.js (CLINIC_VOICE)
   - 페이지의 showQuestion / pick / QUESTIONS / current 를 감싸서 동작 (기존 자동 전송·모름 기록은 그대로) */
(function () {
  var CV = window.CLINIC_VOICE;
  if (!CV || !window.QUESTIONS || typeof window.showQuestion !== "function" || typeof window.pick !== "function") return;
  var BASE = "audio/clinic/" + CV.id + "/";
  var items = CV.items || [];
  var aud = new Audio();
  var playToken = 0;
  var greeted = false;

  var css = document.createElement("style");
  css.textContent =
    ".cv-bar{display:flex;align-items:center;gap:8px;margin:10px 0 4px;flex-wrap:wrap}" +
    ".cv-btn{font-family:inherit;font-size:15px;font-weight:700;border:0;border-radius:999px;padding:8px 14px;background:#eef1ff;color:#2a3a8c;cursor:pointer}" +
    ".cv-btn:disabled{opacity:.5;cursor:default}" +
    ".cv-hint{font-size:14px;color:#7a5a00;background:#fff6d6;border-radius:999px;padding:6px 12px}" +
    ".cv-lock{opacity:.45!important;pointer-events:none!important}" +
    ".cv-panel{margin-top:14px;border-radius:16px;padding:14px 16px;background:#f6f8ff;border:2px solid #d8def8}" +
    ".cv-panel.ok{background:#effaf3;border-color:#9fd9b4}.cv-panel.no{background:#fff3f1;border-color:#f3b8ad}" +
    ".cv-res{font-size:20px;font-weight:800;margin-bottom:6px}" +
    ".cv-ans{font-size:15px;color:#444;margin-bottom:8px}" +
    ".cv-say{display:block;width:100%;text-align:left;font-family:inherit;font-size:19px;line-height:1.5;font-weight:700;color:#1e2b55;background:#fff;border:2px dashed #b9c3f0;border-radius:12px;padding:10px 12px;cursor:pointer}" +
    ".cv-next{display:block;width:100%;margin-top:12px;font-family:inherit;font-size:19px;font-weight:800;border:0;border-radius:14px;padding:13px;background:#2e9e5b;color:#fff;cursor:pointer}" +
    ".cv-next:disabled{background:#b9c7bf;cursor:default}";
  document.head.appendChild(css);

  function url(name) { return BASE + name + ".mp3?v=" + (CV.ver || "1"); }
  function stop() { playToken++; try { aud.pause(); } catch (e) {} }
  // 이름 목록을 차례로 재생, 끝나면 done(). 파일이 없거나 재생이 막히면 건너뜀. 안전장치: 한 파일당 최대 20초.
  function playSeq(names, done) {
    stop();
    var my = playToken, i = 0, guard = null;
    function next() {
      if (guard) { clearTimeout(guard); guard = null; }
      if (my !== playToken) return;
      if (i >= names.length) { if (done) done(); return; }
      var n = names[i++];
      aud.onended = next; aud.onerror = next;
      guard = setTimeout(next, 20000);
      aud.src = url(n);
      var p = aud.play();
      if (p && p.catch) p.catch(function () { if (my === playToken) { clearTimeout(guard); guard = setTimeout(next, 1500); } });
    }
    next();
  }

  function setLocked(on) {
    var btns = document.querySelectorAll("#choices button");
    for (var i = 0; i < btns.length; i++) {
      if (btns[i].classList.contains("cv-keep")) continue;
      btns[i].disabled = on;
      btns[i].classList.toggle("cv-lock", on);
    }
  }

  var origShow = window.showQuestion;
  window.showQuestion = function () {
    var r = origShow.apply(this, arguments);
    var idx = window.current, it = items[idx] || {}, n = idx + 1;
    var seq = [];
    if (!greeted) { greeted = true; seq.push("g"); }
    if (it.k) seq.push("k" + n);
    if (it.q) seq.push("q" + n);
    var box = document.getElementById("choices");
    var bar = document.createElement("div");
    bar.className = "cv-bar";
    var again = document.createElement("button");
    again.className = "cv-btn cv-keep"; again.type = "button"; again.textContent = "🔊 문제 다시 듣기";
    var hint = document.createElement("span");
    hint.className = "cv-hint"; hint.textContent = "👂 끝까지 듣고 골라요";
    bar.appendChild(again); bar.appendChild(hint);
    box.parentNode.insertBefore(bar, box);
    var qseq = seq.filter(function (s) { return s !== "g"; });
    if (!qseq.length) { again.style.display = "none"; }
    function run(list) {
      setLocked(true); again.disabled = true; hint.style.display = "";
      playSeq(list, function () { setLocked(false); again.disabled = false; hint.style.display = "none"; });
    }
    again.onclick = function () { run(qseq); };
    if (seq.length) run(seq); else hint.style.display = "none";
    return r;
  };

  var origPick = window.pick;
  window.pick = function (choice, mark, unknown) {
    if (window.locked) return;
    var idx = window.current, q = window.QUESTIONS[idx], it = items[idx] || {};
    var advance = null, realST = window.setTimeout;
    window.setTimeout = function (fn, ms) { advance = fn; return 0; };
    try { origPick.apply(this, arguments); } finally { window.setTimeout = realST; }
    if (!advance) return;
    stop();
    var ok = !unknown && choice === q.answer;
    document.querySelectorAll(".cv-bar").forEach(function (b) { b.remove(); });
    var box = document.getElementById("choices");
    var btns = box.querySelectorAll("button");
    for (var i = 0; i < btns.length; i++) { btns[i].disabled = true; btns[i].classList.add("cv-lock"); }
    var p = document.createElement("div");
    p.className = "cv-panel " + (ok ? "ok" : "no");
    var res = document.createElement("div"); res.className = "cv-res";
    res.textContent = unknown ? "🤔 괜찮아! 같이 들어 보자" : (ok ? "⭕ 맞았어요!" : "❌ 아쉬워요! 정답을 들어 봐요");
    p.appendChild(res);
    var ans = document.createElement("div"); ans.className = "cv-ans";
    ans.textContent = "정답: " + String(q.answer).replace(/<[^>]+>/g, "");
    p.appendChild(ans);
    var nx = document.createElement("button");
    nx.className = "cv-next"; nx.type = "button"; nx.textContent = "👂 듣는 중…"; nx.disabled = true;
    function ready() { nx.disabled = false; nx.textContent = "넘어가기 ▶"; }
    if (it.a) {
      var say = document.createElement("button");
      say.className = "cv-say"; say.type = "button"; say.textContent = "🔊 " + it.as;
      say.onclick = function () { nx.disabled = true; nx.textContent = "👂 듣는 중…"; playSeq(["a" + (idx + 1)], ready); };
      p.appendChild(say);
      playSeq(["a" + (idx + 1)], ready);
    } else {
      setTimeout(ready, 1200);
    }
    nx.onclick = function () { if (nx.disabled) return; stop(); p.remove(); advance(); };
    p.appendChild(nx);
    box.appendChild(p);
    try { p.scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch (e) {}
  };

  // 마지막 명언 (audio/quotes/quotes.js 의 ENGFIT_QUOTES, 날짜+퀴즈 이름으로 돌아가며 하나)
  if (typeof window.showResult === "function") {
    var origResult = window.showResult;
    window.showResult = function () {
      var r = origResult.apply(this, arguments);
      try { showQuote(); } catch (e) {}
      return r;
    };
  }
  function showQuote() {
    var Q = window.ENGFIT_QUOTES;
    if (!Q || !Q.length || document.getElementById("cv-quote")) return;
    var key = CV.id + new Date().toISOString().slice(0, 10), h = 0;
    for (var i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) >>> 0;
    var k = h % Q.length, q = Q[k], nn = (k + 1 < 10 ? "0" : "") + (k + 1);
    var card = document.getElementById("result-card");
    if (!card) return;
    var st = document.createElement("style");
    st.textContent = "#cv-quote{margin:4px 0 16px;border-radius:18px;padding:16px 18px;background:linear-gradient(135deg,#fff4d6,#ffe3ef);border:2px solid #f5c76a;text-align:center;cursor:pointer}" +
      "#cv-quote .t{font-size:13px;font-weight:800;color:#b5651d;letter-spacing:.5px}" +
      "#cv-quote .e{font-size:21px;font-weight:800;color:#1e2b55;line-height:1.4;margin:6px 0 4px}" +
      "#cv-quote .b{font-size:13px;color:#8a6d3b}#cv-quote .k{font-size:16px;color:#5a4630;margin-top:6px}";
    document.head.appendChild(st);
    var box = document.createElement("div");
    box.id = "cv-quote";
    box.innerHTML = '<div class="t">✨ 오늘의 명언 · 눌러서 다시 듣기 🔊</div><div class="e"></div><div class="b"></div><div class="k"></div>';
    box.querySelector(".e").textContent = "“" + q.en + "”";
    box.querySelector(".b").textContent = "— " + q.by;
    box.querySelector(".k").textContent = q.ko;
    var h2 = card.querySelector("h1,h2,.title");
    if (h2 && h2.nextSibling) card.insertBefore(box, h2.nextSibling); else card.insertBefore(box, card.firstChild);
    var names = [nn + "_en", nn + "_ko"];
    function play() {
      stop(); var my = ++playToken, i = 0;
      (function nx() { if (my !== playToken || i >= names.length) return; aud.onended = nx; aud.onerror = nx;
        aud.src = "audio/quotes/" + names[i++] + ".mp3?v=" + (CV.ver || "1"); var p = aud.play(); if (p && p.catch) p.catch(function () {}); })();
    }
    box.onclick = play;
    play();
  }
})();
