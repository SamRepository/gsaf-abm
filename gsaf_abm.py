"""
Stylized agent-based model (ABM) of semantic capability adoption in public administration.

Agents  : public agencies. Each holds four readiness dimensions (technical, semantic,
          organizational, legal) in [0, 1] and a capability stage s in
          {0 legacy, 1 SMOS, 2 SICS, 3 SROS, 4 HNSS}.
Rule    : reaching stage k requires the weakest readiness dimension to exceed TAU[k]
          (weakest-link assumption, derived from the review finding that organizational
          and legal interoperability are the binding constraints).
Strategies
  graduated : the agency targets s+1 and launches a project only when its weakest
              readiness is within READY_MARGIN of the entry threshold
  big_bang  : the agency targets stage 4 (HNSS) directly and launches a project every year
              until it succeeds or abandons

All parameters are stylized assumptions, not calibrated on empirical data.
The model illustrates the mechanism of the framework; it does not predict outcomes.
"""
import numpy as np

TAU = np.array([0.0, 0.25, 0.45, 0.65, 0.80])  # entry threshold of stage k (weakest-link readiness)
STEEP = 18.0           # steepness of the logistic success probability around the threshold
LEARN = 0.04           # readiness gain per stage level after a successful transition (learning effect)
SETBACK = 0.06         # max loss of organizational readiness after a failed project (resistance)
ABANDON = 0.08         # probability of abandoning the transformation after a failed project
PARTIAL = 0.03         # technical and semantic readiness gained even from a failed project
READY_MARGIN = 0.05    # graduated agencies launch a project only near the threshold
COST = np.array([0, 1.0, 1.5, 2.0, 2.5])  # relative cost of a project targeting stage k

CONTEXTS = {
    # mean and s.d. of initial readiness, annual capacity-building budget (readiness units/year)
    "mature":   dict(r0=0.65, sd=0.10, budget=0.06),
    "emerging": dict(r0=0.30, sd=0.08, budget=0.04),
}
N_AGENCIES, YEARS = 40, 10

def p_success(minr, k):
    return 1.0 / (1.0 + np.exp(-STEEP * (minr - TAU[k])))

AGG = "min"   # readiness aggregation: "min" (weakest link, default) or "mean" (robustness check)

def ready(r):
    return r.min() if AGG == "min" else r.mean()

def simulate(ctx, strategy, rng, n=N_AGENCIES, years=YEARS):
    c = CONTEXTS[ctx] if isinstance(ctx, str) else ctx
    R = np.clip(rng.normal(c["r0"], c["sd"], size=(n, 4)), 0.02, 0.95)
    R[:, 2:] *= 0.8                     # organizational and legal readiness start lower
    s = np.zeros(n, dtype=int)
    active = np.ones(n, dtype=bool)
    failures = 0
    traj = [0.0]
    for _ in range(years):
        for i in range(n):
            if not active[i] or s[i] == 4:
                continue
            j = np.argmin(R[i])                           # capacity building on the weakest dimension
            R[i, j] = min(1.0, R[i, j] + c["budget"])
            target = s[i] + 1 if strategy == "graduated" else 4
            if strategy == "graduated" and ready(R[i]) < TAU[target] - READY_MARGIN:
                continue                                  # not ready: no project this year
            if rng.random() < p_success(ready(R[i]), target):
                s[i] = target
                R[i] = np.minimum(1.0, R[i] + LEARN * target)
            else:
                failures += 1
                R[i, :2] = np.minimum(1.0, R[i, :2] + PARTIAL)   # partial technical/semantic learning
                R[i, 2] = max(0.0, R[i, 2] - SETBACK * COST[target] / COST[-1])
                if rng.random() < ABANDON:
                    active[i] = False
        traj.append(s.mean())
    return dict(mean_stage=s.mean(), share_s2=(s >= 2).mean(), share_s4=(s == 4).mean(),
                failures_per_agency=failures / n, abandoned=(~active).mean(),
                traj=np.array(traj))

def monte_carlo(runs=1000, seed=2026):
    rng = np.random.default_rng(seed)
    out = {}
    for ctx in CONTEXTS:
        for st in ("graduated", "big_bang"):
            res = [simulate(ctx, st, rng) for _ in range(runs)]
            out[(ctx, st)] = {k: (np.mean([r[k] for r in res], axis=0), np.std([r[k] for r in res], axis=0))
                              for k in res[0]}
    return out

def sensitivity(runs=500, seed=11, budgets=(0.02, 0.04, 0.06, 0.08, 0.10)):
    """mean stage after YEARS years versus the annual budget, emerging context"""
    rng = np.random.default_rng(seed)
    rows = []
    for b in budgets:
        c = dict(CONTEXTS["emerging"], budget=b)
        g = np.mean([simulate(c, "graduated", rng)["mean_stage"] for _ in range(runs)])
        bb = np.mean([simulate(c, "big_bang", rng)["mean_stage"] for _ in range(runs)])
        rows.append((b, g, bb))
    return rows

if __name__ == "__main__":
    mc = monte_carlo()
    for k, v in mc.items():
        print(k, {m: f"{a:.2f}±{s:.2f}" for m, (a, s) in v.items() if m != "traj"})
    import gsaf_abm as G
    G.AGG = "mean"
    mc2 = G.monte_carlo(runs=500)
    for k, v in mc2.items():
        print("MEAN-RULE", k, {m: f"{a:.2f}±{s:.2f}" for m, (a, s) in v.items() if m != "traj"})
    G.AGG = "min"
    for row in sensitivity():
        print("budget %.2f  graduated %.2f  big_bang %.2f" % row)
