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
  // ── 소리 파형 (원장님 11/15 "파형이 있으면 들린다는 심리, 안 들으면 미치게") ──
  // 목소리가 나오는 동안 화면 아래 가운데 작은 파형이 춤춘다. 소리를 꺼 두면 파형만 움직이는 걸 보며 기다려야 함.
  var WAVE = (function () {
    var live = [], box = null, cv = null, cx = null, lab = null, raf = 0, amp = 0, t0 = 0, N = 22, ph = [];
    for (var i = 0; i < N; i++) ph.push(Math.random() * 6.28);
    function ensure() {
      if (box || !document.body) return;
      box = document.createElement("div");
      box.style.cssText = "position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:9998;display:flex;align-items:center;gap:8px;padding:6px 14px 6px 10px;border-radius:999px;background:rgba(255,255,255,.96);box-shadow:0 2px 12px rgba(0,0,0,.16);pointer-events:none;font-family:inherit;transition:opacity .3s";
      cv = document.createElement("canvas"); cv.width = 132 * 2; cv.height = 30 * 2; cv.style.cssText = "width:132px;height:30px;display:block";
      lab = document.createElement("span"); lab.style.cssText = "font-size:13px;font-weight:800;color:#2a3a8c;white-space:nowrap";
      box.appendChild(cv); box.appendChild(lab); document.body.appendChild(box); cx = cv.getContext("2d"); draw();
    }
    function speaking() { for (var i = 0; i < live.length; i++) if (!live[i].paused && !live[i].ended) return true; return false; }
    function draw() {
      if (!cx) return;
      var on = speaking(); amp += ((on ? 1 : 0) - amp) * 0.12;
      var W = cv.width, H = cv.height, bw = W / N; cx.clearRect(0, 0, W, H);
      var t = (Date.now() - t0) / 1000;
      for (var i = 0; i < N; i++) {
        var e = 0.35 + 0.65 * Math.abs(Math.sin(t * (5 + i % 5) + ph[i]) * Math.sin(t * 2.3 + i * 0.7));
        var h = Math.max(4, (H - 8) * e * amp + 6 * (1 - amp));
        cx.fillStyle = on ? "hsl(" + (210 + i * 5) + ",75%,52%)" : "#c9cfdf";
        var x = i * bw + bw * 0.2, w = bw * 0.6, y = (H - h) / 2;
        cx.beginPath(); if (cx.roundRect) cx.roundRect(x, y, w, h, w / 2); else cx.rect(x, y, w, h); cx.fill();
      }
      lab.textContent = on ? "🔊 지나티처가 말하는 중" : "🔊 소리 켜 두기!";
      lab.style.color = on ? "#2a3a8c" : "#8a93ad";
      if (on || amp > 0.02) raf = requestAnimationFrame(draw); else raf = 0;
    }
    function kick() { ensure(); if (!raf) { t0 = t0 || Date.now(); raf = requestAnimationFrame(draw); } }
    function watch(a) {
      if (!a || a.__wv) return; a.__wv = 1; live.push(a);
      a.addEventListener("playing", kick); a.addEventListener("pause", kick); a.addEventListener("ended", kick);
    }
    return { watch: watch, show: ensure };
  })();
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
      if (!a || a.__fxw) return; a.__fxw = 1; WAVE.watch(a);
      a.addEventListener("playing", function () { speaking = 1; fadeTo(target()); });
      var off = function () { setTimeout(function () { if (a.paused || a.ended) { speaking = 0; fadeTo(target()); } }, 350); };
      a.addEventListener("pause", off); a.addEventListener("ended", off); a.addEventListener("error", off);
    }
    function paint() { if (btn) { btn.textContent = on ? "🎵" : "🔇"; btn.title = on ? "배경음악 끄기" : "배경음악 켜기"; } }
    function start() {
      started = true; WAVE.show();
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
    if (window.twinAud) FX.watch(window.twinAud); if (window.cheerAud) FX.watch(window.cheerAud); // hte: 페이지 소리 나올 때 배경음악 줄이기
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

  // ── 소리 확인 (원장님 11/15 "소리를 안 듣고는 못 배기게") ──
  // 첫 문제 전에 단어 하나를 들려주고 그림 3개 중 고르기. 2번 연속 맞혀야 시작. 다 듣기 전에는 그림 잠금.
  // 소리 파일이 아예 안 열리면(오류) 막히지 않게 통과.
  var SC = [["bear","🐻"],["car","🚗"],["cow","🐄"],["egg","🥚"],["fish","🐟"],["fox","🦊"],["lion","🦁"],["pig","🐷"],["pizza","🍕"],["plane","✈️"],["rabbit","🐰"],["robot","🤖"],["ship","🚢"],["snake","🐍"],["star","⭐"],["sun","☀️"],["tiger","🐯"],["train","🚆"],["tree","🌳"],["umbrella","☂️"],["whale","🐳"],["zebra","🦓"],["octopus","🐙"],["elephant","🐘"],["drum","🥁"],["house","🏠"]];
  var soundOK = false; try { if (new URLSearchParams(location.search).get("t") === "1") soundOK = true; } catch (e) {}
  function soundCheck(done) {
    var sa = new Audio(); FX.watch(sa);
    var ov = document.createElement("div");
    ov.style.cssText = "position:fixed;inset:0;z-index:9997;background:rgba(20,28,60,.55);display:flex;align-items:center;justify-content:center;padding:16px";
    ov.innerHTML = '<div style="background:#fff;border-radius:22px;max-width:420px;width:100%;padding:22px 18px 18px;text-align:center;font-family:inherit;box-shadow:0 8px 30px rgba(0,0,0,.25)">' +
      '<div style="font-size:22px;font-weight:900;color:#1e2b55">🔊 소리 확인!</div>' +
      '<div class="sc-msg" style="font-size:16px;color:#444;margin:8px 0 14px;line-height:1.5">소리를 <b style="color:#c0392b">최대로</b> 키우고<br>들리는 단어의 그림을 눌러요</div>' +
      '<div class="sc-ch" style="display:flex;gap:10px;justify-content:center"></div>' +
      '<div class="sc-dots" style="margin:14px 0 10px;font-size:20px;letter-spacing:6px"></div>' +
      '<button type="button" class="sc-again cv-btn">🔊 다시 듣기</button></div>';
    document.body.appendChild(ov);
    var ch = ov.querySelector(".sc-ch"), msg = ov.querySelector(".sc-msg"), dots = ov.querySelector(".sc-dots"), again = ov.querySelector(".sc-again");
    var need = 2, got = 0, ans = null, errs = 0, last = "";
    function paintDots() { var s = ""; for (var i = 0; i < need; i++) s += i < got ? "🟢" : "⚪"; dots.textContent = s; }
    function lock(on) { ch.querySelectorAll("button").forEach(function (b) { b.disabled = on; b.style.opacity = on ? .45 : 1; }); again.disabled = on; }
    function say() {
      lock(true);
      sa.onended = function () { lock(false); };
      sa.onerror = function () { errs++; if (errs >= 2) { finish(); } else { lock(false); } };
      sa.src = "audio/emma/" + ans[0] + ".mp3?v=1";
      var p = sa.play(); if (p && p.catch) p.catch(function () { lock(false); });
    }
    function round() {
      var pool = SC.filter(function (w) { return w[0] !== last; }), pick3 = [];
      while (pick3.length < 3) { var w = pool[Math.floor(Math.random() * pool.length)]; if (pick3.indexOf(w) < 0) pick3.push(w); }
      ans = pick3[Math.floor(Math.random() * 3)]; last = ans[0];
      ch.innerHTML = "";
      pick3.forEach(function (w) {
        var b = document.createElement("button"); b.type = "button"; b.textContent = w[1];
        b.style.cssText = "font-size:46px;width:96px;height:96px;border-radius:18px;border:3px solid #d8def8;background:#f6f8ff;cursor:pointer";
        b.onclick = function () {
          if (b.disabled) return;
          if (w === ans) { got++; paintDots(); if (got >= need) { msg.innerHTML = "<b style='color:#2e9e5b'>잘 들려요! 시작해요 👏</b>"; lock(true); var pl = ["praise/p1_3", "praise/p2_3", "praise/p3_3", "praise/p4_3", "praise/p5_3", "praise/p6_3", "praise/p7_3", "praise/p8_3", "praise/p9_3"]; sa.onended = sa.onerror = finish; setTimeout(finish, 5000); sa.src = "audio/fx/" + pl[Math.floor(Math.random() * pl.length)] + ".mp3?v=1114"; var pp = sa.play(); if (pp && pp.catch) pp.catch(function () { setTimeout(finish, 600); }); return; } msg.innerHTML = "맞았어요! 하나 더 👂"; }
          else { got = 0; FX.play("oops", 0.55); paintDots(); msg.innerHTML = "<b style='color:#c0392b'>앗! 소리가 안 들렸나요?</b><br>볼륨을 <b>끝까지</b> 올리고 다시 들어 봐요"; }
          setTimeout(function () { round(); say(); }, 700);
        };
        ch.appendChild(b);
      });
    }
    function finish() { if (soundOK) return; soundOK = true; try { sa.pause(); } catch (e) {} ov.remove(); done(); }
    again.onclick = function () { if (!again.disabled) say(); };
    paintDots(); round(); say();
  }

  var origShow = window.showQuestion;
  window.showQuestion = function () {
    var self = this, args = arguments;
    if (!soundOK) {
      if (!FX.started()) FX.start();
      soundCheck(function () { window.showQuestion.apply(self, args); });
      return;
    }
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
    if (!unknown && !ok) FX.play("oops", 0.55); // 원장님 11/15 "맞을 때 땡 소리 말고 지나티처 목소리만"
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
