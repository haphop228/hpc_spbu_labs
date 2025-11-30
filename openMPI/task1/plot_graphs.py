import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

INPUT_FILE = 'data.csv'
OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print(f"Создана папка: {OUTPUT_FOLDER}")

try:
    df = pd.read_csv(INPUT_FILE, sep=';')
except FileNotFoundError:
    print(f"ОШИБКА: Файл {INPUT_FILE} не найден.")
    exit()
except Exception as e:
    print(f"ОШИБКА при чтении CSV: {e}")
    exit()

required_cols = {'Processes', 'Elements', 'Time'}
if not required_cols.issubset(df.columns):
    print(f"ОШИБКА: В CSV не хватает колонок. Найдены: {list(df.columns)}")
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

plt.title('Время поиска Min/Max от кол-ва процессов')
plt.xlabel('Количество процессов (Processes)')
plt.ylabel('Время (сек) - Log Scale')
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

plt.title('Ускорение (Speedup)')
plt.xlabel('Количество процессов')
plt.ylabel('Ускорение (раз)')
plt.legend()
plt.xticks(df['Processes'].unique())
plt.grid(True)
plt.savefig(f'{OUTPUT_FOLDER}/speedup_vs_procs.png')
plt.close()


plt.figure(figsize=(10, 6))
procs_list = df['Processes'].unique()
# Выбираем ключевые точки для отображения
subset_procs = [p for p in procs_list if p in [1, 4, 16, 32]]

for p in subset_procs:
    subset = df[df['Processes'] == p]
    plt.plot(subset['Elements'], subset['Time'], marker='s', label=f'Procs={p}')

plt.title('Зависимость времени от размера вектора')
plt.xlabel('Количество элементов (N)')
plt.ylabel('Время (сек)')
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size.png')
plt.close()

plt.figure(figsize=(10, 6))
pivot_eff = df.pivot(index="Elements", columns="Processes", values="Efficiency")
sns.heatmap(pivot_eff, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1.1, cbar_kws={'label': 'Efficiency'})
plt.title('Эффективность параллелизации (1.0 = Идеал)')
plt.gca().invert_yaxis()
plt.savefig(f'{OUTPUT_FOLDER}/efficiency_heatmap.png')
plt.close()

plt.figure(figsize=(10, 6))
for i, size in enumerate(sizes):
    if size >= 10000000: 
        subset = df[df['Elements'] == size]
        plt.plot(subset['Processes'], subset['Throughput'], marker='D', label=f'N={size:.0e}', color=colors[i])

plt.title('Скорость обработки данных (Memory Throughput)')
plt.xlabel('Количество процессов')
plt.ylabel('Скорость (Млрд элементов / сек)')
plt.legend()
plt.xticks(df['Processes'].unique())
plt.grid(True)
plt.savefig(f'{OUTPUT_FOLDER}/throughput.png')
plt.close()

print(f"Готово! Графики сохранены в папку '{OUTPUT_FOLDER}/':")
print("- time_vs_procs.png")
print("- speedup_vs_procs.png")
print("- time_vs_size.png")
print("- efficiency_heatmap.png")
print("- throughput.png")