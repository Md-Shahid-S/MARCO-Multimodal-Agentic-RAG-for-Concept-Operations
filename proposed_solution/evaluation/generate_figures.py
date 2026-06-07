import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# Set style for academic paper with high-contrast aesthetic
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.4)

# Create output directory for plots if it doesn't exist
os.makedirs("evaluation/plots", exist_ok=True)

# ==========================================
# DATA INVENTORY (100% Verified Numbers)
# ==========================================

# 1. Base Paper Data (Table 5: Khadem & Movaghar)
base_bm25 = [0.55, 0.68]      # P@5, nDCG@5
base_embed = [0.63, 0.72]     # P@5, nDCG@5
base_rag = [0.82, 0.86]       # P@5, nDCG@5

# 2. MARCO Full System (From user terminal output)
marco_full_k = [0.2916, 0.2896, 0.2896] # nDCG @3, @5, @10
marco_full_p5_ndcg5 = [0.0760, 0.2896]
marco_full_hallucination = 16.0

# 3. Ablation E1 (From user terminal output)
marco_e1_k = [0.2624, 0.2613, 0.2613]   # nDCG @3, @5, @10
marco_e1_p5_ndcg5 = [0.0760, 0.2613]
marco_e1_hallucination = 20.0


# ==========================================
# PLOT 1: Cross-Study Retrieval Comparison
# ==========================================
print("Generating Plot 1: Cross-Study Retrieval Comparison...")
metrics = ['P@5', 'nDCG@5']
x = np.arange(len(metrics))
width = 0.2

fig1, ax1 = plt.subplots(figsize=(10, 6))
rects1 = ax1.bar(x - 1.5*width, base_bm25, width, label='Paper: BM25', color='#cbd5e1', edgecolor='black')
rects2 = ax1.bar(x - 0.5*width, base_embed, width, label='Paper: Embed-only', color='#94a3b8', edgecolor='black')
rects3 = ax1.bar(x + 0.5*width, base_rag, width, label='Paper: Base RAG', color='#475569', edgecolor='black')
rects4 = ax1.bar(x + 1.5*width, marco_full_p5_ndcg5, width, label='Ours: MARCO', color='#0f172a', edgecolor='black')

ax1.set_ylabel('Evaluation Score', fontweight='bold')
ax1.set_title('Figure 1: Cross-Study Retrieval Performance Comparison', fontweight='bold', pad=20)
ax1.set_xticks(x)
ax1.set_xticklabels(metrics, fontweight='bold')
ax1.legend(loc='upper right')

# Add labels
def autolabel(rects, ax):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

for r in [rects1, rects2, rects3, rects4]: autolabel(r, ax1)

plt.tight_layout()
fig1.savefig('evaluation/plots/fig1_comparative_retrieval.png', dpi=300, bbox_inches='tight')
plt.close(fig1)


# ==========================================
# PLOT 2: Ablation Impact (The Critic Agent)
# ==========================================
print("Generating Plot 2: Ablation Impact (Safety vs Accuracy)...")
systems = ['Ablation E1\n(No Critic Agent)', 'Full MARCO\n(Agentic RAG)']
ndcg_scores = [marco_e1_p5_ndcg5[1], marco_full_p5_ndcg5[1]]
hallucinations = [marco_e1_hallucination, marco_full_hallucination]

x_ablation = np.arange(len(systems))
width_ab = 0.35

fig2, ax2a = plt.subplots(figsize=(9, 6))

color1 = '#334155'
ax2a.set_ylabel('nDCG@5 Score', color=color1, fontweight='bold')
bars1 = ax2a.bar(x_ablation - width_ab/2, ndcg_scores, width_ab, color=color1, edgecolor='black', label='nDCG@5 (Ranking Quality)')
ax2a.tick_params(axis='y', labelcolor=color1)
ax2a.set_ylim(0, 0.4)

ax2b = ax2a.twinx()
color2 = '#b91c1c'
ax2b.set_ylabel('Strict Hallucination Rate (%)', color=color2, fontweight='bold')
bars2 = ax2b.bar(x_ablation + width_ab/2, hallucinations, width_ab, color='#fca5a5', edgecolor=color2, label='Hallucination % (Safety)')
ax2b.tick_params(axis='y', labelcolor=color2)
ax2b.set_ylim(0, 30)

def autolabel_ablation(bars, ax, is_percent=False):
    for bar in bars:
        yval = bar.get_height()
        label = f'{yval}%' if is_percent else f'{yval:.4f}'
        ax.text(bar.get_x() + bar.get_width()/2, yval + (0.5 if is_percent else 0.005), 
                label, ha='center', va='bottom', fontweight='bold', color=bar.get_edgecolor())

autolabel_ablation(bars1, ax2a)
autolabel_ablation(bars2, ax2b, True)

ax2a.set_xticks(x_ablation)
ax2a.set_xticklabels(systems, fontweight='bold')
ax2a.set_title('Figure 4: Impact of Agentic Self-Correction', fontweight='bold', pad=20)

lines_1, labels_1 = ax2a.get_legend_handles_labels()
lines_2, labels_2 = ax2b.get_legend_handles_labels()
ax2a.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.tight_layout()
fig2.savefig('evaluation/plots/fig4_ablation_impact.png', dpi=300, bbox_inches='tight')
plt.close(fig2)


# ==========================================
# PLOT 3: Metric Sensitivity Across Depth (K)
# ==========================================
print("Generating Plot 3: Metric Sensitivity Across Depth (K)...")
k_values = [3, 5, 10]

fig3, ax3 = plt.subplots(figsize=(8, 6))

ax3.plot(k_values, marco_e1_k, marker='s', markersize=8, linestyle='--', color='#94a3b8', linewidth=2.5, label='Ablation E1 (No Critic)')
ax3.plot(k_values, marco_full_k, marker='o', markersize=8, linestyle='-', color='#0f172a', linewidth=2.5, label='MARCO Full System')

ax3.set_xlabel('Retrieval Depth (K)', fontweight='bold')
ax3.set_ylabel('nDCG@K Score', fontweight='bold')
ax3.set_title('Figure 3: Retrieval Robustness Across Context Depth', fontweight='bold', pad=20)
ax3.set_xticks(k_values)
ax3.legend(loc='center right')

# Add data point labels to the line chart
for i, txt in enumerate(marco_full_k):
    ax3.annotate(f"{txt:.4f}", (k_values[i], marco_full_k[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')

for i, txt in enumerate(marco_e1_k):
    ax3.annotate(f"{txt:.4f}", (k_values[i], marco_e1_k[i]), textcoords="offset points", xytext=(0,-15), ha='center', color='#475569')

plt.tight_layout()
fig3.savefig('evaluation/plots/fig3_sensitivity_k.png', dpi=300, bbox_inches='tight')
plt.close(fig3)

print("✅ All plots generated successfully and saved to 'evaluation/plots/' directory!")
