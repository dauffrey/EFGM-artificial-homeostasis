import csv, json, hashlib
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SEEDS=range(100,112)
METHODS={'task_only':(0.,False),'joint_1':(1.,False),'joint_4':(4.,False),'guarded_1':(1.,True)}

def data(rng,n,corr,scale=1.):
    x=rng.normal(size=(n,2))*scale
    p=rng.integers(0,2,n)
    q=np.where(rng.random(n)<corr,p,1-p)
    return np.column_stack((x,2*p-1,2*q-1)),(x[:,0]*x[:,1]>0).astype(float),p.astype(float)

def sig(x): return 1/(1+np.exp(-np.clip(x,-40,40)))
def forward(w,x):
    h=np.tanh(x@w[0]+w[1]); z=h@w[2]+w[3]
    return h,z

def grad(w,x,y,head):
    h,z=forward(w,x); v=z[:,head]; e=(sig(v)-y)/len(y)
    dz=np.zeros_like(z); dz[:,head]=e
    dh=(dz@w[2].T)*(1-h*h)
    return [x.T@dh,dh.sum(0),h.T@dz,dz.sum(0)]

def gate_loss(w,d):
    x,_,p=d; z=forward(w,x)[1][:,1]
    return np.mean(np.logaddexp(0,z)-p*z)

def metrics(w,d):
    x,y,p=d; z=forward(w,x)[1]; a=z[:,0]>=0; g=z[:,1]>=0; ok=p==1; no=~ok
    return dict(capability=float(np.mean(a[ok]==y[ok])),permitted_correct=float(np.mean(g[ok] & (a[ok]==y[ok]))),eligible_abstain=float(np.mean(~g[ok])),ineligible_answer=float(np.mean(g[no])),gate_brier=float(np.mean((sig(z[:,1])-p)**2)))

def main():
    rows=[]
    for seed in SEEDS:
        r=np.random.default_rng(seed)
        initial=[r.normal(0,.35,(4,12)),np.zeros(12),r.normal(0,.35,(12,2)),np.zeros(2)]
        train=data(r,256,.9); reg=data(r,256,.5)
        test={'id':data(r,2048,.9),'shift':data(r,2048,.1,1.5)}
        x,y,p=train; mask=p==1
        for name,(weight,guard) in METHODS.items():
            w=[v.copy() for v in initial]; extra=0; rejected=0; scaled=0
            for step in range(201):
                if step%10==0:
                    for dist,d in test.items(): rows.append(dict(seed=seed,method=name,step=step,distribution=dist,extra_forwards=extra,rejected=rejected,scaled=scaled,**metrics(w,d)))
                if step==200: break
                gt=grad(w,x[mask],y[mask],0); gg=grad(w,reg[0],reg[2],1)
                direction=[a+weight*b for a,b in zip(gt,gg)]
                eta=.12
                if guard:
                    base=gate_loss(w,reg); extra+=1; accepted=False
                    for k in range(9):
                        candidate=[a-eta*b for a,b in zip(w,direction)]; extra+=1
                        if gate_loss(candidate,reg)<=base+.0001:
                            w=candidate; accepted=True; scaled+=int(k>0); break
                        eta*=.5
                    if not accepted: rejected+=1
                else: w=[a-eta*b for a,b in zip(w,direction)]
    with (ROOT/'trajectories.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    shift=[r for r in rows if r['distribution']=='shift']; keys=['capability','permitted_correct','eligible_abstain','ineligible_answer','gate_brier']
    def mean(method,step):
        subset=[r for r in shift if r['method']==method and r['step']==step]
        return {k:float(np.mean([r[k] for r in subset])) for k in keys}
    endpoints={m:{str(s):mean(m,s) for s in (0,20,200)} for m in METHODS}
    baseline=endpoints['joint_1']; dc=baseline['200']['capability']-baseline['20']['capability']; dv=baseline['200']['ineligible_answer']-baseline['20']['ineligible_answer']
    pairs=[]
    for m in METHODS:
        if m=='guarded_1': continue
        for seed in SEEDS:
            a=next(r for r in shift if r['seed']==seed and r['method']=='guarded_1' and r['step']==200)
            b=min((r for r in shift if r['seed']==seed and r['method']==m),key=lambda r:(abs(r['capability']-a['capability']),-r['step']))
            pairs.append(dict(seed=seed,baseline=m,step=b['step'],accuracy_gap=abs(a['capability']-b['capability']),violation_delta=a['ineligible_answer']-b['ineligible_answer'],utility_delta=a['permitted_correct']-b['permitted_correct']))
    summary=dict(numpy=np.__version__,protocol_sha256=hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=len(rows),endpoints=endpoints,primary=dict(capability_delta=dc,violation_delta=dv,observed=bool(dc>=.10 and dv>=.05)),matched={m:{k:float(np.mean([r[k] for r in pairs if r['baseline']==m])) for k in ('accuracy_gap','violation_delta','utility_delta')} for m in METHODS if m!='guarded_1'},matched_pairs=pairs,guarded_extra_forwards=sum(r['extra_forwards'] for r in shift if r['method']=='guarded_1' and r['step']==200),guarded_rejected=sum(r['rejected'] for r in shift if r['method']=='guarded_1' and r['step']==200),guarded_scaled=sum(r['scaled'] for r in shift if r['method']=='guarded_1' and r['step']==200))
    (ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps({k:v for k,v in summary.items() if k!='matched_pairs'},indent=2))

if __name__=='__main__': main()
