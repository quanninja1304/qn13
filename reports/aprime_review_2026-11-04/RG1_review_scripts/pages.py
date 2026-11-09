import sys;sys.path.append("C:/Users/ADMIN/AppData/Roaming/Python/Python314/site-packages")
import sys,re
import pymupdf
sys.stdout.reconfigure(encoding="utf-8")
path=sys.argv[1]
d=pymupdf.open(path)
print('PAGES',len(d))
for spec in sys.argv[2:]:
    pg,pat,ln=spec.split('|')
    if pg=='*':
        for i,p in enumerate(d):
            t=p.get_text()
            for m in re.finditer(pat,t):
                print(f'--- p{i+1}: '+t[max(0,m.start()-60):m.end()+int(ln)].replace('\n',' '))
    else:
        t=d[int(pg)-1].get_text()
        m=re.search(pat,t)
        print(f'--- p{pg}: '+(t[max(0,m.start()-60):m.end()+int(ln)].replace('\n',' ') if m else 'NOMATCH'))
