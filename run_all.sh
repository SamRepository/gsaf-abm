#!/usr/bin/env bash
# Reproduces all results and figures reported in the paper (about 3 minutes on a laptop).
set -e
mkdir -p results figures
python3 make_fig2.py            # Monte Carlo (1,000 runs), Table 4, Fig. 2, results/sim_results.json
python3 sensitivity_oat.py      # one-at-a-time sensitivity, results/sens2.json
python3 sensitivity_global.py   # Latin hypercube global sensitivity, results/gsa.json
python3 make_fig1.py            # Fig. 1, reference architecture
