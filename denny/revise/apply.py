# -*- coding: utf-8 -*-
"""개정된 뜻을 모아 glossary.json 을 만든다. (단어(소문자) → 새 뜻)

  A  Step 3 개정판에서 승계   (새로 쓴 글자 없음)
  B  원본의 여러 뜻을 병합     (새로 쓴 글자 없음)
  C  직접 새로 씀              (chunks/ ↔ done/)
  D  손대지 않음               (glossary 에 넣지 않음)
"""
import json, os
def width(s): return sum(2 if ord(c)>0x1100 and not c.isascii() else 1 for c in s)
here=os.path.dirname(os.path.abspath(__file__))
p2=json.load(open(os.path.join(here,"plan2.json"),encoding="utf-8"))
def scrub(m):
    """원본 수식 오류(#NAME? 등)가 섞인 조각을 걷어낸다."""
    parts=[x.strip() for x in m.split(",")]
    parts=[x for x in parts if x and "#" not in x]
    return ", ".join(parts)

import re
def width(x): return sum(2 if ord(c)>0x1100 and not c.isascii() else 1 for c in x)
def segs(m): return [x.strip() for x in re.split(r"[,;]", m) if x.strip()]
SUF=("시키다","하게 하다","해지다","스럽다","롭다","되다","하다","적인","있는","없는",
     "적으로","하게","하는","한","인","의","는","게","히","적","로")
def norm(x):
    x=re.sub(r"[\s~()\[\]]","",x)
    for _ in range(3):
        for suf in SUF:
            if len(x)>len(suf)+1 and x.endswith(suf): x=x[:-len(suf)]; break
        else: break
    return x
def cover(a,b):
    """a(새 뜻)가 b(원본 뜻)의 의미를 담고 있는가"""
    na={norm(s) for s in segs(a)}; nb={norm(s) for s in segs(b)}
    return bool(na & nb) or any(x in y or y in x for x in na for y in nb if len(x)>=2 and len(y)>=2)

ORIG=p2.get("orig",{})
def keep_sense(k, new):
    """Step3 뜻이 원본의 의미를 놓쳤으면 원본 뜻을 뒤에 덧붙인다."""
    olds=ORIG.get(k) or []
    if not olds: return new
    if any(cover(new,o) for o in olds): return new
    extra=sorted(olds, key=width)[0]
    merged=new+"; "+segs(extra)[0]
    return merged if width(merged)<=30 else new

gloss={}
gloss.update({k:scrub(v) for k,v in p2["B"].items()})   # 병합
gloss.update({k:keep_sense(k,scrub(v)) for k,v in p2["A"].items()})   # Step3 승계 + 원의미 보존
written={}
for cf in sorted(os.listdir(os.path.join(here,"chunks"))):
    n=cf[:3]; df=os.path.join(here,"done",n+".txt")
    if not os.path.exists(df): continue
    src=[l.rstrip("\n").split("\t")[0].lower() for l in open(os.path.join(here,"chunks",cf),encoding="utf-8")]
    new=[l.rstrip("\n").strip() for l in open(df,encoding="utf-8")]
    assert len(src)==len(new), f"{cf}: 줄 수 불일치 {len(src)} vs {len(new)}"
    for w,m in zip(src,new):
        if not m: continue
        assert width(m)<=30, f"{cf}: '{w}' 폭 초과 → {m}"
        written[w]=m
gloss.update(written)          # 직접 쓴 것이 최우선
gloss={k:v for k,v in gloss.items() if v}
json.dump(gloss, open(os.path.join(here,"glossary.json"),"w"), ensure_ascii=False)
print(f"A(Step3 승계) {len(p2['A']):,} · B(원본 병합) {len(p2['B']):,} · C+블록1(직접 작성) {len(written):,}")
print(f"→ glossary {len(gloss):,}개 / Step1+2 고유단어 10,804  (나머지 D는 원본 유지)")
