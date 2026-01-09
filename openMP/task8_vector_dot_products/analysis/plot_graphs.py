#!/usr/bin/env python3
"""
Генерация графиков для задачи 8: Vector Dot Products with Sections
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import glob

def find_latest_processed_file():
    """Поиск последнего обработанного файла результатов"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(os.path.dirname(script_dir), 'results')
    
    processed_files = glob.glob(os.path.join(results_dir, '*_processed.csv'))
    
    if not processed_files:
        print("Error: No processed CSV files found in results/")
        print("Please run analyze.py first")
        sys.exit(1)
    
    latest_file = max(processed_files, key=os.path.getmtime)
    return latest_file

def load_data(csv_file):
    """Загрузка обработанных данных"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded data from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)

def plot_execution_time(df, output_dir):
    """График времени выполнения vs количество потоков"""
    
    for (num_pairs, vector_size), group in df.groupby(['num_pairs', 'vector_size']):
        plt.figure(figsize=(10, 6))
        
        for method in group['method'].unique():
            method_data = group[group['method'] == method].sort_values('num_threads')
            plt.plot(method_data['num_threads'], method_data['total_time_ms'], 
                    marker='o', label=method.capitalize(), linewidth=2, markersize=8)
        
        plt.xlabel('Number of Threads', fontsize=12)
        plt.ylabel('Execution Time (ms)', fontsize=12)
        plt.title(f'Execution Time vs Threads\n({num_pairs} pairs, vector size {vector_size})', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = f'execution_time_pairs_{num_pairs}_size_{vector_size}.png'
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Created {filename}")

def plot_speedup(df, output_dir):
    """График ускорения vs количество потоков"""
    
    for (num_pairs, vector_size), group in df.groupby(['num_pairs', 'vector_size']):
        plt.figure(figsize=(10, 6))
        
        # Идеальное ускорение
        max_threads = group['num_threads'].max()
        ideal_threads = np.arange(1, max_threads + 1)
        plt.plot(ideal_threads, ideal_threads, 'k--', label='Ideal Speedup', linewidth=2, alpha=0.5)
        
        # Реальное ускорение для sections
        sections_data = group[group['method'] == 'sections'].sort_values('num_threads')
        if not sections_data.empty:
            plt.plot(sections_data['num_threads'], sections_data['speedup'], 
                    marker='o', label='Sections', linewidth=2, markersize=8, color='#2E86AB')
        
        plt.xlabel('Number of Threads', fontsize=12)
        plt.ylabel('Speedup', fontsize=12)
        plt.title(f'Speedup vs Threads\n({num_pairs} pairs, vector size {vector_size})', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filename = f'speedup_pairs_{num_pairs}_size_{vector_size}.png'
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Created {filename}")

def plot_efficiency(df, output_dir):
    """График эффективности vs количество потоков"""
    
    for (num_pairs, vector_size), group in df.groupby(['num_pairs', 'vector_size']):
        plt.figure(figsize=(10, 6))
        
        # Идеальная эффективность (100%)
        max_threads = group['num_threads'].max()
        ideal_threads = np.arange(1, max_threads + 1)
        plt.plot(ideal_threads, [100] * len(ideal_threads), 'k--', 
                label='Ideal Efficiency (100%)', linewidth=2, alpha=0.5)
        
        # Реальная эффективность для sections
        sections_data = group[group['method'] == 'sections'].sort_values('num_threads')
        if not sections_data.empty:
            plt.plot(sections_data['num_threads'], sections_data['efficiency'], 
                    marker='o', label='Sections', linewidth=2, markersize=8, color='#A23B72')
        
        plt.xlabel('Number of Threads', fontsize=12)
        plt.ylabel('Efficiency (%)', fontsize=12)
        plt.title(f'Efficiency vs Threads\n({num_pairs} pairs, vector size {vector_size})', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 110)
        plt.tight_layout()
        
        filename = f'efficiency_pairs_{num_pairs}_size_{vector_size}.png'
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Created {filename}")

def plot_time_breakdown(df, output_dir):
    """График разбивки времени на ввод и вычисления"""
    
    plt.figure(figsize=(12, 6))
    
    # Группируем по методу и количеству потоков
    methods = df['method'].unique()
    thread_counts = sorted(df['num_threads'].unique())
    
    x = np.arange(len(thread_counts))
    width = 0.35
    
    for i, method in enumerate(methods):
        method_data = df[df['method'] == method].groupby('num_threads')[['input_time_ms', 'computation_time_ms']].mean()
        
        input_times = [method_data.loc[t, 'input_time_ms'] if t in method_data.index else 0
                      for t in thread_counts]
        compute_times = [method_data.loc[t, 'computation_time_ms'] if t in method_data.index else 0
                        for t in thread_counts]
        
        offset = width * (i - len(methods)/2 + 0.5)
        
        plt.bar(x + offset, input_times, width, label=f'{method.capitalize()} - Input', 
               alpha=0.7)
        plt.bar(x + offset, compute_times, width, bottom=input_times,
               label=f'{method.capitalize()} - Compute', alpha=0.7)
    
    plt.xlabel('Number of Threads', fontsize=12)
    plt.ylabel('Time (ms)', fontsize=12)
    plt.title('Time Breakdown: Input vs Computation', fontsize=14, fontweight='bold')
    plt.xticks(x, thread_counts)
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    filename = 'time_breakdown.png'
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Created {filename}")

def plot_sections_limitation(df, output_dir):
    """График демонстрирующий ограничение sections (2 секции)"""
    
    sections_df = df[df['method'] == 'sections']
    
    if sections_df.empty:
        return
    
    plt.figure(figsize=(10, 6))
    
    # Группируем по размеру данных
    for (num_pairs, vector_size), group in sections_df.groupby(['num_pairs', 'vector_size']):
        group_sorted = group.sort_values('num_threads')
        plt.plot(group_sorted['num_threads'], group_sorted['speedup'], 
                marker='o', label=f'{num_pairs} pairs, size {vector_size}', 
                linewidth=2, markersize=8)
    
    # Теоретический максимум для 2 секций
    max_threads = sections_df['num_threads'].max()
    plt.axhline(y=2.0, color='r', linestyle='--', linewidth=2, 
               label='Theoretical Max (2 sections)', alpha=0.7)
    
    plt.xlabel('Number of Threads', fontsize=12)
    plt.ylabel('Speedup', fontsize=12)
    plt.title('Sections Limitation: Maximum 2 Parallel Tasks', 
             fontsize=14, fontweight='bold')
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    filename = 'sections_limitation.png'
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Created {filename}")

def create_summary_table(df, output_dir):
    """Создание текстовой сводной таблицы"""
    
    output_file = os.path.join(output_dir, 'summary_table.txt')
    
    with open(output_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("SUMMARY TABLE: Vector Dot Products with OpenMP Sections\n")
        f.write("="*100 + "\n\n")
        
        for (num_pairs, vector_size), group in df.groupby(['num_pairs', 'vector_size']):
            f.write(f"\nConfiguration: {num_pairs} pairs, vector size {vector_size}\n")
            f.write("-"*100 + "\n")
            f.write(f"{'Method':<12} {'Threads':<8} {'Time (ms)':<12} {'Input (ms)':<12} "
                   f"{'Compute (ms)':<14} {'Speedup':<10} {'Efficiency':<12}\n")
            f.write("-"*100 + "\n")
            
            for _, row in group.iterrows():
                f.write(f"{row['method']:<12} {row['num_threads']:<8} "
                       f"{row['total_time_ms']:>10.2f}  {row['input_time_ms']:>10.2f}  "
                       f"{row['computation_time_ms']:>12.2f}  {row['speedup']:>8.2f}x  "
                       f"{row['efficiency']:>10.1f}%\n")
            f.write("\n")
        
        # Ключевые выводы
        f.write("\n" + "="*100 + "\n")
        f.write("KEY FINDINGS\n")
        f.write("="*100 + "\n\n")
        
        sections_df = df[df['method'] == 'sections']
        if not sections_df.empty:
            best = sections_df.loc[sections_df['speedup'].idxmax()]
            f.write(f"Best speedup: {best['speedup']:.2f}x with {best['num_threads']} threads\n")
            f.write(f"Configuration: {best['num_pairs']} pairs, vector size {best['vector_size']}\n\n")
            
            sections_2t = sections_df[sections_df['num_threads'] == 2]
            if not sections_2t.empty:
                avg_speedup = sections_2t['speedup'].mean()
                avg_efficiency = sections_2t['efficiency'].mean()
                f.write(f"Average with 2 threads (optimal): {avg_speedup:.2f}x speedup, "
                       f"{avg_efficiency:.1f}% efficiency\n\n")
            
            f.write("Note: Limited benefit beyond 2 threads due to only 2 sections\n")
    
    print(f"  ✓ Created summary_table.txt")

def main():
    # Определяем директории
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    graphs_dir = os.path.join(project_dir, 'graphs')
    
    # Создаем директорию для графиков
    os.makedirs(graphs_dir, exist_ok=True)
    
    # Находим последний обработанный файл
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = find_latest_processed_file()
    
    print(f"\nGenerating graphs from: {csv_file}")
    print(f"Output directory: {graphs_dir}\n")
    
    # Загружаем данные
    df = load_data(csv_file)
    
    # Генерируем графики
    print("Generating graphs...")
    plot_execution_time(df, graphs_dir)
    plot_speedup(df, graphs_dir)
    plot_efficiency(df, graphs_dir)
    plot_time_breakdown(df, graphs_dir)
    plot_sections_limitation(df, graphs_dir)
    create_summary_table(df, graphs_dir)
    
    print(f"\n✓ All graphs saved to: {graphs_dir}")
    print("\nGenerated files:")
    print("  - execution_time_*.png - Execution time vs threads")
    print("  - speedup_*.png - Speedup analysis")
    print("  - efficiency_*.png - Efficiency analysis")
    print("  - time_breakdown.png - Input vs computation time")
    print("  - sections_limitation.png - Demonstration of 2-section limit")
    print("  - summary_table.txt - Numerical summary")
    print()

if __name__ == "__main__":
    main()
