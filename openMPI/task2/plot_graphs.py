import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

INPUT_FILE = 'data1.csv'
OUTPUT_FOLDER = 'graphs1'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

df = pd.read_csv(INPUT_FILE, sep=';')

required_cols = {'Processes', 'Elements', 'Time'}
if not required_cols.issubset(df.columns):
    exit()

t1_map = df[df['Processes'] == 1].set_index('Elements')['Time'].to_dict()
df['T1'] = df['Elements'].map(t1_map)

df['Speedup'] = df['T1'] / df['Time']

df['Efficiency'] = df['Speedup'] / df['Processes']

df['Throughput'] = (df['Elements'] / df['Time']) / 1e9 

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})
sizes = df['Elements'].unique()
colors = sns.color_palette("tab10", len(sizes))

plt.figure(figsize=(10, 6))
for i, size in enumerate(sizes):
    subset = df[df['Elements'] == size]
    plt.plot(subset['Processes'], subset['Time'], marker='o', label=f'N={size:.0e}', color=colors[i])

plt.title('Execution time vs processes')
plt.xlabel('Processes')
plt.ylabel('Time (sec) - Log Scale')
plt.yscale('log')
plt.legend()
plt.xticks(df['Processes'].unique())
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.savefig(f'{OUTPUT_FOLDER}/time_vs_procs.png')
plt.close()

plt.figure(figsize=(10, 6))
for i, size in enumerate(sizes):
    subset = df[df['Elements'] == size]
    plt.plot(subset['Processes'], subset['Speedup'], marker='o', label=f'N={size:.0e}', color=colors[i])

max_proc = df['Processes'].max()
plt.plot([1, max_proc], [1, max_proc], 'k--', label='Ideal Linear', alpha=0.5)

plt.title('Speedup')
plt.xlabel('Processes')
plt.ylabel('Speedup')
plt.legend()
plt.xticks(df['Processes'].unique())
plt.grid(True)
plt.savefig(f'{OUTPUT_FOLDER}/speedup_vs_procs.png')
plt.close()

plt.figure(figsize=(10, 6))
procs_list = df['Processes'].unique()
subset_procs = [p for p in procs_list if p in [1, 4, 16, 32]]

for p in subset_procs:
    subset = df[df['Processes'] == p]
    plt.plot(subset['Elements'], subset['Time'], marker='s', label=f'Processes={p}')

plt.title('Time vs size')
plt.xlabel('Elements')
plt.ylabel('Time (sec)')
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size.png')
plt.close()

plt.figure(figsize=(10, 6))
pivot_eff = df.pivot(index="Elements", columns="Processes", values="Efficiency")
sns.heatmap(pivot_eff, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1.1, cbar_kws={'label': 'Efficiency'})
plt.title('Efficiency')
plt.gca().invert_yaxis()
plt.savefig(f'{OUTPUT_FOLDER}/efficiency_heatmap.png')
plt.close()

plt.figure(figsize=(10, 6))
for i, size in enumerate(sizes):
    if size >= 10000000: 
        subset = df[df['Elements'] == size]
        plt.plot(subset['Processes'], subset['Throughput'], marker='D', label=f'N={size:.0e}', color=colors[i])

plt.title('Throughput')
plt.xlabel('Processes')
plt.ylabel('Throughput (Billion elements/sec)')
plt.legend()
plt.xticks(df['Processes'].unique())
plt.grid(True)
plt.savefig(f'{OUTPUT_FOLDER}/throughput.png')
plt.close()
