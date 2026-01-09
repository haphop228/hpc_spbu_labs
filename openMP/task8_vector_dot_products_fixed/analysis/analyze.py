#!/usr/bin/env python3
"""
Анализ результатов бенчмарков для задачи 8: Vector Dot Products with Sections
"""

import pandas as pd
import sys
import os

def load_data(csv_file):
    """Загрузка данных из CSV файла"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} benchmark results from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)

def calculate_metrics(df):
    """Расчет метрик производительности"""
    
    # Получаем базовое время (sequential с 1 потоком)
    baseline = df[df['method'] == 'sequential'].copy()
    
    results = []
    
    for (num_pairs, vector_size), group in df.groupby(['num_pairs', 'vector_size']):
        # Базовое время для этой конфигурации
        base_time = baseline[
            (baseline['num_pairs'] == num_pairs) & 
            (baseline['vector_size'] == vector_size)
        ]['total_time_ms'].values
        
        if len(base_time) == 0:
            continue
            
        base_time = base_time[0]
        
        for _, row in group.iterrows():
            speedup = base_time / row['total_time_ms'] if row['total_time_ms'] > 0 else 0
            efficiency = (speedup / row['num_threads']) * 100 if row['num_threads'] > 0 else 0
            
            results.append({
                'num_pairs': num_pairs,
                'vector_size': vector_size,
                'num_threads': row['num_threads'],
                'method': row['method'],
                'total_time_ms': row['total_time_ms'],
                'input_time_ms': row['input_time_ms'],
                'computation_time_ms': row['computation_time_ms'],
                'speedup': speedup,
                'efficiency': efficiency
            })
    
    return pd.DataFrame(results)

def print_summary(df):
    """Вывод сводной информации"""
    
    print("\n" + "="*80)
    print("SUMMARY: Vector Dot Products with OpenMP Sections")
    print("="*80)
    
    # Группировка по конфигурациям
    for (num_pairs, vector_size), group in df.groupby(['num_pairs', 'vector_size']):
        print(f"\n{'─'*80}")
        print(f"Configuration: {num_pairs} pairs, vector size {vector_size}")
        print(f"{'─'*80}")
        
        print(f"\n{'Method':<15} {'Threads':<10} {'Time (ms)':<12} {'Speedup':<10} {'Efficiency':<12}")
        print("─"*80)
        
        for _, row in group.iterrows():
            print(f"{row['method']:<15} {row['num_threads']:<10} "
                  f"{row['total_time_ms']:>10.2f}  {row['speedup']:>8.2f}x  "
                  f"{row['efficiency']:>10.1f}%")
    
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    # Лучшее ускорение для sections
    sections_df = df[df['method'] == 'sections']
    if not sections_df.empty:
        best_speedup = sections_df.loc[sections_df['speedup'].idxmax()]
        print(f"\n✓ Best speedup with sections: {best_speedup['speedup']:.2f}x")
        print(f"  Configuration: {best_speedup['num_pairs']} pairs, "
              f"vector size {best_speedup['vector_size']}, "
              f"{best_speedup['num_threads']} threads")
        
        # Анализ для 2 потоков (оптимально для 2 секций)
        sections_2t = sections_df[sections_df['num_threads'] == 2]
        if not sections_2t.empty:
            avg_speedup_2t = sections_2t['speedup'].mean()
            avg_efficiency_2t = sections_2t['efficiency'].mean()
            print(f"\n✓ Average performance with 2 threads (optimal for 2 sections):")
            print(f"  Speedup: {avg_speedup_2t:.2f}x")
            print(f"  Efficiency: {avg_efficiency_2t:.1f}%")
        
        # Сравнение 2 vs 4 потока
        sections_4t = sections_df[sections_df['num_threads'] == 4]
        if not sections_2t.empty and not sections_4t.empty:
            improvement = ((sections_4t['speedup'].mean() / sections_2t['speedup'].mean()) - 1) * 100
            print(f"\n✓ Performance improvement from 2 to 4 threads: {improvement:+.1f}%")
            if improvement < 10:
                print("  → Limited benefit beyond 2 threads (expected for 2 sections)")
    
    # Анализ времени ввода vs вычислений
    print(f"\n{'─'*80}")
    print("TIME BREAKDOWN ANALYSIS")
    print(f"{'─'*80}")
    
    for method in df['method'].unique():
        method_df = df[df['method'] == method]
        avg_input = method_df['input_time_ms'].mean()
        avg_compute = method_df['computation_time_ms'].mean()
        total = avg_input + avg_compute
        
        print(f"\n{method.capitalize()}:")
        print(f"  Input time:       {avg_input:>8.2f} ms ({avg_input/total*100:>5.1f}%)")
        print(f"  Computation time: {avg_compute:>8.2f} ms ({avg_compute/total*100:>5.1f}%)")
        print(f"  Total:            {total:>8.2f} ms")

def save_processed_data(df, original_file):
    """Сохранение обработанных данных"""
    output_file = original_file.replace('.csv', '_processed.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✓ Processed data saved to: {output_file}")
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_results.csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    # Загрузка и обработка данных
    df = load_data(csv_file)
    df_processed = calculate_metrics(df)
    
    # Вывод результатов
    print_summary(df_processed)
    
    # Сохранение обработанных данных
    output_file = save_processed_data(df_processed, csv_file)
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Generate graphs:")
    print("   python3 plot_graphs.py")
    print("\n2. View processed data:")
    print(f"   cat {output_file}")
    print()

if __name__ == "__main__":
    main()