"""Fig. 2 (simulation results) and results/sim_results.json."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import gsaf_abm as G, json
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'font.size':8})
# ---------- Fig 2 simulation
mc=G.monte_carlo(runs=1000)
sens=G.sensitivity()
fig,ax=plt.subplots(1,2,figsize=(4.8,2.15),dpi=300)
yrs=np.arange(G.YEARS+1)
sty={('mature','graduated'):('k','-','Mature, graduated'),('mature','big_bang'):('k','--','Mature, big-bang'),
     ('emerging','graduated'):('0.45','-','Emerging, graduated'),('emerging','big_bang'):('0.45','--','Emerging, big-bang')}
for k,(c,ls,lab) in sty.items():
    m,sd=mc[k]['traj']; ax[0].plot(yrs,m,color=c,ls=ls,lw=1.1,label=lab); ax[0].fill_between(yrs,m-sd,m+sd,color=c,alpha=0.12,lw=0)
ax[0].set_xlabel('Year'); ax[0].set_xticks([0,2,4,6,8,10]); ax[0].set_ylabel('Mean capability stage'); ax[0].set_ylim(0,4.1)
ax[0].set_yticks([0,1,2,3,4]); ax[0].set_yticklabels(['0','1 SMOS','2 SICS','3 SROS','4 HNSS'],fontsize=6.5)
ax[0].set_title('(a) Adoption trajectories',fontsize=7.5)
b=[r[0] for r in sens]; ax[1].plot(b,[r[1] for r in sens],'k-o',ms=3,lw=1.1,label='Graduated'); ax[1].plot(b,[r[2] for r in sens],'k--s',ms=3,lw=1.1,label='Big-bang')
ax[1].set_xlabel('Annual capacity budget'); ax[1].set_ylabel('Mean stage, year 10'); ax[1].set_ylim(0,2.5)
ax[1].legend(fontsize=6,frameon=False); ax[1].set_title('(b) Emerging context: budget',fontsize=7.5)
for a in ax:
    a.spines['top'].set_visible(False); a.spines['right'].set_visible(False)
h,l=ax[0].get_legend_handles_labels(); fig.legend(h,l,loc='lower center',ncol=4,fontsize=6,frameon=False,bbox_to_anchor=(0.5,0.0)); fig.tight_layout(pad=0.4,rect=(0,0.09,1,1)); fig.savefig('figures/fig2_simulation.png',dpi=300)
G.AGG='mean'; mc2=G.monte_carlo(runs=500); G.AGG='min'
res={'mc':{f'{k[0]}|{k[1]}':{m:[float(np.round(np.mean(a),3)) if m!='traj' else None, float(np.round(np.mean(s),3)) if m!='traj' else None] for m,(a,s) in v.items()} for k,v in mc.items()},
     'mean_rule':{f'{k[0]}|{k[1]}':{m:[float(np.round(a,3)),float(np.round(s,3))] for m,(a,s) in v.items() if m!='traj'} for k,v in mc2.items()},
     'sens':[[float(x) for x in r] for r in sens]}
json.dump(res,open('results/sim_results.json','w'),indent=1)
