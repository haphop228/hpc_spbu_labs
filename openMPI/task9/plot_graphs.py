import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print(f"Created folder: {OUTPUT_FOLDER}")

# Read data files
try:
    df_fixed = pd.read_csv('data.csv', sep=';')
    df_fixed['Config'] = '2 Nodes (Fixed)'
except Exception as e:
    print(f"Error reading data.csv: {e}")
    print("Run 'sbatch job.sh' first")
    exit(1)

try:
    df_auto = pd.read_csv('data_auto.csv', sep=';')
    df_auto['Config'] = 'Auto (Scheduler)'
    has_auto = True
except Exception as e:
    print(f"Warning: data_auto.csv not found: {e}")
    print("Run 'sbatch job_auto.sh' for comparison")
    has_auto = False

# Combine data
if has_auto:
    df_all = pd.concat([df_fixed, df_auto], ignore_index=True)
else:
    df_all = df_fixed

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 11})

operations = df_all['Operation'].unique()
process_counts = sorted(df_all['Processes'].unique())

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for idx, op in enumerate(operations):
    ax = axes[idx]
    df_op = df_all[df_all['Operation'] == op]
    
    for config in df_op['Config'].unique():
        df_subset = df_op[df_op['Config'] == config]
        ax.plot(df_subset['DataSize'], df_subset['CustomTime'], 
               marker='o', linestyle='--', label=f'Custom ({config})', alpha=0.7)
        ax.plot(df_subset['DataSize'], df_subset['MPITime'], 
               marker='s', linestyle='-', label=f'MPI ({config})')
    
    ax.set_title(f'{op}', fontsize=12, fontweight='bold')
    ax.set_xlabel('Data Size (integers)')
    ax.set_ylabel('Time (seconds)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.3)
    ax.legend(fontsize=8)

plt.suptitle('Сравнение времени выполнения: Custom vs MPI Native', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/time_comparison_all_ops.png', dpi=150)
plt.close()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for idx, op in enumerate(operations):
    ax = axes[idx]
    df_op = df_all[df_all['Operation'] == op]
    
    for config in df_op['Config'].unique():
        df_subset = df_op[df_op['Config'] == config]
        ax.plot(df_subset['DataSize'], df_subset['Speedup'], 
               marker='o', label=config, linewidth=2)
    
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Equal performance')
    ax.set_title(f'{op}', fontsize=12, fontweight='bold')
    ax.set_xlabel('Data Size (integers)')
    ax.set_ylabel('Speedup (Custom/MPI)')
    ax.set_xscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.3)
    ax.legend(fontsize=8)

plt.suptitle('Speedup Analysis: Custom Time / MPI Time\n(<1 = MPI faster, >1 = Custom faster)', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/speedup_all_ops.png', dpi=150)
plt.close()

plt.figure(figsize=(14, 7))
avg_speedup = df_all.groupby(['Operation', 'Config'])['Speedup'].mean().reset_index()

configs = df_all['Config'].unique()
x = range(len(operations))
width = 0.35 if len(configs) == 1 else 0.35

for i, config in enumerate(configs):
    subset = avg_speedup[avg_speedup['Config'] == config]
    offset = (i - len(configs)/2 + 0.5) * width
    plt.bar([pos + offset for pos in x], subset['Speedup'], width, 
           label=config, alpha=0.8)

plt.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Equal performance')
plt.xlabel('Operation', fontsize=12)
plt.ylabel('Average Speedup (Custom / MPI)', fontsize=12)
plt.title('Average Speedup by Operation\n(<1 = MPI faster, >1 = Custom faster)', 
         fontsize=14, fontweight='bold')
plt.xticks(x, operations, rotation=0)
plt.legend()
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/average_speedup.png', dpi=150)
plt.close()

if has_auto:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    for op in operations:
        df_op = df_all[df_all['Operation'] == op]
        for config in df_op['Config'].unique():
            df_subset = df_op[df_op['Config'] == config]
            avg_time = df_subset.groupby('Operation')['MPITime'].mean().values[0]
            ax.bar(f'{op}\n{config}', avg_time, alpha=0.7)
    
    ax.set_ylabel('Average MPI Time (seconds)', fontsize=12)
    ax.set_title('MPI Performance: Fixed vs Auto Placement', fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', alpha=0.3)

    ax = axes[1]
    for config in configs:
        subset = avg_speedup[avg_speedup['Config'] == config]
        ax.plot(operations, subset['Speedup'], marker='o', label=config, linewidth=2)
    
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Operation', fontsize=12)
    ax.set_ylabel('Average Speedup', fontsize=12)
    ax.set_title('Speedup Comparison: Fixed vs Auto', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/config_comparison.png', dpi=150)
    plt.close()
