import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

INPUT_FILE = 'data.csv'
OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

df = pd.read_csv(INPUT_FILE, sep=';')

df = df[df['Algorithm'] != 'Skipped']

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

sizes = df['MatrixSize'].unique()

fig, axes = plt.subplots(1, len(sizes), figsize=(18, 5))
if len(sizes) == 1: axes = [axes]

for i, size in enumerate(sizes):
    subset = df[df['MatrixSize'] == size]
    
    ax = axes[i]
    sns.lineplot(data=subset, x='Processes', y='Time', hue='Algorithm', marker='o', ax=ax)
    
    ax.set_title(f'Matrix Size {size}x{size}')
    ax.set_xlabel('Processes')
    ax.set_ylabel('Time (sec)')
    ax.set_xticks(subset['Processes'].unique())
    ax.grid(True, which="both", ls="--")

plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/comparison_time.png')
plt.close()

t1_table = df[df['Processes'] == 1].set_index(['Algorithm', 'MatrixSize'])['Time'].to_dict()

def get_speedup(row):
    t1 = t1_table.get((row['Algorithm'], row['MatrixSize']))
    if t1: return t1 / row['Time']
    return 0

df['Speedup'] = df.apply(get_speedup, axis=1)

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Processes', y='Speedup', hue='Algorithm', style='MatrixSize', markers=True, dashes=False)

max_p = df['Processes'].max()
plt.plot([1, max_p], [1, max_p], 'k--', label='Ideal', alpha=0.5)

plt.title('Speedup')
plt.legend()
plt.grid(True)
plt.xticks(df['Processes'].unique())
plt.savefig(f'{OUTPUT_FOLDER}/comparison_speedup.png')
plt.close()

df['GFLOPS'] = (2 * df['MatrixSize']**3) / df['Time'] / 1e9

plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='Processes', y='GFLOPS', hue='Algorithm')

plt.title('Performance (GFLOPS)')
plt.ylabel('GFLOPS')
plt.grid(True, axis='y')
plt.savefig(f'{OUTPUT_FOLDER}/comparison_gflops.png')
plt.close()
