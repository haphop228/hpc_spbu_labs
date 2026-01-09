import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

df_fixed = pd.read_csv('data.csv', sep=';')
df_fixed['Config'] = '2 Nodes (Fixed)'

try:
    df_auto = pd.read_csv('data_auto.csv', sep=';')
    df_auto['Config'] = 'Auto (Scheduler)'
    has_auto = True
except:
    has_auto = False

if has_auto:
    df_all = pd.concat([df_fixed, df_auto], ignore_index=True)
else:
    df_all = df_fixed

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

plt.figure(figsize=(12, 6))
plt.plot(df_fixed['Bytes'], df_fixed['Time'], marker='o', color='tab:blue', 
         label='2 Nodes (Fixed)', linewidth=2)
plt.title('Time vs message size (MPI_Sendrecv, 2 nodes fixed)')
plt.xlabel('Message size (Bytes)')
plt.ylabel('Time (sec)')
plt.xscale('log')
plt.yscale('log')
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size_fixed.png', dpi=150)
plt.close()

plt.figure(figsize=(12, 6))
subset = df_fixed[df_fixed['Bytes'] > 0]
plt.plot(subset['Bytes'], subset['Bandwidth'], marker='s', color='tab:green', 
         label='2 Nodes (Fixed)', linewidth=2)
plt.title('Bandwidth (MPI_Sendrecv, 2 nodes fixed)')
plt.xlabel('Message size (Bytes)')
plt.ylabel('Bandwidth (MB/sec)')
plt.xscale('log')
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(f'{OUTPUT_FOLDER}/bandwidth_vs_size_fixed.png', dpi=150)
plt.close()

if has_auto:
    plt.figure(figsize=(12, 6))
    plt.plot(df_auto['Bytes'], df_auto['Time'], marker='o', color='tab:orange', 
             label='Auto (Scheduler)', linewidth=2)
    plt.title('Time vs message size (MPI_Sendrecv, auto placement)')
    plt.xlabel('Message size (Bytes)')
    plt.ylabel('Time (sec)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size_auto.png', dpi=150)
    plt.close()

    plt.figure(figsize=(12, 6))
    subset_auto = df_auto[df_auto['Bytes'] > 0]
    plt.plot(subset_auto['Bytes'], subset_auto['Bandwidth'], marker='s', color='tab:purple', 
             label='Auto (Scheduler)', linewidth=2)
    plt.title('Bandwidth (MPI_Sendrecv, auto placement)')
    plt.xlabel('Message size (Bytes)')
    plt.ylabel('Bandwidth (MB/sec)')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/bandwidth_vs_size_auto.png', dpi=150)
    plt.close()

    plt.figure(figsize=(14, 7))
    for config in df_all['Config'].unique():
        subset = df_all[df_all['Config'] == config]
        plt.plot(subset['Bytes'], subset['Time'], marker='o', label=config, linewidth=2)
    
    plt.title('Time comparison: Fixed vs Auto (MPI_Sendrecv)')
    plt.xlabel('Message size (Bytes)')
    plt.ylabel('Time (sec)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_time.png', dpi=150)
    plt.close()

    plt.figure(figsize=(14, 7))
    for config in df_all['Config'].unique():
        subset = df_all[(df_all['Config'] == config) & (df_all['Bytes'] > 0)]
        plt.plot(subset['Bytes'], subset['Bandwidth'], marker='s', label=config, linewidth=2)
    
    plt.title('Bandwidth comparison: Fixed vs Auto (MPI_Sendrecv)')
    plt.xlabel('Message size (Bytes)')
    plt.ylabel('Bandwidth (MB/sec)')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_bandwidth.png', dpi=150)
    plt.close()

    plt.figure(figsize=(14, 7))
    small_msgs = df_all[df_all['Bytes'] <= 1024]
    for config in small_msgs['Config'].unique():
        subset = small_msgs[small_msgs['Config'] == config]
        plt.plot(subset['Bytes'], subset['Time'] * 1e6, marker='o', label=config, linewidth=2)
    
    plt.title('Latency for small messages (MPI_Sendrecv)')
    plt.xlabel('Message size (Bytes)')
    plt.ylabel('Time (microseconds)')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_latency.png', dpi=150)
    plt.close()

    plt.figure(figsize=(14, 7))
    df_pivot = df_all.pivot(index='Bytes', columns='Config', values='Time')
    df_pivot['Speedup'] = df_pivot['Auto (Scheduler)'] / df_pivot['2 Nodes (Fixed)']
    
    plt.plot(df_pivot.index, df_pivot['Speedup'], marker='o', color='tab:red', linewidth=2)
    plt.axhline(y=1.0, color='black', linestyle='--', linewidth=2, label='Equal performance')
    plt.title('Relative performance (Speedup = Time_Auto / Time_Fixed)')
    plt.xlabel('Message size (Bytes)')
    plt.ylabel('Speedup')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_speedup.png', dpi=150)
    plt.close()
