import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

INPUT_FILE = 'data.csv'
OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

try:
    df = pd.read_csv(INPUT_FILE, sep=';')
except:
    print("Error reading CSV")
    exit()

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

plt.figure(figsize=(12, 7))

chart = sns.barplot(data=df, x='MatrixSize', y='Time', hue='Mode', palette='viridis')

plt.title('Сравнение режимов передачи данных MPI (Cannon Algorithm)')
plt.xlabel('Размер матрицы (NxN)')
plt.ylabel('Время выполнения (сек)')
plt.legend(title='MPI Mode')
plt.grid(True, axis='y')

plt.savefig(f'{OUTPUT_FOLDER}/modes_comparison_time.png')
plt.close()

df_rel = df.copy()
base_times = df[df['Mode'] == 'Standard'].set_index('MatrixSize')['Time'].to_dict()

def normalize(row):
    base = base_times.get(row['MatrixSize'])
    if base: return row['Time'] / base
    return 1.0

df_rel['RelativeTime'] = df_rel.apply(normalize, axis=1)

plt.figure(figsize=(12, 7))
sns.barplot(data=df_rel, x='MatrixSize', y='RelativeTime', hue='Mode', palette='viridis')
plt.axhline(1.0, color='red', linestyle='--', label='Standard Baseline')

plt.title('Относительное время (Standard = 1.0)')
plt.xlabel('Размер матрицы')
plt.ylabel('Коэффициент (меньше = лучше)')
plt.legend()
plt.grid(True, axis='y')

plt.savefig(f'{OUTPUT_FOLDER}/modes_relative_perf.png')
plt.close()

print(f"Graphs saved in {OUTPUT_FOLDER}/")