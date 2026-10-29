"""Fig. 1 (GSAF layered reference architecture)."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':7})
fig,ax=plt.subplots(figsize=(4.8,3.1),dpi=300); ax.set_xlim(0,100); ax.set_ylim(0,66); ax.axis('off')
def rbox(x,y,w,h,fc):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.2,rounding_size=1.0',fc=fc,ec='k',lw=0.6))
layers=[('S4  Neuro-Symbolic services (HNSS)','KG-grounded LLM assistants (RAG); LLM-proposed\nmappings validated by shapes; generated explanations','0.80','0.80'),
        ('S3  Reasoning and validation (SROS)','SHACL / SHACL-SPARQL shapes; OWL 2 RL and\ndecidable rules; compliance reports','0.65','0.86'),
        ('S2  Integration (SICS)','R2RML / OBDA virtual knowledge graph; DCAT-AP\ncatalog; cross-agency SPARQL endpoint','0.45','0.92'),
        ('S1  Semantic modeling (SMOS)','Reused vocabularies (CPSV-AP, Core Vocabularies);\nagency ontologies; persistent URI policy','0.25','0.97')]
y=52
for h,t,tau,fc in layers:
    rbox(1,y,62,12,fc)
    ax.text(3,y+9.3,h,fontsize=6.8,weight='bold',va='center')
    ax.text(3,y+4.0,t,fontsize=5.7,va='center',linespacing=1.25)
    ax.text(65,y+6,'entry\n'+r'$R_{\min}\geq$'+tau,fontsize=5.8,va='center',linespacing=1.2)
    y-=13
rbox(1,2,62,8,'white'); ax.text(32,6,'Legacy sources: relational databases,\ndocuments, registries, APIs',fontsize=5.9,ha='center',va='center',linespacing=1.2)
ax.annotate('',xy=(78,63),xytext=(78,4),arrowprops=dict(arrowstyle='-|>',lw=0.8,color='k'))
rbox(81.5,2,17,62,'0.93')
ax.text(90,33,'Governance and oversight\ndata governance (Decree 25-320)\nsecurity (Decree 25-321)\nprovenance, human review',fontsize=5.4,ha='center',va='center',rotation=90,linespacing=1.35)
fig.savefig('figures/fig1_architecture.png',dpi=300,bbox_inches='tight',pad_inches=0.02)
