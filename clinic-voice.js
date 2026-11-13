/* 영핏 웹 클리닉 「읽어 주기」 (2026-11-13 원장님 요청)
   - 시작: 지나쌤 한글 인사 (g.mp3: "○○아~ 안녕! 오늘도 지나티처랑 클리닉 시작해 보자!! 화이팅!")
   - 문제마다: 한국어 지시문(k) → 영어 문제(q)를 끝까지 읽어 줄 때까지 보기·🤔 모름 버튼 잠금 (막 누르기 방지)
   - 답을 고르면: 맞았는지 + 정답 문장(a, 지나티처 영어)을 읽어 주고, 다 들은 뒤에 「넘어가기 ▶」
   - 소리: audio/clinic/<quizId>/{g,kN,qN,aN}.mp3 , 목록: audio/clinic/<quizId>/voice.js (CLINIC_VOICE)
   - 페이지의 showQuestion / pick / QUESTIONS / current 를 감싸서 동작 (기존 자동 전송·모름 기록은 그대로) */
(function () {
  // 원장님 들어 보기 모드 (?t=1): 결과를 구글시트로 보내지 않음 (원장님 11/13 "그날 보낸 링크 전부 개인톡에, 다 들어보게")
  try { if (new URLSearchParams(location.search).get("t") === "1") { window.fetch = function () { return Promise.resolve({ ok: true, json: function () { return {}; } }); }; window._engfitSent = true; try { localStorage.removeItem("engfit-" + (window.QUIZ_ID || "")); } catch (e) {} } } catch (e) {}
  var CV = window.CLINIC_VOICE;
  if (!CV) return;
  var BASE = "audio/clinic/" + CV.id + "/";
  var items = CV.items || [];
  var aud = new Audio();
  var playToken = 0;
  var greeted = false;
  // ── 배경음악·효과음 (원장님 2026-11-13 일레븐랩스 Pro "배경음악이나 목소리 아주 다양하게") ──
  // audio/fx/bgm.mp3 (작게, 목소리 나오면 더 작게), ding(맞음)·oops(틀림, 부드럽게)·tada(결과). 🎵 버튼으로 끄고 켬(기기에 기억).
  var FXV = "20261113b";
  var FX = (function () {
    var on = true; try { on = localStorage.getItem("engfit-bgm") !== "off"; } catch (e) {}
    var bgmName = "bgm"; try { var qb = new URLSearchParams(location.search).get("bgm"); if (qb === "1") bgmName = "bgm_a"; else if (qb === "2") bgmName = "bgm_b"; } catch (e) {}
    var bgm = new Audio("audio/fx/" + bgmName + ".mp3?v=" + FXV); bgm.loop = true; bgm.volume = 0.13;
    var sfx = new Audio(); var speaking = 0, started = false, btn = null;
    function target() { return speaking > 0 ? 0.035 : 0.13; }
    var fadeT = null;
    function fadeTo(v) { clearInterval(fadeT); fadeT = setInterval(function () { var d = v - bgm.volume; if (Math.abs(d) < 0.01) { bgm.volume = v; clearInterval(fadeT); return; } bgm.volume = Math.max(0, Math.min(1, bgm.volume + d * 0.35)); }, 40); }
    function watch(a) {
      if (!a || a.__fxw) return; a.__fxw = 1;
      a.addEventListener("playing", function () { speaking = 1; fadeTo(target()); });
      var off = function () { setTimeout(function () { if (a.paused || a.ended) { speaking = 0; fadeTo(target()); } }, 350); };
      a.addEventListener("pause", off); a.addEventListener("ended", off); a.addEventListener("error", off);
    }
    function paint() { if (btn) { btn.textContent = on ? "🎵" : "🔇"; btn.title = on ? "배경음악 끄기" : "배경음악 켜기"; } }
    function start() {
      started = true;
      if (!btn) {
        btn = document.createElement("button"); btn.type = "button";
        btn.style.cssText = "position:fixed;right:12px;bottom:12px;z-index:9999;width:46px;height:46px;border-radius:50%;border:0;font-size:22px;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.18);cursor:pointer";
        btn.onclick = function () { on = !on; try { localStorage.setItem("engfit-bgm", on ? "on" : "off"); } catch (e) {} paint(); if (on) { var p = bgm.play(); if (p && p.catch) p.catch(function () {}); } else bgm.pause(); };
        document.body.appendChild(btn); paint();
      }
      if (on) { bgm.volume = target(); var p = bgm.play(); if (p && p.catch) p.catch(function () {}); }
    }
    function play(name, vol) { try { sfx.pause(); sfx.src = "audio/fx/" + name + ".mp3?v=" + FXV; sfx.volume = vol || 0.8; var p = sfx.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {} }
    function end() { fadeTo(0); setTimeout(function () { bgm.pause(); }, 900); }
    return { watch: watch, start: start, play: play, end: end, started: function () { return started; } };
  })();
  FX.watch(aud);
  // 인사·명언만 (사진 클리닉 hte 처럼 QUESTIONS/showQuestion 이 없는 페이지): 첫 화면에서 인사, 결과 화면에서 명언
  if (CV.greetOnly) {
    if (window.twinAud) FX.watch(window.twinAud); // hte: 페이지 소리 나올 때 배경음악 줄이기
    if (typeof window.show === "function") {
      var origShow0 = window.show;
      window.show = function () {
        var r = origShow0.apply(this, arguments);
        if (!greeted && CV.noGreet) { greeted = true; FX.start(); }
        if (!greeted && !CV.noGreet) { greeted = true; FX.start(); aud.src = BASE + "g.mp3?v=" + (CV.ver || "1"); var p = aud.play(); if (p && p.catch) p.catch(function () {}); }
        return r;
      };
    }
    hookResult();
    return;
  }
  if (!window.QUESTIONS || typeof window.showQuestion !== "function" || typeof window.pick !== "function") return;
  // 페이지가 단어 소리를 직접 내는 경우(다은 jde: playQ 가 엠마 단어를 3번): 우리 인사·지시문 뒤에 페이지 소리를 이어서, 3번 다 들은 뒤 풀림
  var PAGE = !!(CV.pageAudio && typeof window.playQ === "function" && window.AUD);
  var origPlayQ = PAGE ? window.playQ : null, quietPage = false;
  if (PAGE) {
    FX.watch(window.AUD);
    window.playQ = function (i) { if (quietPage) return; return origPlayQ.apply(this, arguments); };
  }
  function pageSay(i, done) {
    var A = window.AUD, n = 0, fin = false, g = setTimeout(end, 9000);
    function end() { if (fin) return; fin = true; clearTimeout(g); A.removeEventListener("ended", on); A.removeEventListener("error", end); done(); }
    function on() { n++; if (n >= 3) end(); }
    A.addEventListener("ended", on); A.addEventListener("error", end);
    origPlayQ(i);
  }

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

  // 대화문은 줄마다 나뉜 파일 (q3_1, q3_2 …: A=지나티처, B=다른 목소리, A/B 는 읽지 않음)
  function parts(kind, n, cnt) {
    if (!cnt) return [];
    if (cnt === 1 || cnt === true) return [kind + n];
    var r = []; for (var i = 1; i <= cnt; i++) r.push(kind + n + "_" + i); return r;
  }
  function url(name) { return BASE + name + ".mp3?v=" + (CV.ver || "1"); }
  function stop() { playToken++; try { aud.pause(); } catch (e) {} try { if (PAGE) { clearTimeout(window.REPT); window.AUD.pause(); } } catch (e) {} }
  // 이름 목록을 차례로 재생, 끝나면 done(). 파일이 없거나 재생이 막히면 건너뜀. 안전장치: 한 파일당 최대 20초.
  function playSeq(names, done) {
    stop();
    var my = playToken, i = 0, guard = null;
    function next() {
      if (guard) { clearTimeout(guard); guard = null; }
      if (my !== playToken) return;
      if (i >= names.length) { if (done) done(); return; }
      var n = names[i++];
      // 소리가 안 나와도(파일 오류·재생 막힘) 바로 풀리지 않게 최소 2.5초는 잠가 둔다 (원장님 11/13 "다 듣기 전에는 아무것도 못 누르게")
      aud.onended = next; aud.onerror = function () { if (my !== playToken) return; clearTimeout(guard); guard = setTimeout(next, 2500); };
      guard = setTimeout(next, 45000);
      aud.src = url(n);
      var p = aud.play();
      if (p && p.catch) p.catch(function () { if (my === playToken) { clearTimeout(guard); guard = setTimeout(next, 2500); } });
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

  // ── 개념 먼저 (원장님 11/13 유정완: "지나선생님 목소리로 개념설명 하고 클리닉 진행") ──
  // voice.js 의 concepts:[{at:문항번호(0부터), title, body(html), c:소리 파일 수}] → 그 문항 앞에서 개념 카드 + cN(_k).mp3 (지나쌤 한글)
  //   끝까지 다 들어야 「이해했어요! 문제 풀기 ▶」가 열린다. 그동안 문제·보기·모름은 안 보이고 못 누른다.
  var CONC = CV.concepts || [], cdone = {};
  if (CONC.length) {
    var cst = document.createElement("style");
    cst.textContent = ".cv-concept{margin:6px 0 10px;border-radius:18px;padding:16px 16px 14px;background:linear-gradient(135deg,#eef4ff,#f3fbf6);border:2px solid #b9cdf3}" +
      ".cv-concept .h{font-size:13px;font-weight:800;color:#3a5bb8;letter-spacing:.3px}" +
      ".cv-concept .t{font-size:21px;font-weight:900;color:#1e2b55;margin:4px 0 10px;line-height:1.35}" +
      ".cv-concept .b{font-size:16.5px;line-height:1.7;color:#24304f}.cv-concept .b b{color:#c0392b}.cv-concept .b .ex{display:block;background:#fff;border-radius:10px;padding:6px 10px;margin:6px 0;font-weight:700;color:#1e2b55}" +
      ".cv-concept .b ul{margin:4px 0 4px 18px;padding:0}.cv-concept .b li{margin:3px 0}" +
      ".cv-hide{display:none!important}";
    document.head.appendChild(cst);
  }
  function conceptAt(idx) { for (var i = 0; i < CONC.length; i++) if (CONC[i].at === idx && !cdone[i]) return i; return -1; }
  function hideQ(on) {
    ["qtext", "choices", "part"].forEach(function (id) { var e = document.getElementById(id); if (e) e.classList.toggle("cv-hide", on); });
    document.querySelectorAll(".cv-bar").forEach(function (b) { b.classList.toggle("cv-hide", on); });
  }
  function showConcept(ci, pre, done) {
    var C = CONC[ci], q = document.getElementById("qtext");
    var box = document.createElement("div"); box.className = "cv-concept";
    box.innerHTML = '<div class="h">📘 개념 먼저! (' + (ci + 1) + " / " + CONC.length + ') · 끝까지 듣고 문제 풀어요</div><div class="t"></div><div class="b"></div>';
    box.querySelector(".t").textContent = C.title;
    box.querySelector(".b").innerHTML = C.body;
    var bar = document.createElement("div"); bar.className = "cv-bar";
    var again = document.createElement("button"); again.className = "cv-btn"; again.type = "button"; again.textContent = "🔊 설명 다시 듣기";
    bar.appendChild(again); box.appendChild(bar);
    var go = document.createElement("button"); go.className = "cv-next"; go.type = "button";
    box.appendChild(go);
    q.parentNode.insertBefore(box, q);
    var list = parts("c", ci + 1, C.c || 1);
    function run(l) {
      go.disabled = true; go.textContent = "👂 선생님 설명 듣는 중…"; again.disabled = true;
      playSeq(l, function () { go.disabled = false; go.textContent = "이해했어요! 문제 풀기 ▶"; again.disabled = false; });
    }
    again.onclick = function () { run(list); };
    go.onclick = function () { if (go.disabled) return; stop(); box.remove(); done(); };
    run(pre.concat(list));
    try { window.scrollTo({ top: 0, behavior: "smooth" }); } catch (e) {}
  }

  var origShow = window.showQuestion;
  window.showQuestion = function () {
    var r = origShow.apply(this, arguments);
    var idx = window.current;
    if (!FX.started()) FX.start();
    var ci = conceptAt(idx);
    if (ci >= 0) {
      cdone[ci] = 1;
      var pre = []; if (!greeted) { greeted = true; pre.push("g"); }
      hideQ(true);
      showConcept(ci, pre, function () { hideQ(false); startQ(idx); });
      return r;
    }
    startQ(idx);
    return r;
  };
  function startQ(idx) {
    var it = items[idx] || {}, n = idx + 1;
    var seq = [];
    if (!greeted) { greeted = true; seq.push("g"); }
    if (it.k) seq.push("k" + n);
    seq = seq.concat(parts("q", n, it.q));
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
    if (!qseq.length && !PAGE) { again.style.display = "none"; }
    function run(list) {
      setLocked(true); again.disabled = true; hint.style.display = "";
      var my;
      playSeq(list, function () {
        function open() { if (my !== playToken) return; setLocked(false); again.disabled = false; hint.style.display = "none"; }
        my = playToken;
        if (PAGE) pageSay(idx, open); else open();
      });
    }
    again.onclick = function () { run(qseq); };
    if (seq.length || PAGE) run(seq); else hint.style.display = "none";
  }

  // 11/14 원장님 목소리(v4) 칭찬·틀림·모름 한 마디 → 그다음 정답 문장. 원장님 선택: 칭찬 전부 3번
  var CHEER = {
    ok: ["praise/p1_3", "praise/p2_3", "praise/p3_3", "praise/p4_3", "praise/p5_3", "praise/p6_3", "praise/p7_3", "praise/p8_3", "praise/p9_3"],
    no: ["oops/p1_3", "oops/p2_3", "oops/p3_1", "oops/p4_3", "oops/p5_3"],
    un: ["oops/p6_3", "oops/p7_3", "oops/p8_3"]
  };
  var vfx = new Audio(); FX.watch(vfx);
  function cheer(kind, done) {
    var list = CHEER[kind] || [], fin = false;
    function f() { if (fin) return; fin = true; vfx.onended = vfx.onerror = null; done(); }
    if (!list.length) return f();
    vfx.onended = f; vfx.onerror = f; setTimeout(f, 4000);
    try { vfx.pause(); vfx.src = "audio/fx/" + list[Math.floor(Math.random() * list.length)] + ".mp3?v=1114"; var pr = vfx.play(); if (pr && pr.catch) pr.catch(f); } catch (e) { f(); }
  }
  var origPick = window.pick;
  window.pick = function (choice, mark, unknown) {
    if (window.locked) return;
    var idx = window.current, q = window.QUESTIONS[idx], it = items[idx] || {};
    var advance = null, realST = window.setTimeout;
    window.setTimeout = function (fn, ms) { advance = fn; return 0; };
    quietPage = true;
    try { origPick.apply(this, arguments); } finally { window.setTimeout = realST; quietPage = false; }
    if (!advance) return;
    stop();
    var ok = !unknown && choice === q.answer;
    if (!unknown) FX.play(ok ? "ding" : "oops", ok ? 0.75 : 0.55);
    var cheerKind = unknown ? "un" : (ok ? "ok" : "no");
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
      say.onclick = function () { nx.disabled = true; nx.textContent = "👂 듣는 중…"; playSeq(parts("a", idx + 1, it.a), ready); };
      p.appendChild(say);
      var aList = parts("a", idx + 1, it.a);
      setTimeout(function () { cheer(cheerKind, function () { if (!nx.disabled) return; playSeq(aList, ready); }); }, unknown ? 0 : 450);
    } else {
      setTimeout(function () { cheer(cheerKind, ready); }, unknown ? 0 : 450);
    }
    nx.onclick = function () { if (nx.disabled) return; stop(); p.remove(); advance(); };
    p.appendChild(nx);
    box.appendChild(p);
    try { p.scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch (e) {}
  };

  hookResult();
  // 마지막 명언 (audio/quotes/quotes.js 의 ENGFIT_QUOTES, 날짜+퀴즈 이름으로 돌아가며 하나)
  function hookResult() {
    if (typeof window.showResult !== "function") return;
    var origResult = window.showResult;
    window.showResult = function () {
      var r = origResult.apply(this, arguments);
      try { FX.end(); FX.play("tada", 0.8); } catch (e) {}
      try { setTimeout(function () { try { showQuote(); } catch (e) {} }, 2600); } catch (e) {}
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
