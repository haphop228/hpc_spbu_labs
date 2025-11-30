import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

INPUT_FILE = 'data.csv'
OUTPUT_FOLDER = 'graphs'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print(f"Создана папка: {OUTPUT_FOLDER}")

try:
    df = pd.read_csv(INPUT_FILE, sep=';')
except Exception as e:
    print(f"Ошибка чтения CSV: {e}")
    exit()

sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

plt.figure(figsize=(10, 6))

# Рисуем график
plt.plot(df['Bytes'], df['Time'], marker='o', color='tab:blue', label='Communication Time')

plt.title('Зависимость времени передачи от размера сообщения')
plt.xlabel('Размер сообщения (Байт)')
plt.ylabel('Время (сек)')
plt.xscale('log') # Логарифмическая шкала по X
plt.yscale('log') # Логарифмическая шкала по Y (так как время меняется от мкс до мс)
plt.grid(True, which="both", ls="--")
plt.legend()

plt.savefig(f'{OUTPUT_FOLDER}/time_vs_size.png')
plt.close()

plt.figure(figsize=(10, 6))

subset = df[df['Bytes'] > 0]

plt.plot(subset['Bytes'], subset['Bandwidth'], marker='s', color='tab:green', label='Bandwidth')

plt.title('Пропускная способность сети')
plt.xlabel('Размер сообщения (Байт)')
plt.ylabel('Скорость (МБ/сек)')
plt.xscale('log') 
plt.grid(True, which="both", ls="--")
plt.legend()

plt.savefig(f'{OUTPUT_FOLDER}/bandwidth_vs_size.png')
plt.close()

print(f"Готово! Графики сохранены в '{OUTPUT_FOLDER}/':")
print("- time_vs_size.png")
print("- bandwidth_vs_size.png")