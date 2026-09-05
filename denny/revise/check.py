import sys, os, re
def width(s): return sum(2 if ord(c)>0x1100 and not c.isascii() else 1 for c in s)
def segs(m):
    return {x for x in re.split(r"[,;/·]", re.sub(r"\([^)]*\)","",m).replace("~","").replace(" ","")) if x}
bad=0; rows=0; over=[]; empt=[]; nolink=[]; short=[]
for cf in sorted(os.listdir("chunks")):
    n=cf[:3]; df=f"done/{n}.txt"
    if not os.path.exists(df): continue
    src=[l.rstrip("\n").split("\t") for l in open("chunks/"+cf,encoding="utf-8")]
    new=[l.rstrip("\n") for l in open(df,encoding="utf-8")]
    if len(src)!=len(new):
        print(f"[{n}] 줄 수 불일치 {len(src)} vs {len(new)}"); bad+=1; continue
    for (w,old),nm in zip(src,new):
        rows+=1
        if not nm.strip(): empt.append((n,w))
        elif width(nm)>30: over.append((n,w,nm,width(nm)))
        elif width(nm)<=width(old.split(" / ")[0]) and width(nm)<10: short.append((n,w,old,nm))
        else:
            o=set()
            for part in old.split(" / "): o|=segs(part)
            if o and not (o & segs(nm)) and not any(x in nm for x in o):
                nolink.append((n,w,old,nm))
print(f"검사 {rows:,}줄")
print(f"  빈 줄            : {len(empt)}")
print(f"  폭 30 초과       : {len(over)}")
print(f"  기존보다 짧아짐  : {len(short)}")
print(f"  기존 뜻과 안 겹침: {len(nolink)}  (뜻이 바뀌었을 수 있어 확인 필요)")
for x in over[:10]: print("   [폭초과]", x)
for x in empt[:10]: print("   [빈줄]", x)
for x in short[:10]: print("   [짧음]", x)
for x in nolink[:25]: print("   [확인]", x[1], "|", x[2], "→", x[3])
sys.exit(1 if (over or empt) else 0)
