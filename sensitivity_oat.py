import numpy as np, json, gsaf_abm as G
rng=np.random.default_rng(99)
out={}
base=(G.ABANDON,G.TAU.copy(),G.STEEP)
def mean_stage(ctx,st,runs=400):
    return float(np.mean([G.simulate(ctx,st,rng)['mean_stage'] for _ in range(runs)]))
for ab in (0.04,0.16):
    G.ABANDON=ab
    out[f'abandon={ab}']={f'{c}|{s}':round(mean_stage(c,s),2) for c in G.CONTEXTS for s in ('graduated','big_bang')}
G.ABANDON=base[0]
for t4 in (0.70,0.90):
    G.TAU=base[1].copy(); G.TAU[4]=t4
    out[f'tau4={t4}']={f'{c}|{s}':round(mean_stage(c,s),2) for c in G.CONTEXTS for s in ('graduated','big_bang')}
G.TAU=base[1].copy()
for st in (10.0,30.0):
    G.STEEP=st
    out[f'steep={st}']={f'{c}|{s}':round(mean_stage(c,s),2) for c in G.CONTEXTS for s in ('graduated','big_bang')}
G.STEEP=base[2]
json.dump(out,open('results/sens2.json','w'),indent=1); print(json.dumps(out,indent=1))
