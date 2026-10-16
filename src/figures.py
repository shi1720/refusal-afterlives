#!/usr/bin/env python3
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'figures'; F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'savefig.bbox':'tight','pdf.fonttype':42})
INK='#142c42'; TEAL='#157b83'; GOLD='#b66a2e'; PALE='#edf3f6'

def save(fig,name):
    fig.savefig(F/(name+'.pdf'))
    fig.savefig(F/(name+'.png'),dpi=220)
    plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,2.5)); ax.set(xlim=(0,10),ylim=(0,3)); ax.axis('off')
nodes=[(.1,1.0,2.4,1.35,'1  Expressed intention\n\nWhat does the chosen\noption say I want?'),
       (3.65,1.0,2.55,1.35,'2  Executable memory\n\nWhich values and\nfuture rules change?'),
       (7.4,1.0,2.45,1.35,'3  Narrative future\n\nDoes pursuit stop,\nor the story continue?')]
for x,y,w,h,t in nodes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.1',facecolor=PALE,edgecolor=INK,lw=.8))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=10,color=INK,linespacing=1.5)
for x,y in [(2.65,3.45),(6.35,7.2)]:
    ax.add_patch(FancyArrowPatch((x,1.65),(y,1.65),arrowstyle='-|>',mutation_scale=13,color=TEAL))
ax.text(5,.35,'These are separate interpretive questions; a refusal can differ across all three.',ha='center',fontsize=9,color=INK)
save(fig,'01_refusal_layers')

fig,ax=plt.subplots(figsize=(7.1,3.8))
matrix=np.ones((3,3));matrix[1,1:]=0
from matplotlib.colors import ListedColormap
ax.imshow(matrix,cmap=ListedColormap([TEAL,PALE]),vmin=0,vmax=1,aspect='auto')
for i in range(3):
    for j in range(3):
        ax.text(j,i,'Pursuit stops' if matrix[i,j]==0 else 'New royal offer',ha='center',va='center',
                color='white' if matrix[i,j]==0 else INK,fontweight='bold',fontsize=10)
ax.set_xticks(range(3),['Thank the monarch','Withhold thanks:\nencourage pursuit','Withhold thanks:\nwant pursuit to stop'])
ax.set_yticks(range(3),['Welcome the horse','Try to refuse\nthe horse','Accept provisionally;\nconsult uncle'])
ax.set_xlabel('Earlier response to the poem',labelpad=10);ax.set_ylabel('Earlier response to the horse',labelpad=10)
ax.set_title('After returning the jewels: earlier acceptance governs recognition',loc='left',pad=17,color=INK,fontweight='bold',fontsize=11)
ax.set_xticks(np.arange(-.5,3,1),minor=True);ax.set_yticks(np.arange(-.5,3,1),minor=True)
ax.grid(which='minor',color='white',linewidth=4);ax.tick_params(which='minor',bottom=False,left=False)
for s in ax.spines.values():s.set_visible(False)
save(fig,'02_history_matrix')

def fair(r,p):return np.minimum(99,np.floor(r+(100-r)*p/100))
r=np.arange(101)
fig,axs=plt.subplots(1,2,figsize=(7.2,3.0),sharex=True)
for ax in axs:
    ax.set(xlim=(0,100),ylim=(-2,75),xlabel='Prior royal relationship score')
    ax.grid(axis='y',alpha=.18)
axs[0].plot(r,fair(r,10)-r,color=GOLD,label='Thank the monarch (+10%)',lw=1.6)
axs[0].plot(r,fair(r,20)-r,color=TEAL,label='Either motive for silence (+20%)',lw=1.8)
axs[0].set(ylabel='Change in relationship score',title='A  Responding to the poem')
axs[1].plot(r,fair(r,30)-r,color=TEAL,label='Decline the night visit (+30%)',lw=1.6)
axs[1].plot(r,fair(r,70)-r,color=GOLD,label='Decline the affair offer (+70%)',lw=1.6)
axs[1].set_title('B  Declining intimacy')
for ax in axs:ax.legend(fontsize=7,frameon=False,loc='upper right');ax.title.set_fontsize(10)
fig.tight_layout(w_pad=1.8)
save(fig,'03_score_updates')

print('Created 3 vector figures and PNG previews.')
