import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

INPUT_FILE = 'data.csv'
OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

df = pd.read_csv(INPUT_FILE, sep=';')

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

plt.figure(figsize=(10, 6))

plt.plot(df['Bytes'], df['Time'], marker='o', color='tab:blue', label='Communication Time')

plt.title('Time vs message size')
plt.xlabel('Message size (Bytes)')
plt.ylabel('Time (sec)')
plt.xscale('log')
plt.yscale('log')
plt.grid(True, which="both", ls="--")
plt.legend()

plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size.png')
plt.close()

plt.figure(figsize=(10, 6))

subset = df[df['Bytes'] > 0]

plt.plot(subset['Bytes'], subset['Bandwidth'], marker='s', color='tab:green', label='Bandwidth')

plt.title('Bandwidth')
plt.xlabel('Message size (Bytes)')
plt.ylabel('Bandwidth (MB/sec)')
plt.xscale('log') 
plt.grid(True, which="both", ls="--")
plt.legend()

plt.savefig(f'{OUTPUT_FOLDER}/bandwidth_vs_size.png')
plt.close()
