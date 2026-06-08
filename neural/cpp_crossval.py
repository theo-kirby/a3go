import json, subprocess, sys
def run(fix):
    d=json.load(open(fix)); games=d["data"]
    lines=[str(len(games))]
    for g in games:
        mv=g["moves"]; toks=[]
        for m in mv:
            toks.append("p" if m=="pass" else f"{m[0]},{m[1]},{m[2]}")
        lines.append(f"{g['n']} {len(mv)}")
        lines.append(" ".join(toks))
    inp="\n".join(lines)+"\n"
    out=subprocess.run(["cpp/engine","crossval"],input=inp,capture_output=True,text=True)
    res=out.stdout.strip().split("\n")
    mism=0
    for i,(g,line) in enumerate(zip(games,res)):
        bs,ws,bt,wt,neu,diff,win=line.split()
        got=(int(bs),int(ws),int(bt),int(wt),int(neu),int(diff),win)
        exp=(g["blackStones"],g["whiteStones"],g["blackTerritory"],g["whiteTerritory"],g["neutral"],g["diff"],g["winner"])
        if got!=exp:
            mism+=1
            if mism<=3: print(f"  MISMATCH game {i}: got {got} exp {exp}")
    if out.stderr.strip(): print("  stderr:",out.stderr.strip()[:200])
    print(f"{fix}: {len(games)-mism}/{len(games)} match")
    return mism
m=0
for f in ("fixture_3.json","fixture_4.json"): m+=run(f)
print("PASS" if m==0 else "FAIL")
