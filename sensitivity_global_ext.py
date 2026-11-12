"""Extended global sensitivity analysis and distribution of the 300 samples.

1. 'baseline' re-runs the analysis of sensitivity_global.py (same ranges, same seed) and
   checks that its summary equals results/gsa.json; it also keeps every sample.
2. 'extended' adds initial readiness (both contexts) and the thresholds tau1-tau3 to the
   sampled parameters, as asked by the reviewers. Ranges keep tau1 < tau2 < tau3 < tau4.

Output: results/gsa_ext.json (summaries and per-sample values) and
figures/fig_gsa_distribution.png (distribution of the advantage of graduated adoption).
The structure of the model (logistic success function, failure setback, the 20% lower
organizational and legal start) is not varied.
"""
import json
import numpy as np
import gsaf_abm as G
from sensitivity_global import RANGES, lhs

EXTRA = {'R0_MATURE': (0.55, 0.75), 'R0_EMERGING': (0.20, 0.40),
         'TAU1': (0.15, 0.35), 'TAU2': (0.35, 0.55), 'TAU3': (0.55, 0.70)}
BEHAVIOR = ('STEEP', 'LEARN', 'SETBACK', 'ABANDON', 'PARTIAL', 'READY_MARGIN')


def run(ranges, n=300, runs=40, seed=4242):
    rng = np.random.default_rng(seed)
    U = lhs(n, len(ranges), rng)
    keys = list(ranges)
    base = {k: getattr(G, k) for k in BEHAVIOR}
    tau = G.TAU.copy()
    ctx0 = {c: dict(v) for c, v in G.CONTEXTS.items()}
    samples, out = [], {'mature': [], 'emerging': []}
    try:
        for row in U:
            v = {k: ranges[k][0] + row[i] * (ranges[k][1] - ranges[k][0]) for i, k in enumerate(keys)}
            for k in BEHAVIOR:
                setattr(G, k, v[k])
            G.TAU = tau.copy()
            G.TAU[4] = v['TAU4']
            for j in (1, 2, 3):
                if f'TAU{j}' in v:
                    G.TAU[j] = v[f'TAU{j}']
            G.CONTEXTS['mature']['budget'] = v['B_MATURE']
            G.CONTEXTS['emerging']['budget'] = v['B_EMERGING']
            if 'R0_MATURE' in v:
                G.CONTEXTS['mature']['r0'] = v['R0_MATURE']
                G.CONTEXTS['emerging']['r0'] = v['R0_EMERGING']
            for ctx in ('mature', 'emerging'):
                g = np.mean([G.simulate(ctx, 'graduated', rng)['mean_stage'] for _ in range(runs)])
                b = np.mean([G.simulate(ctx, 'big_bang', rng)['mean_stage'] for _ in range(runs)])
                out[ctx].append((float(g), float(b)))
            samples.append({k: round(float(val), 4) for k, val in v.items()})
    finally:
        for k in BEHAVIOR:
            setattr(G, k, base[k])
        G.TAU = tau
        for c in ctx0:
            G.CONTEXTS[c].update(ctx0[c])
    res = {}
    for ctx, gb in out.items():
        d = np.array([g - b for g, b in gb])
        res[ctx] = dict(share_graduated_better=float((d > 0).mean()), min=float(d.min()),
                        p5=float(np.percentile(d, 5)), median=float(np.median(d)), max=float(d.max()),
                        graduated=[round(g, 4) for g, _ in gb], big_bang=[round(b, 4) for _, b in gb],
                        advantage=[round(float(x), 4) for x in d])
    res['samples'] = samples
    res['ranges'] = ranges
    res['n_samples'] = n
    res['runs_per_cell'] = runs
    return res


def summary(r):
    return {c: {k: r[c][k] for k in ('share_graduated_better', 'min', 'p5', 'median', 'max')}
            for c in ('mature', 'emerging')}


def figure(base, ext, path='figures/fig_gsa_distribution.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'], 'font.size': 8})
    fig, ax = plt.subplots(1, 2, figsize=(4.8, 2.0), dpi=300)
    bins = np.linspace(min(min(base[c]['advantage'] + ext[c]['advantage']) for c in ('mature', 'emerging')),
                       max(max(base[c]['advantage'] + ext[c]['advantage']) for c in ('mature', 'emerging')), 30)
    for a, ctx in zip(ax, ('mature', 'emerging')):
        a.hist(base[ctx]['advantage'], bins=bins, color='0.25', alpha=0.75, label='Baseline GSA (9 parameters)')
        a.hist(ext[ctx]['advantage'], bins=bins, color='0.65', alpha=0.75, label='Extended GSA (+ r0, τ1–τ3)')
        a.axvline(0, color='k', lw=0.8, ls='--')
        a.set_title(f'({"a" if ctx == "mature" else "b"}) {ctx.capitalize()} context', fontsize=7.5)
        a.set_xlabel('Advantage of graduated adoption\n(mean stage, graduated − big-bang)')
        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
    ax[0].set_ylabel('Parameter sets')
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=2, fontsize=6, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(pad=0.4, rect=(0, 0.08, 1, 1))
    fig.savefig(path, dpi=300)


if __name__ == '__main__':
    base = run(dict(RANGES))
    published = json.load(open('results/gsa.json'))
    for c in ('mature', 'emerging'):
        for k in ('share_graduated_better', 'min', 'p5', 'median', 'max'):
            assert abs(base[c][k] - published[c][k]) < 1e-9, (c, k, base[c][k], published[c][k])
    print('baseline reproduces results/gsa.json')
    ext = run({**RANGES, **EXTRA})
    json.dump({'baseline': base, 'extended': ext}, open('results/gsa_ext.json', 'w', newline='\n'), indent=1)
    figure(base, ext)
    print(json.dumps({'baseline': summary(base), 'extended': summary(ext)}, indent=1))
