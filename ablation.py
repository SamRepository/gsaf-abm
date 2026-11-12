"""Ablation requested by reviewers: gated big-bang, stage-skipping, no learning gain.
Reuses gsaf_abm parameters; same draw order as G.simulate so baselines match exactly.
Each strategy starts from the same seed (common random numbers).
Every metric is reported as the mean over runs plus the half-width of its 95% confidence
interval (key suffix "_ci95").
Note: big_bang and big_bang_gated give identical results with and without the learning
gain (LEARN), by design: they only ever target Stage 4, and an agency stops once it
reaches Stage 4, so the gain is never applied."""
import numpy as np, json, gsaf_abm as G

def plan(strategy, s):
    if strategy == "graduated":      return s + 1, True
    if strategy == "big_bang":       return 4, False
    if strategy == "big_bang_gated": return 4, True
    if strategy == "skip_to_S3":     return (3 if s < 3 else 4), True   # gated, jumps S0 -> S3 -> S4
    raise ValueError(strategy)

def simulate2(ctx, strategy, rng, n=G.N_AGENCIES, years=G.YEARS):
    c = G.CONTEXTS[ctx]
    R = np.clip(rng.normal(c["r0"], c["sd"], size=(n, 4)), 0.02, 0.95)
    R[:, 2:] *= 0.8
    s = np.zeros(n, dtype=int); active = np.ones(n, dtype=bool); failures = 0
    for _ in range(years):
        for i in range(n):
            if not active[i] or s[i] == 4: continue
            j = np.argmin(R[i]); R[i, j] = min(1.0, R[i, j] + c["budget"])
            target, gated = plan(strategy, s[i])
            if gated and G.ready(R[i]) < G.TAU[target] - G.READY_MARGIN: continue
            if rng.random() < G.p_success(G.ready(R[i]), target):
                s[i] = target; R[i] = np.minimum(1.0, R[i] + G.LEARN * target)
            else:
                failures += 1
                R[i, :2] = np.minimum(1.0, R[i, :2] + G.PARTIAL)
                R[i, 2] = max(0.0, R[i, 2] - G.SETBACK * G.COST[target] / G.COST[-1])
                if rng.random() < G.ABANDON: active[i] = False
    return dict(mean_stage=s.mean(), share_s4=(s == 4).mean(), failures=failures / n, abandoned=(~active).mean())

def run(runs=1000, seed=2026):
    out = {}
    for ctx in ("mature", "emerging"):
        for st in ("graduated", "big_bang", "big_bang_gated", "skip_to_S3"):
            rng = np.random.default_rng(seed)
            res = [simulate2(ctx, st, rng) for _ in range(runs)]
            cell = {}
            for k in res[0]:
                x = np.array([r[k] for r in res], dtype=float)
                cell[k] = round(float(x.mean()), 2)
                cell[k + "_ci95"] = round(float(1.96 * x.std(ddof=1) / np.sqrt(runs)), 3)
            out[f"{ctx}|{st}"] = cell
    return out

if __name__ == "__main__":
    # sanity: baselines must equal G.simulate with the same seed
    rng = np.random.default_rng(5); a = G.simulate("mature", "graduated", rng)["mean_stage"]
    rng = np.random.default_rng(5); b = simulate2("mature", "graduated", rng)["mean_stage"]
    rng = np.random.default_rng(5); c = G.simulate("emerging", "big_bang", rng)["failures_per_agency"]
    rng = np.random.default_rng(5); d = simulate2("emerging", "big_bang", rng)["failures"]
    print("check graduated:", a == b, "| check big_bang failures:", c == d)
    res = {"baseline_learning": run()}
    G.LEARN = 0.0
    res["no_learning"] = run()
    json.dump(res, open("results/ablation.json", "w", newline="\n"), indent=1)
    for k, v in res.items():
        print("==", k)
        for kk, vv in v.items(): print(f"{kk:28s}", vv)
