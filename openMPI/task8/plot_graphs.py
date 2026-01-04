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
    exit(1)

try:
    df_auto = pd.read_csv('data_auto.csv', sep=';')
    df_auto['Config'] = 'Auto (Scheduler)'
    has_auto = True
except Exception as e:
    print(f"Warning: data_auto.csv not found: {e}")
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
plt.title('Зависимость времени передачи от размера сообщения\n(MPI_Sendrecv, 2 ноды фиксированно)')
plt.xlabel('Размер сообщения (Байт)')
plt.ylabel('Время (сек)')
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
plt.title('Пропускная способность сети\n(MPI_Sendrecv, 2 ноды фиксированно)')
plt.xlabel('Размер сообщения (Байт)')
plt.ylabel('Скорость (МБ/сек)')
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
    plt.title('Зависимость времени передачи от размера сообщения\n(MPI_Sendrecv, автоматическое размещение)')
    plt.xlabel('Размер сообщения (Байт)')
    plt.ylabel('Время (сек)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size_auto.png', dpi=150)
    plt.close()

    # Plot 4: Bandwidth vs Size for Auto configuration
    plt.figure(figsize=(12, 6))
    subset_auto = df_auto[df_auto['Bytes'] > 0]
    plt.plot(subset_auto['Bytes'], subset_auto['Bandwidth'], marker='s', color='tab:purple', 
             label='Auto (Scheduler)', linewidth=2)
    plt.title('Пропускная способность сети\n(MPI_Sendrecv, автоматическое размещение)')
    plt.xlabel('Размер сообщения (Байт)')
    plt.ylabel('Скорость (МБ/сек)')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/bandwidth_vs_size_auto.png', dpi=150)
    plt.close()

    # Plot 5: Comparison - Time
    plt.figure(figsize=(14, 7))
    for config in df_all['Config'].unique():
        subset = df_all[df_all['Config'] == config]
        plt.plot(subset['Bytes'], subset['Time'], marker='o', label=config, linewidth=2)
    
    plt.title('Сравнение времени передачи: Fixed vs Auto\n(MPI_Sendrecv)')
    plt.xlabel('Размер сообщения (Байт)')
    plt.ylabel('Время (сек)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_time.png', dpi=150)
    plt.close()

    # Plot 6: Comparison - Bandwidth
    plt.figure(figsize=(14, 7))
    for config in df_all['Config'].unique():
        subset = df_all[(df_all['Config'] == config) & (df_all['Bytes'] > 0)]
        plt.plot(subset['Bytes'], subset['Bandwidth'], marker='s', label=config, linewidth=2)
    
    plt.title('Сравнение пропускной способности: Fixed vs Auto\n(MPI_Sendrecv)')
    plt.xlabel('Размер сообщения (Байт)')
    plt.ylabel('Пропускная способность (МБ/сек)')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_bandwidth.png', dpi=150)
    plt.close()

    # Plot 7: Latency comparison (small messages)
    plt.figure(figsize=(14, 7))
    small_msgs = df_all[df_all['Bytes'] <= 1024]
    for config in small_msgs['Config'].unique():
        subset = small_msgs[small_msgs['Config'] == config]
        plt.plot(subset['Bytes'], subset['Time'] * 1e6, marker='o', label=config, linewidth=2)
    
    plt.title('Латентность для малых сообщений (≤ 1 КБ)\n(MPI_Sendrecv)')
    plt.xlabel('Размер сообщения (Байт)')
    plt.ylabel('Время (микросекунды)')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_latency.png', dpi=150)
    plt.close()

    # Plot 8: Relative performance
    plt.figure(figsize=(14, 7))
    df_pivot = df_all.pivot(index='Bytes', columns='Config', values='Time')
    df_pivot['Speedup'] = df_pivot['Auto (Scheduler)'] / df_pivot['2 Nodes (Fixed)']
    
    plt.plot(df_pivot.index, df_pivot['Speedup'], marker='o', color='tab:red', linewidth=2)
    plt.axhline(y=1.0, color='black', linestyle='--', linewidth=2, label='Equal performance')
    plt.title('Относительная производительность\n(Speedup = Time_Auto / Time_Fixed, >1 = Fixed быстрее)')
    plt.xlabel('Размер сообщения (Байт)')
    plt.ylabel('Speedup')
    plt.xscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/comparison_speedup.png', dpi=150)
    plt.close()
