# -*- coding: utf-8 -*-
"""done/*.txt 를 모아 glossary.json 을 만든다. (단어(소문자) → 개정된 뜻)"""
import json, os, re
def width(s): return sum(2 if ord(c)>0x1100 and not c.isascii() else 1 for c in s)
here=os.path.dirname(os.path.abspath(__file__))
plan=json.load(open(os.path.join(here,"plan.json"),encoding="utf-8"))
gloss=dict(plan["reuse"])            # Step3 개정판에서 승계한 것
done_blocks=[]
for cf in sorted(os.listdir(os.path.join(here,"chunks"))):
    n=cf[:3]; df=os.path.join(here,"done",n+".txt")
    if not os.path.exists(df): continue
    src=[l.rstrip("\n").split("\t")[0] for l in open(os.path.join(here,"chunks",cf),encoding="utf-8")]
    new=[l.rstrip("\n") for l in open(df,encoding="utf-8")]
    assert len(src)==len(new), f"{n}: 줄 수 불일치 {len(src)} vs {len(new)}"
    for w,m in zip(src,new):
        m=m.strip()
        if not m: continue
        assert width(m)<=30, f"{n}: '{w}' 뜻 폭 초과 → {m}"
        gloss[w.lower()]=m
    done_blocks.append(cf)
json.dump(gloss, open(os.path.join(here,"glossary.json"),"w"), ensure_ascii=False)
total=sum(b["n"] for b in plan["blocks"])
did=sum(b["n"] for b,cf in zip(plan["blocks"],sorted(os.listdir(os.path.join(here,"chunks")))) if cf in done_blocks)
print(f"완료 블록 {len(done_blocks)}/{len(plan['blocks'])} · 개정 단어 {did:,}/{total:,} "
      f"(+ Step3 승계 {len(plan['reuse']):,}) → glossary {len(gloss):,}개")
