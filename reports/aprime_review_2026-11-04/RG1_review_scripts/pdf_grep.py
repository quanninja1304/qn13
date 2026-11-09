import sys,re
import pymupdf as fitz
sys.stdout.reconfigure(encoding="utf-8")
path=sys.argv[1]; pats=sys.argv[2:]
d=fitz.open(path)
print(path.split('/')[-1],'pages',len(d))
for i,p in enumerate(d):
    t=p.get_text()
    for pat in pats:
        for m in re.finditer(pat,t):
            s=max(0,m.start()-100); e=min(len(t),m.end()+700)
            print(f'--- p{i+1} [{pat}]\n'+t[s:e].replace('\n',' '))
            break
