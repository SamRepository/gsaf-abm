# GSAF agent-based model

Code and results for the paper:

> A. Haioun, S. Sellami. *Modeling the Graduated Adoption of Semantic and Neuro-Symbolic Interoperability in Public Administration: A Capability Framework and Agent-Based Simulation.* Submitted to the 2nd International Conference on Modeling, Simulation and Computer Technology (ICMSCT'26), 2026.

The model compares two strategies for adopting semantic and Neuro-Symbolic capabilities in public administration, using the four stages of the Graduated Semantic Adoption Framework (GSAF):

| Stage | Capability |
|---|---|
| S1 SMOS | Semantic modeling |
| S2 SICS | Cross-agency integration |
| S3 SROS | Reasoning and validation |
| S4 HNSS | Hybrid Neuro-Symbolic services |

- **Graduated strategy:** each agency moves one stage at a time, and only when its weakest readiness dimension is close to the entry threshold.
- **Big-bang strategy:** each agency targets S4 directly.

## Model summary (ODD elements)

- **Entities:** 40 agencies, each with four readiness dimensions (technical, semantic, organizational, legal) in [0, 1] and a capability stage from 0 (legacy) to 4.
- **Scales:** yearly time steps over 10 years. There are two contexts: mature and emerging.
- **Process:** each year, an agency invests its budget in its weakest dimension and may launch a project toward a target stage k. The project succeeds with probability `P = 1 / (1 + exp(-kappa * (R_min - tau_k)))`, where `R_min` is the minimum of the four dimensions.
  - **If the project succeeds:** the agency moves to stage k and gains readiness through learning.
  - **If it fails:** the agency gains a little technical and semantic readiness, loses some organizational readiness, and abandons with probability alpha.
- **Parameters:** all values are listed in `gsaf_abm.py` and in Table 3 of the paper. **They are stylized assumptions, not calibrated estimates**: the model illustrates a mechanism, it does not forecast outcomes.

## Reproduce

```bash
pip install -r requirements.txt
./run_all.sh
```

All runs use fixed random seeds. The results in `results/` and `figures/` are the ones reported in the paper; `run_all.sh` regenerates them identically. It was tested with Python 3.13, NumPy 2.5 and Matplotlib 3.11.

| File | Content |
|---|---|
| `gsaf_abm.py` | Model, Monte Carlo runs, budget sensitivity |
| `make_fig2.py` | Table 4, Fig. 2, `results/sim_results.json` |
| `sensitivity_oat.py` | One-at-a-time sensitivity, `results/sens2.json` |
| `sensitivity_global.py` | Global sensitivity (300 Latin hypercube samples), `results/gsa.json` |
| `make_fig1.py` | Fig. 1, reference architecture |

## License

MIT. See `LICENSE` and `CITATION.cff`.
