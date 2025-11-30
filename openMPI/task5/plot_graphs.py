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
except Exception as e:
    print(f"Error: {e}")
    exit()

t1_values = df[df['Procs'] == 1].set_index('Label')['Time'].to_dict()

def calc_speedup(row):
    t1 = t1_values.get(row['Label'])
    if t1:
        return t1 / row['Time']
    return 0

df['Speedup'] = df.apply(calc_speedup, axis=1)

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Procs', y='Time', hue='Label', marker='o')

plt.title('Время выполнения: Вычисления vs Сеть')
plt.xlabel('Количество процессов')
plt.ylabel('Время (сек) - Log Scale')
plt.yscale('log')
plt.grid(True, which="both", ls="--")
plt.savefig(f'{OUTPUT_FOLDER}/comparison_time.png')
plt.close()

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Procs', y='Speedup', hue='Label', marker='o')

max_p = df['Procs'].max()
plt.plot([1, max_p], [1, max_p], 'k--', label='Ideal', alpha=0.5)

plt.title('Ускорение (Speedup)')
plt.xlabel('Количество процессов')
plt.ylabel('Ускорение (раз)')
plt.legend()
plt.grid(True)
plt.xticks(df['Procs'].unique())
plt.savefig(f'{OUTPUT_FOLDER}/comparison_speedup.png')
plt.close()

print(f"Graphs saved to {OUTPUT_FOLDER}/")