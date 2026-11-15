/* 영핏 링크 비밀번호 (원장님 11/15)
   한 번 맞히면 그 기기에서는 다시 안 물어봄. 비밀번호 바꾸려면 H 값과 KEY 를 바꾸면 됨. */
(function () {
  var KEY = "engfit_gate_v1";
  var H = "f18d";
  function hash(s) { var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) & 0xffff; return h.toString(16); }
  function ok() { try { if (localStorage.getItem(KEY) === H) return true; } catch (e) {} try { if (sessionStorage.getItem(KEY) === H) return true; } catch (e) {} return false; }
  function save() { try { localStorage.setItem(KEY, H); } catch (e) {} try { sessionStorage.setItem(KEY, H); } catch (e) {} }
  if (ok()) return;

  var root = document.documentElement;
  root.classList.add("engfit-locked");
  var st = document.createElement("style");
  st.textContent =
    "html.engfit-locked body>*:not(#engfit-gate){display:none!important}" +
    "html.engfit-locked body{overflow:hidden!important}" +
    "#engfit-gate{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;" +
    "background:linear-gradient(160deg,#5b3fd6,#2fa3e6);font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;padding:16px;box-sizing:border-box}" +
    "#engfit-gate .bx{background:#fff;border-radius:22px;padding:28px 22px;width:100%;max-width:340px;text-align:center;box-shadow:0 12px 40px rgba(0,0,0,.25)}" +
    "#engfit-gate .lg{font-size:30px;font-weight:900;color:#5b3fd6;letter-spacing:1px}" +
    "#engfit-gate .t{font-size:17px;color:#333;margin:10px 0 16px;font-weight:700}" +
    "#engfit-gate input{width:100%;box-sizing:border-box;font-size:32px;text-align:center;letter-spacing:14px;padding:12px;border:3px solid #c9bdf5;border-radius:14px;outline:none}" +
    "#engfit-gate input:focus{border-color:#5b3fd6}" +
    "#engfit-gate button{margin-top:14px;width:100%;font-size:19px;font-weight:800;color:#fff;background:#5b3fd6;border:0;border-radius:14px;padding:14px;cursor:pointer}" +
    "#engfit-gate .m{min-height:22px;margin-top:10px;font-size:15px;color:#e0435a;font-weight:700}" +
    "#engfit-gate .shake{animation:egs .35s}@keyframes egs{0%,100%{transform:translateX(0)}25%{transform:translateX(-9px)}75%{transform:translateX(9px)}}";
  (document.head || root).appendChild(st);

  function build() {
    if (document.getElementById("engfit-gate")) return;
    var g = document.createElement("div");
    g.id = "engfit-gate";
    g.innerHTML = '<div class="bx"><div class="lg">🧊 EngFit</div><div class="t">🔒 비밀번호 4자리를 넣어요</div>' +
      '<input id="engfit-pw" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="4" autocomplete="off">' +
      '<button id="engfit-go">들어가기 ▶</button><div class="m" id="engfit-m"></div></div>';
    document.body.appendChild(g);
    var inp = document.getElementById("engfit-pw"), m = document.getElementById("engfit-m"), bx = g.firstChild;
    function tryIt() {
      if (hash(inp.value.trim()) === H) {
        save(); root.classList.remove("engfit-locked"); g.parentNode.removeChild(g);
      } else {
        m.textContent = "비밀번호가 달라요. 지나쌤께 물어봐요!"; inp.value = "";
        bx.classList.remove("shake"); void bx.offsetWidth; bx.classList.add("shake"); inp.focus();
      }
    }
    document.getElementById("engfit-go").onclick = tryIt;
    inp.addEventListener("keydown", function (e) { if (e.key === "Enter") tryIt(); });
    inp.addEventListener("input", function () { if (inp.value.length === 4) tryIt(); });
    setTimeout(function () { try { inp.focus(); } catch (e) {} }, 50);
  }
  if (document.body) build(); else document.addEventListener("DOMContentLoaded", build);
})();
