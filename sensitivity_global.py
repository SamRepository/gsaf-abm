"""Global sensitivity analysis: Latin hypercube sampling over all behavioral parameters."""
import numpy as np, json, gsaf_abm as G
RANGES = {'STEEP':(8,30),'LEARN':(0.02,0.06),'SETBACK':(0.02,0.10),'ABANDON':(0.02,0.16),
          'PARTIAL':(0.0,0.05),'READY_MARGIN':(0.0,0.10),'TAU4':(0.70,0.90),
          'B_MATURE':(0.04,0.10),'B_EMERGING':(0.02,0.08)}
def lhs(n, k, rng):
    u = (rng.permuted(np.tile(np.arange(n), (k, 1)), axis=1).T + rng.random((n, k))) / n
    return u
def main(n=300, runs=40, seed=4242):
    rng = np.random.default_rng(seed)
    U = lhs(n, len(RANGES), rng)
    keys = list(RANGES)
    base = {k: getattr(G, k) for k in ('STEEP','LEARN','SETBACK','ABANDON','PARTIAL','READY_MARGIN')}
    tau = G.TAU.copy(); bm = G.CONTEXTS['mature']['budget']; be = G.CONTEXTS['emerging']['budget']
    diffs = {'mature': [], 'emerging': []}
    for row in U:
        v = {k: RANGES[k][0] + row[i] * (RANGES[k][1] - RANGES[k][0]) for i, k in enumerate(keys)}
        for k in base: setattr(G, k, v[k])
        G.TAU = tau.copy(); G.TAU[4] = v['TAU4']
        G.CONTEXTS['mature']['budget'] = v['B_MATURE']; G.CONTEXTS['emerging']['budget'] = v['B_EMERGING']
        for ctx in ('mature', 'emerging'):
            g = np.mean([G.simulate(ctx, 'graduated', rng)['mean_stage'] for _ in range(runs)])
            b = np.mean([G.simulate(ctx, 'big_bang', rng)['mean_stage'] for _ in range(runs)])
            diffs[ctx].append(g - b)
    for k in base: setattr(G, k, base[k])
    G.TAU = tau; G.CONTEXTS['mature']['budget'] = bm; G.CONTEXTS['emerging']['budget'] = be
    out = {}
    for ctx, d in diffs.items():
        d = np.array(d)
        out[ctx] = dict(share_graduated_better=float((d > 0).mean()), min=float(d.min()),
                        p5=float(np.percentile(d, 5)), median=float(np.median(d)), max=float(d.max()))
    out['n_samples'] = n; out['runs_per_cell'] = runs; out['ranges'] = RANGES
    json.dump(out, open('results/gsa.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
