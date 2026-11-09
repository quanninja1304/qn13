def dags(p):
    pairs=list(itertools.combinations(range(p),2));res=[]
    for perm in itertools.product((0,1,2),repeat=len(pairs)):
        A=np.zeros((p,p),int)
        for (i,j),c in zip(pairs,perm):
            if c==1:A[i,j]=1
            if c==2:A[j,i]=1
        # acyclic test via trace of powers
        M=np.eye(p,dtype=int);ok=True
        for _ in range(p):
            M=M@A
            if np.trace(M)>0: ok=False
        if ok: res.append(A)
    return res
def dsep(A,x,y,S):
    # Bayes-ball style: enumerate trails by (node,direction) reachability (differs from moral-graph route used by the author)
    p=len(A);S=set(S)
    anS=set(S);st=list(S)
    while st:
        v=st.pop()
        for u in range(p):
            if A[u,v] and u not in anS: anS.add(u);st.append(u)
    vis=set();st=[(x,'up')]
    while st:
        v,d=st.pop()
        if (v,d) in vis: continue
        vis.add((v,d))
        if v==y and v not in S: return False
        if d=='up' and v not in S:
            for u in range(p):
                if A[u,v]: st.append((u,'up'))
                if A[v,u]: st.append((u,'down'))
        if d=='down':
            if v not in S:
                for u in range(p):
                    if A[v,u]: st.append((u,'down'))
            if v in anS:
                for u in range(p):
                    if A[u,v]: st.append((u,'up'))
    return True
