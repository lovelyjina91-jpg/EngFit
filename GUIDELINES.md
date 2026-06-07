<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>EngFit 단어 테스트 · Dreaming of My Future</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  :root{
    --navy:#1f2a52;
    --navy-d:#16203f;
    --navy-l:#27336b;
    --gold:#f0a830;
    --gold-d:#d68f15;
    --cream:#fdf9f0;
    --card:#ffffff;
    --ink:#1f2a52;
    --sub:#7c879e;
    --green:#16a673;
    --green-bg:#e6f8f0;
    --red:#e5484d;
    --red-bg:#fdeced;
    --line:#e9e4d8;
    --shadow:0 14px 36px rgba(13,19,43,.38);
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
  html,body{margin:0;height:100%;}
  body{
    font-family:'Noto Sans KR',sans-serif;
    color:var(--ink);
    display:flex;align-items:center;justify-content:center;
    min-height:100dvh;padding:16px;
    background:
      radial-gradient(circle at 50% -10%, rgba(240,168,48,.30) 0%, rgba(240,168,48,0) 42%),
      radial-gradient(circle at 12% 88%, rgba(240,168,48,.12) 0%, rgba(240,168,48,0) 30%),
      linear-gradient(165deg,#27336b 0%, #1f2a52 45%, #16203f 100%);
    position:relative;overflow-x:hidden;
  }
  /* retro badge motifs on background */
  body::before, body::after{
    content:'';position:fixed;border-radius:50%;pointer-events:none;
    border:2px dashed rgba(240,168,48,.28);
  }
  body::before{width:340px;height:340px;top:-130px;right:-110px;}
  body::after{width:260px;height:260px;bottom:-100px;left:-90px;}
  .eng{font-family:'Patrick Hand',cursive;}
  .app{
    width:100%;max-width:460px;background:var(--card);
    border-radius:26px;box-shadow:var(--shadow);
    overflow:hidden;position:relative;min-height:620px;
    display:flex;flex-direction:column;z-index:1;
    border:1px solid rgba(240,168,48,.35);
  }
  .logo{display:flex;align-items:center;}
  .logo svg{display:block;}
  .screen{flex:1;display:none;flex-direction:column;padding:26px 22px 24px;}
  .screen.on{display:flex;}

  /* START */
  #start{align-items:center;justify-content:center;text-align:center;gap:6px;
    background:
      radial-gradient(circle at 50% 0%, rgba(240,168,48,.10) 0%, rgba(240,168,48,0) 55%),
      var(--cream);
  }
  #start .badge{
    margin:6px 0 12px;width:190px;height:190px;border-radius:50%;
    background:#fff;border:2.5px solid var(--navy);
    box-shadow:0 0 0 7px var(--cream), 0 0 0 9px rgba(240,168,48,.85), 0 14px 26px rgba(31,42,82,.18);
    display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
    position:relative;
  }
  .badge .star{color:var(--gold);font-size:15px;letter-spacing:5px;}
  #start h1{margin:10px 0 2px;font-size:1.5em;font-weight:900;color:var(--navy);}
  #start .unit{font-family:'Patrick Hand',cursive;font-size:1.32em;color:var(--gold-d);}
  #start .meta{margin-top:5px;font-size:.92em;color:var(--sub);}
  .btn{
    border:none;border-radius:16px;cursor:pointer;font-family:'Noto Sans KR',sans-serif;
    font-weight:700;transition:transform .08s, box-shadow .2s, background .2s;
  }
  .btn:active{transform:scale(.97);}
  .btn-primary{
    background:var(--navy);color:#fff;font-size:1.08em;padding:16px 20px;width:100%;
    box-shadow:0 8px 18px rgba(31,42,82,.35);
  }
  .btn-primary:active{background:var(--navy-d);}
  #start .startwrap{width:100%;margin-top:20px;}

  /* QUIZ */
  #quiz{padding-top:18px;background:#fff;}
  .qtop{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}
  .count{font-size:.92em;color:var(--sub);font-weight:700;}
  .bar{height:8px;background:var(--line);border-radius:99px;overflow:hidden;margin-bottom:24px;}
  .bar > i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--gold),#f6c465);border-radius:99px;transition:width .3s;}
  .prompt{
    flex:0 0 auto;min-height:120px;display:flex;flex-direction:column;
    align-items:center;justify-content:center;text-align:center;gap:8px;margin-bottom:22px;
  }
  .qtag{font-size:.82em;font-weight:700;color:var(--gold-d);background:rgba(240,168,48,.14);padding:5px 12px;border-radius:99px;}
  .qword-en{font-family:'Patrick Hand',cursive;font-size:2.6em;line-height:1.1;color:var(--navy);}
  .qword-ko{font-family:'Noto Sans KR',sans-serif;font-size:1.65em;font-weight:700;line-height:1.3;color:var(--navy);}
  .choices{display:flex;flex-direction:column;gap:11px;margin-top:auto;}
  .choice{
    width:100%;text-align:center;background:#fff;border:2px solid var(--line);
    border-radius:16px;padding:15px 14px;cursor:pointer;color:var(--ink);
    transition:border-color .15s, background .15s, transform .08s;
  }
  .choice:active{transform:scale(.98);}
  .choice.ko{font-family:'Noto Sans KR',sans-serif;font-size:0.96em;font-weight:500;}
  .choice.en{font-family:'Patrick Hand',cursive;font-size:1.44em;}
  .choice.correct{border-color:var(--green);background:var(--green-bg);color:var(--green);font-weight:700;}
  .choice.wrong{border-color:var(--red);background:var(--red-bg);color:var(--red);}
  .choice.lock{pointer-events:none;}
  .choice .num{
    display:inline-flex;align-items:center;justify-content:center;
    width:22px;height:22px;border-radius:7px;margin-right:9px;
    background:rgba(31,42,82,.07);color:var(--sub);
    font-family:'Noto Sans KR',sans-serif;font-size:.72rem;font-weight:700;vertical-align:middle;
  }
  .choice.correct .num{background:rgba(22,166,115,.15);color:var(--green);}
  .choice.wrong .num{background:rgba(229,72,77,.15);color:var(--red);}

  /* 주관식 */
  .typebox{display:flex;flex-direction:column;gap:11px;margin-top:auto;}
  .typebox input{
    width:100%;text-align:center;background:#fff;border:2px solid var(--line);
    border-radius:16px;padding:14px;color:var(--ink);outline:none;
    font-family:'Patrick Hand',cursive;font-size:1.44em;
    transition:border-color .15s, background .15s;
  }
  .typebox input:focus{border-color:var(--gold);}
  .typebox input.correct{border-color:var(--green);background:var(--green-bg);color:var(--green);font-weight:700;}
  .typebox input.wrong{border-color:var(--red);background:var(--red-bg);color:var(--red);}
  .typeanswer{
    text-align:center;font-size:1em;color:var(--green);font-weight:700;display:none;
  }
  .typeanswer .eng{font-size:1.35em;}
  .typehint{text-align:center;font-size:.8em;color:var(--sub);}
  .kbdhint{margin-top:10px;font-size:.8em;color:var(--sub);}
  .kbdhint b{color:var(--gold-d);}

  /* RESULT */
  #result{padding-top:20px;
    background:
      radial-gradient(circle at 50% 0%, rgba(240,168,48,.10) 0%, rgba(240,168,48,0) 50%),
      var(--cream);
  }
  #result .logo{justify-content:center;margin-bottom:8px;}
  .scorecard{text-align:center;margin:6px 0 18px;}
  .scorecard .emoji{font-size:46px;}
  .scorecard .score{font-size:2.4em;font-weight:900;margin-top:4px;color:var(--navy);}
  .scorecard .score small{font-size:.42em;color:var(--sub);font-weight:700;}
  .scorecard .pct{font-size:1em;color:var(--gold-d);font-weight:700;margin-top:2px;}
  .reviewhead{font-size:.95em;font-weight:700;margin:6px 2px 10px;display:flex;justify-content:space-between;align-items:center;color:var(--navy);}
  .reviewhead .ok{color:var(--green);font-size:.92em;}
  .review{display:flex;flex-direction:column;gap:9px;max-height:240px;overflow-y:auto;padding:2px;}
  .ritem{border:1.5px solid var(--red-bg);background:#fff;border-radius:14px;padding:11px 13px;border-left:5px solid var(--red);}
  .ritem .q{font-size:.8em;color:var(--sub);font-weight:600;margin-bottom:3px;}
  .ritem .ans{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline;font-size:.95em;}
  .ritem .yours{color:var(--red);} .ritem .yours s{opacity:.8;}
  .ritem .right{color:var(--green);font-weight:700;}
  .ritem b.eng{font-family:'Patrick Hand',cursive;font-size:1.2em;font-weight:400;color:var(--navy);}
  .allright{text-align:center;color:var(--green);font-weight:700;padding:18px;background:var(--green-bg);border-radius:14px;}
  .actions{margin-top:16px;display:flex;flex-direction:column;gap:10px;}
  .btn-kakao{background:#FEE500;color:#3a1d1d;font-size:1.04em;padding:15px;width:100%;display:flex;align-items:center;justify-content:center;gap:8px;}
  .btn-ghost{background:#efe9db;color:var(--navy);font-size:1em;padding:14px;width:100%;}
  .toast{
    position:absolute;left:50%;bottom:26px;transform:translateX(-50%) translateY(20px);
    background:var(--navy);color:#fff;padding:11px 18px;border-radius:99px;font-size:.9em;font-weight:600;
    opacity:0;pointer-events:none;transition:.25s;white-space:nowrap;
  }
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
</style>
</head>
<body>
<div class="app">

  <!-- START -->
  <section id="start" class="screen on">
    <div class="badge">
      <span class="star">★ ★ ★</span>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 150" width="150" role="img" aria-label="영핏 EngFit 로고">
        <g>
          <polygon points="60,18 100,40 60,62 20,40" fill="#1f2a52"/>
          <polygon points="20,40 60,62 60,108 20,86" fill="#27336b"/>
          <polygon points="60,62 100,40 100,86 60,108" fill="#1f2a52"/>
          <polygon points="78,51 88,57 88,97 78,91" fill="#f0a830"/>
          <polygon points="74,29 84,35 78,38 68,32" fill="#f0a830"/>
        </g>
        <text x="120" y="78" font-family="'Noto Sans KR',sans-serif" font-size="58" font-weight="800" fill="#1f2a52" letter-spacing="2">영핏</text>
        <text x="122" y="104" font-family="'Noto Sans KR',sans-serif" font-size="15" font-weight="600" letter-spacing="3" fill="#6b7280">영어를 <tspan fill="#1f2a52" font-weight="800">핏</tspan><tspan fill="#6b7280">하다</tspan></text>
      </svg>
      <span class="star">★ ★ ★</span>
    </div>
    <h1>단어 테스트</h1>
    <div class="unit eng">4. Dreaming of My Future</div>
    <div class="meta">천재(정사열) 중3 영어 · 전체 60문항 랜덤</div>
    <div class="meta">영어↔한글 혼합 + 주관식(영어 쓰기) 출제</div>
    <div class="kbdhint">💻 키보드 <b>1~4</b>로 보기 선택 · 주관식은 <b>Enter</b>로 제출</div>
    <div class="startwrap">
      <button class="btn btn-primary" onclick="startQuiz()">시작하기</button>
    </div>
  </section>

  <!-- QUIZ -->
  <section id="quiz" class="screen">
    <div class="qtop">
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 120" width="92" role="img" aria-label="영핏 로고">
          <g>
            <polygon points="60,8 100,30 60,52 20,30" fill="#1f2a52"/>
            <polygon points="20,30 60,52 60,98 20,76" fill="#27336b"/>
            <polygon points="60,52 100,30 100,76 60,98" fill="#1f2a52"/>
            <polygon points="78,41 88,47 88,87 78,81" fill="#f0a830"/>
            <polygon points="74,19 84,25 78,28 68,22" fill="#f0a830"/>
          </g>
          <text x="118" y="74" font-family="'Noto Sans KR',sans-serif" font-size="56" font-weight="800" fill="#1f2a52" letter-spacing="2">영핏</text>
        </svg>
      </div>
      <div class="count"><span id="cur">1</span> / <span id="total">60</span></div>
    </div>
    <div class="bar"><i id="prog"></i></div>
    <div class="prompt">
      <span class="qtag" id="qtag">뜻 고르기</span>
      <div id="promptword"></div>
    </div>
    <div class="choices" id="choices"></div>
    <div class="typebox" id="typebox" style="display:none">
      <input type="text" id="typeinput" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="영어로 입력하세요">
      <div class="typeanswer" id="typeanswer"></div>
      <button class="btn btn-primary" id="typebtn" onclick="submitTyping()">제출 (Enter ⏎)</button>
      <div class="typehint">대소문자는 구분하지 않아요</div>
    </div>
  </section>

  <!-- RESULT -->
  <section id="result" class="screen">
    <div class="logo">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 150" width="120" role="img" aria-label="영핏 EngFit 로고">
        <g>
          <polygon points="60,18 100,40 60,62 20,40" fill="#1f2a52"/>
          <polygon points="20,40 60,62 60,108 20,86" fill="#27336b"/>
          <polygon points="60,62 100,40 100,86 60,108" fill="#1f2a52"/>
          <polygon points="78,51 88,57 88,97 78,91" fill="#f0a830"/>
          <polygon points="74,29 84,35 78,38 68,32" fill="#f0a830"/>
        </g>
        <text x="120" y="78" font-family="'Noto Sans KR',sans-serif" font-size="58" font-weight="800" fill="#1f2a52" letter-spacing="2">영핏</text>
        <text x="122" y="104" font-family="'Noto Sans KR',sans-serif" font-size="15" font-weight="600" letter-spacing="3" fill="#6b7280">영어를 <tspan fill="#1f2a52" font-weight="800">핏</tspan><tspan fill="#6b7280">하다</tspan></text>
      </svg>
    </div>
    <div class="scorecard">
      <div class="emoji" id="remoji">🎉</div>
      <div class="score"><span id="rscore">0</span><small> / <span id="rtotal">60</span></small></div>
      <div class="pct" id="rpct">0%</div>
    </div>
    <div class="reviewhead"><span id="rvtitle">오답 확인</span><span class="ok" id="rvok"></span></div>
    <div class="review" id="review"></div>
    <div class="actions">
      <button class="btn btn-kakao" onclick="copyResult()">📋 결과 복사하기 (카카오톡 전송용)</button>
      <button class="btn btn-ghost" onclick="restart()">다시 풀기 🔄</button>
    </div>
  </section>

  <div class="toast" id="toast">복사되었습니다!</div>
</div>

<script>
/* ===== 단어 데이터: 4. Dreaming of My Future (60) ===== */
const WORDS = [
  {en:"look down", ko:"우울해 보이다"},
  {en:"disappointed", ko:"실망한"},
  {en:"competition", ko:"대회, 시합"},
  {en:"record", ko:"기록"},
  {en:"cook", ko:"요리사"},
  {en:"laugh at", ko:"…을 비웃다"},
  {en:"give up", ko:"포기하다"},
  {en:"lose", ko:"지다, 패배하다"},
  {en:"match", ko:"시합, 경기"},
  {en:"presentation", ko:"발표"},
  {en:"speech", ko:"연설, 말"},
  {en:"a little", ko:"약간, 조금"},
  {en:"tip", ko:"조언"},
  {en:"dish", ko:"요리"},
  {en:"against", ko:"…에 반대하여"},
  {en:"grade", ko:"성적"},
  {en:"Why don't you ...?", ko:"…하는 게 어때?"},
  {en:"hidden", ko:"숨겨진, 비밀의"},
  {en:"figure", ko:"(중요한) 인물, 숫자"},
  {en:"career", ko:"직업, 직장 생활"},
  {en:"space", ko:"우주"},
  {en:"expert", ko:"전문가"},
  {en:"get over", ko:"…을 극복하다"},
  {en:"manager", ko:"관리자, 경영자"},
  {en:"recognize", ko:"알아보다, 인정하다"},
  {en:"ability", ko:"능력"},
  {en:"colored", ko:"유색 인종의"},
  {en:"courage", ko:"용기"},
  {en:"break down", ko:"…을 부수다"},
  {en:"rocket", ko:"로켓"},
  {en:"allow", ko:"허락하다"},
  {en:"judge", ko:"판사"},
  {en:"permission", ko:"허락"},
  {en:"have no choice but to", ko:"…할 수밖에 없다"},
  {en:"impress", ko:"감명을 주다"},
  {en:"stand up for", ko:"…을 옹호하다"},
  {en:"engineer", ko:"기술자"},
  {en:"install", ko:"설치하다"},
  {en:"later", ko:"나중에, 후에"},
  {en:"offer", ko:"제의, 제안"},
  {en:"thanks to", ko:"… 덕분에"},
  {en:"programmer", ko:"프로그래머"},
  {en:"be afraid of", ko:"…을 두려워하다"},
  {en:"face", ko:"(상황에) 직면하다"},
  {en:"laughter", ko:"웃음(소리)"},
  {en:"job festival", ko:"진로 박람회"},
  {en:"magician", ko:"마술사"},
  {en:"keep -ing", ko:"계속 …하다"},
  {en:"help", ko:"도움이 되다"},
  {en:"keep ... in mind", ko:"…을 명심하다"},
  {en:"reporter", ko:"기자"},
  {en:"baker", ko:"제빵사"},
  {en:"control", ko:"조종하다"},
  {en:"magic trick", ko:"마술 묘기"},
  {en:"line", ko:"(연극, 영화의) 대사"},
  {en:"decorate", ko:"장식하다"},
  {en:"let", ko:"~하게 하다"},
  {en:"enter", ko:"들어가다, 참가하다"},
  {en:"audition", ko:"오디션"},
  {en:"prepare", ko:"준비하다"}
];

let queue=[], idx=0, score=0, wrongs=[], locked=false;

function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function show(id){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('on'));document.getElementById(id).classList.add('on');}

function buildQuestion(word){
  // 주관식: 한글 뜻 → 영어 입력 (… / ? 포함 표현은 객관식만)
  const canType = !/[.?…]/.test(word.en);
  if(canType && Math.random()<0.35){
    return {word, type:'typing'};
  }
  // 객관식 방향 랜덤: en2ko = 영어 제시→한글 보기 / ko2en = 한글 제시→영어 보기
  const dir = Math.random()<0.5 ? 'en2ko' : 'ko2en';
  const key = dir==='en2ko' ? 'ko' : 'en';
  const distractPool = shuffle(WORDS.filter(w=>w.en!==word.en));
  const opts=[word];
  for(const w of distractPool){
    if(opts.length>=4) break;
    if(opts.some(o=>o[key]===w[key])) continue; // 중복 보기 방지
    opts.push(w);
  }
  return {word, type:'mc', dir, key, options:shuffle(opts)};
}

function startQuiz(){
  queue = shuffle(WORDS).map(buildQuestion);
  idx=0; score=0; wrongs=[];
  document.getElementById('total').textContent=queue.length;
  show('quiz');
  render();
}

function render(){
  locked=false;
  const q=queue[idx];
  document.getElementById('cur').textContent=idx+1;
  document.getElementById('prog').style.width=((idx)/queue.length*100)+'%';

  const pw=document.getElementById('promptword');
  const tag=document.getElementById('qtag');
  const box=document.getElementById('choices');
  const tbox=document.getElementById('typebox');

  if(q.type==='typing'){
    tag.textContent='영어로 쓰기 ⏎';
    pw.className='qword-ko';
    pw.textContent=q.word.ko;
    box.style.display='none';
    tbox.style.display='flex';
    const inp=document.getElementById('typeinput');
    inp.value=''; inp.className=''; inp.disabled=false;
    document.getElementById('typeanswer').style.display='none';
    inp.focus();
    return;
  }

  tbox.style.display='none';
  box.style.display='flex';
  if(q.dir==='en2ko'){
    tag.textContent='뜻 고르기';
    pw.className='qword-en eng';
    pw.textContent=q.word.en;
  }else{
    tag.textContent='단어 고르기';
    pw.className='qword-ko';
    pw.textContent=q.word.ko;
  }

  box.innerHTML='';
  q.options.forEach((opt,i)=>{
    const b=document.createElement('button');
    const isEn = q.key==='en';
    b.className='choice '+(isEn?'en eng':'ko');
    b.dataset.val=opt[q.key];
    const num=document.createElement('span');
    num.className='num'; num.textContent=i+1;
    b.appendChild(num);
    b.appendChild(document.createTextNode(opt[q.key]));
    b.onclick=()=>choose(b,opt,q);
    box.appendChild(b);
  });
}

function choose(btn,opt,q){
  if(locked) return;
  locked=true;
  const correct = opt.en===q.word.en;
  const buttons=[...document.getElementById('choices').children];
  buttons.forEach(b=>b.classList.add('lock'));

  if(correct){
    btn.classList.add('correct');
    score++;
    setTimeout(next,250); // 정답 → 0.25초 후 넘어가기
  }else{
    btn.classList.add('wrong');
    buttons.forEach(b=>{ if(b.dataset.val===q.word[q.key]) b.classList.add('correct'); });
    wrongs.push({
      dir:q.dir,
      en:q.word.en, ko:q.word.ko,
      chosen: opt[q.key], correct:q.word[q.key], key:q.key
    });
    setTimeout(next,900); // 오답 → 잠시 보여주고 넘어가기
  }
}

/* ===== 주관식 채점 (대소문자 구분 없음) ===== */
function norm(s){
  return s.toLowerCase()
    .replace(/[’‘`]/g,"'")
    .replace(/\s+/g,' ')
    .trim();
}
function submitTyping(){
  if(locked) return;
  const q=queue[idx];
  if(!q || q.type!=='typing') return;
  const inp=document.getElementById('typeinput');
  const val=inp.value;
  if(norm(val)==='') { inp.focus(); return; } // 빈 입력은 제출 안 됨
  locked=true;
  inp.disabled=true;
  const correct = norm(val)===norm(q.word.en);
  if(correct){
    inp.classList.add('correct');
    score++;
    setTimeout(next,250); // 정답 → 0.25초 후 넘어가기
  }else{
    inp.classList.add('wrong');
    const ans=document.getElementById('typeanswer');
    ans.innerHTML='정답: <b class="eng">'+q.word.en+'</b>';
    ans.style.display='block';
    wrongs.push({
      dir:'typing',
      en:q.word.en, ko:q.word.ko,
      chosen: val.trim(), correct:q.word.en, key:'en'
    });
    setTimeout(next,1500); // 오답 → 정답 보여주고 넘어가기
  }
}

/* ===== 키보드 조작: 1~4 보기 선택 / Enter 주관식 제출 ===== */
document.addEventListener('keydown',function(e){
  if(!document.getElementById('quiz').classList.contains('on')) return;
  const q=queue[idx];
  if(!q || locked) return;
  if(q.type==='mc'){
    const n={'1':0,'2':1,'3':2,'4':3}[e.key];
    if(n!==undefined){
      const b=document.getElementById('choices').children[n];
      if(b){ e.preventDefault(); b.click(); }
    }
  }else if(q.type==='typing' && e.key==='Enter'){
    e.preventDefault();
    submitTyping();
  }
});

function next(){
  idx++;
  if(idx>=queue.length){ finish(); }
  else render();
}

function finish(){
  document.getElementById('prog').style.width='100%';
  const total=queue.length;
  const pct=Math.round(score/total*100);
  document.getElementById('rscore').textContent=score;
  document.getElementById('rtotal').textContent=total;
  document.getElementById('rpct').textContent=pct+'%';
  document.getElementById('remoji').textContent = pct===100?'🏆': pct>=80?'🎉': pct>=60?'👍':'💪';

  const review=document.getElementById('review');
  const ok=document.getElementById('rvok');
  const title=document.getElementById('rvtitle');
  review.innerHTML='';
  if(wrongs.length===0){
    title.textContent='오답 확인';
    ok.textContent='';
    review.innerHTML='<div class="allright">완벽해요! 틀린 단어가 없어요 ✨</div>';
  }else{
    title.textContent='오답 확인 ('+wrongs.length+')';
    ok.textContent='맞은 단어 '+score+'개';
    wrongs.forEach(w=>{
      const enB='<b class="eng">'+w.en+'</b>';
      const div=document.createElement('div');
      div.className='ritem';
      div.innerHTML =
        '<div class="q">'+enB+' &nbsp;—&nbsp; '+w.ko+'</div>'+
        '<div class="ans"><span class="yours">내 답: <s>'+w.chosen+'</s></span>'+
        '<span class="right">정답: '+w.correct+'</span></div>';
      review.appendChild(div);
    });
  }
  show('result');
}

function copyResult(){
  const total=queue.length, pct=Math.round(score/total*100);
  let t='[EngFit 단어 테스트]\n4. Dreaming of My Future (천재 정사열·중3)\n\n';
  t+='점수: '+score+'/'+total+' ('+pct+'%)\n';
  t+='날짜: '+new Date().toLocaleDateString('ko-KR')+'\n';
  if(wrongs.length===0){
    t+='\n🏆 모두 정답! 완벽합니다.';
  }else{
    t+='\n■ 틀린 단어 ('+wrongs.length+')\n';
    wrongs.forEach((w,i)=>{ t+=(i+1)+'. '+w.en+' - '+w.ko+'\n'; });
  }
  const done=()=>showToast('복사되었습니다!');
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(t).then(done).catch(()=>fallbackCopy(t,done));
  }else{ fallbackCopy(t,done); }
}
function fallbackCopy(text,cb){
  const ta=document.createElement('textarea');
  ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.focus(); ta.select();
  try{document.execCommand('copy');}catch(e){}
  document.body.removeChild(ta); cb&&cb();
}
let toastT;
function showToast(msg){
  const el=document.getElementById('toast');
  el.textContent=msg; el.classList.add('show');
  clearTimeout(toastT); toastT=setTimeout(()=>el.classList.remove('show'),1600);
}
function restart(){ show('start'); }
</script>
<!-- v2: keyboard 1-4 + typing(Enter, case-insensitive) -->
</body>
</html>
