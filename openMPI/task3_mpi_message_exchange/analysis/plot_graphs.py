#!/usr/bin/env python3
"""
Построение графиков для анализа производительности MPI обмена сообщениями
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from pathlib import Path
import glob

def format_size(size_bytes):
    """Форматирование размера в человекочитаемый вид"""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes} B"

def plot_time_vs_size(df, output_dir):
    """График зависимости времени от размера сообщения"""
    plt.figure(figsize=(12, 7))
    
    # Логарифмическая шкала для обеих осей
    plt.loglog(df['message_size_bytes'], df['avg_time_ms'], 
               'o-', linewidth=2, markersize=8, label='Average time')
    plt.loglog(df['message_size_bytes'], df['median_time_ms'], 
               's--', linewidth=2, markersize=6, alpha=0.7, label='Median time')
    
    # Заполнение области между min и max
    plt.fill_between(df['message_size_bytes'], 
                     df['min_time_ms'], 
                     df['max_time_ms'], 
                     alpha=0.2, label='Min-Max range')
    
    plt.xlabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    plt.ylabel('Time (ms)', fontsize=12, fontweight='bold')
    plt.title('MPI Message Exchange: Time vs Message Size', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, which='both')
    plt.legend(fontsize=10)
    
    # Добавление аннотаций для ключевых точек
    min_time_idx = df['avg_time_ms'].idxmin()
    max_time_idx = df['avg_time_ms'].idxmax()
    
    plt.annotate(f'Fastest\n{df.loc[min_time_idx, "avg_time_ms"]:.4f} ms',
                xy=(df.loc[min_time_idx, 'message_size_bytes'], 
                    df.loc[min_time_idx, 'avg_time_ms']),
                xytext=(10, 20), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'time_vs_message_size.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_bandwidth_vs_size(df, output_dir):
    """График зависимости пропускной способности от размера сообщения"""
    plt.figure(figsize=(12, 7))
    
    plt.semilogx(df['message_size_bytes'], df['bandwidth_mbps'], 
                 'o-', linewidth=2, markersize=8, color='green')
    
    plt.xlabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    plt.ylabel('Bandwidth (MB/s)', fontsize=12, fontweight='bold')
    plt.title('MPI Message Exchange: Bandwidth vs Message Size', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Добавление горизонтальной линии для пиковой пропускной способности
    peak_bw = df['bandwidth_mbps'].max()
    plt.axhline(y=peak_bw, color='r', linestyle='--', alpha=0.5, 
                label=f'Peak: {peak_bw:.2f} MB/s')
    
    # Аннотация для пиковой пропускной способности
    peak_idx = df['bandwidth_mbps'].idxmax()
    plt.annotate(f'Peak Bandwidth\n{peak_bw:.2f} MB/s\nat {format_size(df.loc[peak_idx, "message_size_bytes"])}',
                xy=(df.loc[peak_idx, 'message_size_bytes'], peak_bw),
                xytext=(20, -30), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.legend(fontsize=10)
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'bandwidth_vs_message_size.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_latency_analysis(df, output_dir):
    """График анализа латентности (для малых сообщений)"""
    # Фильтруем малые сообщения (до 1 MB)
    small_msgs = df[df['message_size_bytes'] <= 1048576].copy()
    
    if small_msgs.empty:
        print("⚠ No small messages for latency analysis")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # График 1: Время vs размер (линейная шкала)
    ax1.plot(small_msgs['message_size_bytes'], small_msgs['avg_time_ms'], 
             'o-', linewidth=2, markersize=8)
    ax1.set_xlabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Latency Analysis: Small Messages', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # График 2: Время на байт
    small_msgs['time_per_byte_us'] = (small_msgs['avg_time_ms'] / small_msgs['message_size_bytes']) * 1000
    ax2.semilogx(small_msgs['message_size_bytes'], small_msgs['time_per_byte_us'], 
                 's-', linewidth=2, markersize=8, color='orange')
    ax2.set_xlabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Time per Byte (µs)', fontsize=12, fontweight='bold')
    ax2.set_title('Time per Byte Analysis', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'latency_analysis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_combined_analysis(df, output_dir):
    """Комбинированный график с двумя осями Y"""
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    color1 = 'tab:blue'
    ax1.set_xlabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Time (ms)', color=color1, fontsize=12, fontweight='bold')
    ax1.loglog(df['message_size_bytes'], df['avg_time_ms'], 
               'o-', color=color1, linewidth=2, markersize=8, label='Time')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3, which='both')
    
    # Вторая ось Y для пропускной способности
    ax2 = ax1.twinx()
    color2 = 'tab:green'
    ax2.set_ylabel('Bandwidth (MB/s)', color=color2, fontsize=12, fontweight='bold')
    ax2.semilogx(df['message_size_bytes'], df['bandwidth_mbps'], 
                 's-', color=color2, linewidth=2, markersize=8, label='Bandwidth')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title('MPI Message Exchange: Time and Bandwidth vs Message Size', 
              fontsize=14, fontweight='bold')
    
    # Объединение легенд
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'combined_time_bandwidth.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_performance_heatmap(df, output_dir):
    """Тепловая карта производительности"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Подготовка данных для тепловой карты
    sizes = df['message_size_bytes'].values
    times = df['avg_time_ms'].values
    bandwidths = df['bandwidth_mbps'].values
    
    # График 1: Время (цветовая шкала)
    scatter1 = ax1.scatter(range(len(sizes)), sizes, c=times, 
                          s=200, cmap='YlOrRd', edgecolors='black', linewidth=1)
    ax1.set_yscale('log')
    ax1.set_xlabel('Test Index', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    ax1.set_title('Time Heatmap', fontsize=13, fontweight='bold')
    plt.colorbar(scatter1, ax=ax1, label='Time (ms)')
    ax1.grid(True, alpha=0.3)
    
    # График 2: Пропускная способность (цветовая шкала)
    scatter2 = ax2.scatter(range(len(sizes)), sizes, c=bandwidths, 
                          s=200, cmap='RdYlGn', edgecolors='black', linewidth=1)
    ax2.set_yscale('log')
    ax2.set_xlabel('Test Index', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Message Size (bytes)', fontsize=12, fontweight='bold')
    ax2.set_title('Bandwidth Heatmap', fontsize=13, fontweight='bold')
    plt.colorbar(scatter2, ax=ax2, label='Bandwidth (MB/s)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'performance_heatmap.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def create_summary_table(df, output_dir):
    """Создание текстовой таблицы с результатами"""
    output_file = os.path.join(output_dir, 'summary_table.txt')
    
    with open(output_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("MPI MESSAGE EXCHANGE BENCHMARK - SUMMARY TABLE\n")
        f.write("=" * 100 + "\n\n")
        
        f.write(f"{'Message Size':<20} {'Avg Time':<15} {'Bandwidth':<15} {'Std Dev':<15} {'Min Time':<15}\n")
        f.write(f"{'':20} {'(ms)':<15} {'(MB/s)':<15} {'(ms)':<15} {'(ms)':<15}\n")
        f.write("-" * 100 + "\n")
        
        for _, row in df.iterrows():
            size_str = format_size(row['message_size_bytes'])
            f.write(f"{size_str:<20} "
                   f"{row['avg_time_ms']:<15.6f} "
                   f"{row['bandwidth_mbps']:<15.2f} "
                   f"{row['std_dev_ms']:<15.6f} "
                   f"{row['min_time_ms']:<15.6f}\n")
        
        f.write("\n" + "=" * 100 + "\n")
        f.write("KEY FINDINGS\n")
        f.write("=" * 100 + "\n\n")
        
        fastest = df.loc[df['avg_time_ms'].idxmin()]
        slowest = df.loc[df['avg_time_ms'].idxmax()]
        best_bw = df.loc[df['bandwidth_mbps'].idxmax()]
        
        f.write(f"Fastest transmission:\n")
        f.write(f"  Size: {format_size(fastest['message_size_bytes'])}\n")
        f.write(f"  Time: {fastest['avg_time_ms']:.6f} ms\n\n")
        
        f.write(f"Slowest transmission:\n")
        f.write(f"  Size: {format_size(slowest['message_size_bytes'])}\n")
        f.write(f"  Time: {slowest['avg_time_ms']:.6f} ms\n\n")
        
        f.write(f"Best bandwidth:\n")
        f.write(f"  Size: {format_size(best_bw['message_size_bytes'])}\n")
        f.write(f"  Bandwidth: {best_bw['bandwidth_mbps']:.2f} MB/s\n")
    
    print(f"✓ Saved: {output_file}")

def plot_all_graphs(csv_file):
    """Построение всех графиков"""
    
    # Чтение данных
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Сортировка по размеру сообщения
    df = df.sort_values('message_size_bytes')
    
    # Определение директории для графиков
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'graphs'
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("GENERATING GRAPHS")
    print("=" * 80)
    print()
    
    # Построение графиков
    plot_time_vs_size(df, output_dir)
    plot_bandwidth_vs_size(df, output_dir)
    plot_latency_analysis(df, output_dir)
    plot_combined_analysis(df, output_dir)
    plot_performance_heatmap(df, output_dir)
    create_summary_table(df, output_dir)
    
    print()
    print("=" * 80)
    print("GRAPHS GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print(f"All graphs saved to: {output_dir}")
    print()
    print("Generated files:")
    print("  - time_vs_message_size.png")
    print("  - bandwidth_vs_message_size.png")
    print("  - latency_analysis.png")
    print("  - combined_time_bandwidth.png")
    print("  - performance_heatmap.png")
    print("  - summary_table.txt")
    print()

def main():
    # Поиск последнего файла с результатами
    project_root = Path(__file__).parent.parent
    results_dir = project_root / 'results'
    
    if len(sys.argv) < 2:
        # Попытка найти последний файл
        csv_files = list(results_dir.glob('benchmark_*.csv'))
        csv_files = [f for f in csv_files if not f.name.endswith('_processed.csv')]
        
        if not csv_files:
            print("Error: No benchmark files found in results/")
            print("Usage: python3 plot_graphs.py [benchmark_csv_file]")
            sys.exit(1)
        
        # Сортировка по времени модификации
        csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        csv_file = csv_files[0]
        print(f"Using latest benchmark file: {csv_file}")
        print()
    else:
        csv_file = Path(sys.argv[1])
    
    if not csv_file.exists():
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    plot_all_graphs(str(csv_file))

if __name__ == "__main__":
    main()