import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

try:
    df_fixed = pd.read_csv('data.csv', sep=';')
    df_fixed['Config'] = '2 Nodes (Fixed)'
except Exception as e:
    print(f"Error reading data.csv: {e}")
    exit(1)

try:
    df_auto = pd.read_csv('data_auto.csv', sep=';')
    df_auto['Config'] = 'Auto (Scheduler)'
    has_auto = True
except Exception as e:
    print(f"Warning: data_auto.csv not found")
    has_auto = False

if has_auto:
    df_all = pd.concat([df_fixed, df_auto], ignore_index=True)
else:
    df_all = df_fixed

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 11})

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

data_sizes = sorted(df_all['DataSize'].unique())

for idx, ds in enumerate(data_sizes):
    ax = axes[idx]
    df_ds = df_all[df_all['DataSize'] == ds]
    
    for config in df_ds['Config'].unique():
        df_subset = df_ds[df_ds['Config'] == config]
        avg_blocking = df_subset.groupby('Processes')['BlockingTime'].mean()
        avg_nonblocking = df_subset.groupby('Processes')['NonBlockingTime'].mean()
        
        ax.plot(avg_blocking.index, avg_blocking.values, 
               marker='o', linestyle='--', label=f'Blocking ({config})', alpha=0.7)
        ax.plot(avg_nonblocking.index, avg_nonblocking.values, 
               marker='s', linestyle='-', label=f'Non-Blocking ({config})')
    
    ax.set_title(f'Data Size: {ds} bytes', fontsize=12, fontweight='bold')
    ax.set_xlabel('Number of Processes')
    ax.set_ylabel('Average Execution Time (seconds)')
    ax.set_yscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.3)
    ax.legend(fontsize=8)

plt.suptitle('Blocking vs Non-Blocking: Time Comparison', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/time_comparison.png', dpi=150)
plt.close()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for idx, ds in enumerate(data_sizes):
    ax = axes[idx]
    df_ds = df_all[df_all['DataSize'] == ds]
    
    for config in df_ds['Config'].unique():
        df_subset = df_ds[df_ds['Config'] == config]
        avg_speedup = df_subset.groupby('Processes')['Speedup'].mean()
        ax.plot(avg_speedup.index, avg_speedup.values, 
               marker='o', label=config, linewidth=2)
    
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='No improvement')
    ax.set_title(f'Data Size: {ds} bytes', fontsize=12, fontweight='bold')
    ax.set_xlabel('Number of Processes')
    ax.set_ylabel('Average Speedup (Blocking/Non-Blocking)')
    ax.grid(True, which="both", ls="--", alpha=0.3)
    ax.legend(fontsize=8)

plt.suptitle('Speedup Analysis: Non-Blocking vs Blocking\n(>1 = Non-Blocking faster)', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/speedup_analysis.png', dpi=150)
plt.close()

if has_auto:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    ax = axes[0]
    for config in df_all['Config'].unique():
        df_subset = df_all[df_all['Config'] == config]
        avg_speedup = df_subset.groupby('DataSize')['Speedup'].mean()
        ax.plot(avg_speedup.index, avg_speedup.values, marker='o', label=config, linewidth=2)
    
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Data Size (bytes)', fontsize=12)
    ax.set_ylabel('Average Speedup', fontsize=12)
    ax.set_title('Average Speedup by Data Size', fontsize=12, fontweight='bold')
    ax.set_xscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    for config in df_all['Config'].unique():
        df_subset = df_all[df_all['Config'] == config]
        avg_speedup = df_subset.groupby('Processes')['Speedup'].mean()
        ax.plot(avg_speedup.index, avg_speedup.values, marker='o', label=config, linewidth=2)
    
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Number of Processes', fontsize=12)
    ax.set_ylabel('Average Speedup', fontsize=12)
    ax.set_title('Average Speedup by Process Count', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/config_comparison.png', dpi=150)
    plt.close()

try:
    df_task5 = pd.read_csv('../task5/data.csv', sep=';')
    
    scenarios_map = {
        'ComputeBound': (10000, 1024),
        'NetworkBound': (10, 4194304),
        'Balanced': (1000, 102400)
    }
    
    comparison_data = []
    for scenario, (compute, data_size) in scenarios_map.items():
        task5_data = df_task5[df_task5['Label'] == scenario]
        
        for procs in task5_data['Procs'].unique():
            t5 = task5_data[task5_data['Procs'] == procs]['Time'].values
            if len(t5) == 0:
                continue
            
            task7_match = df_fixed[
                (df_fixed['ComputeUS'] == compute) & 
                (df_fixed['DataSize'] == data_size) &
                (df_fixed['Processes'] == procs)
            ]
            
            if not task7_match.empty:
                t7_blocking = task7_match['BlockingTime'].values[0]
                t7_nonblocking = task7_match['NonBlockingTime'].values[0]
                
                comparison_data.append({
                    'Scenario': scenario,
                    'Processes': procs,
                    'Task5_Time': t5[0],
                    'Task7_Blocking': t7_blocking,
                    'Task7_NonBlocking': t7_nonblocking,
                    'Improvement_vs_Task5': (t5[0] - t7_nonblocking) / t5[0] * 100
                })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        ax = axes[0]
        scenarios = df_comparison['Scenario'].unique()
        x = range(len(scenarios))
        width = 0.25
        
        for i, method in enumerate(['Task5_Time', 'Task7_Blocking', 'Task7_NonBlocking']):
            avg_times = [df_comparison[df_comparison['Scenario'] == s][method].mean() 
                        for s in scenarios]
            offset = (i - 1) * width
            ax.bar([pos + offset for pos in x], avg_times, width, 
                  label=method.replace('_', ' '), alpha=0.8)
        
        ax.set_xlabel('Scenario', fontsize=12)
        ax.set_ylabel('Average Time (seconds)', fontsize=12)
        ax.set_title('Comparison: Task 5 vs Task 7', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios)
        ax.legend()
        ax.grid(True, axis='y', alpha=0.3)
        
        ax = axes[1]
        for scenario in scenarios:
            df_scen = df_comparison[df_comparison['Scenario'] == scenario]
            ax.plot(df_scen['Processes'], df_scen['Improvement_vs_Task5'], 
                   marker='o', label=scenario, linewidth=2)
        
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_xlabel('Number of Processes', fontsize=12)
        ax.set_ylabel('Improvement vs Task 5 (%)', fontsize=12)
        ax.set_title('Non-Blocking Improvement over Task 5', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_FOLDER}/task5_comparison.png', dpi=150)
        plt.close()
        
except Exception as e:
    print(f"Note: Could not compare with task5: {e}")
