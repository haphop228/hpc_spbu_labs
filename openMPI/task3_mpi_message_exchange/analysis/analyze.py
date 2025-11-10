#!/usr/bin/env python3
"""
Анализ результатов бенчмарков MPI обмена сообщениями
"""

import pandas as pd
import sys
import os
from pathlib import Path

def format_size(size_bytes):
    """Форматирование размера в человекочитаемый вид"""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"

def analyze_results(csv_file):
    """Анализ результатов бенчмарков"""
    
    # Чтение данных
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print("=" * 80)
    print("MPI MESSAGE EXCHANGE BENCHMARK ANALYSIS")
    print("=" * 80)
    print()
    
    # Общая информация
    print("DATASET INFORMATION")
    print("-" * 80)
    print(f"Total measurements: {len(df)}")
    print(f"Message sizes tested: {df['message_size_bytes'].nunique()}")
    print(f"Iterations per size: {df['iterations'].iloc[0]}")
    print()
    
    # Сортировка по размеру сообщения
    df = df.sort_values('message_size_bytes')
    
    # Детальная таблица результатов
    print("DETAILED RESULTS")
    print("-" * 80)
    print(f"{'Message Size':<15} {'Avg Time':<12} {'Median Time':<12} {'Std Dev':<12} {'Bandwidth':<12}")
    print(f"{'':15} {'(ms)':<12} {'(ms)':<12} {'(ms)':<12} {'(MB/s)':<12}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        size_str = format_size(row['message_size_bytes'])
        print(f"{size_str:<15} "
              f"{row['avg_time_ms']:>11.6f} "
              f"{row['median_time_ms']:>11.6f} "
              f"{row['std_dev_ms']:>11.6f} "
              f"{row['bandwidth_mbps']:>11.2f}")
    
    print()
    
    # Статистика
    print("PERFORMANCE STATISTICS")
    print("-" * 80)
    
    # Самое быстрое сообщение
    fastest = df.loc[df['avg_time_ms'].idxmin()]
    print(f"Fastest transmission:")
    print(f"  Message size: {format_size(fastest['message_size_bytes'])}")
    print(f"  Average time: {fastest['avg_time_ms']:.6f} ms")
    print(f"  Bandwidth: {fastest['bandwidth_mbps']:.2f} MB/s")
    print()
    
    # Самое медленное сообщение
    slowest = df.loc[df['avg_time_ms'].idxmax()]
    print(f"Slowest transmission:")
    print(f"  Message size: {format_size(slowest['message_size_bytes'])}")
    print(f"  Average time: {slowest['avg_time_ms']:.6f} ms")
    print(f"  Bandwidth: {slowest['bandwidth_mbps']:.2f} MB/s")
    print()
    
    # Лучшая пропускная способность
    best_bw = df.loc[df['bandwidth_mbps'].idxmax()]
    print(f"Best bandwidth:")
    print(f"  Message size: {format_size(best_bw['message_size_bytes'])}")
    print(f"  Bandwidth: {best_bw['bandwidth_mbps']:.2f} MB/s")
    print(f"  Average time: {best_bw['avg_time_ms']:.6f} ms")
    print()
    
    # Худшая пропускная способность
    worst_bw = df.loc[df['bandwidth_mbps'].idxmin()]
    print(f"Worst bandwidth:")
    print(f"  Message size: {format_size(worst_bw['message_size_bytes'])}")
    print(f"  Bandwidth: {worst_bw['bandwidth_mbps']:.2f} MB/s")
    print(f"  Average time: {worst_bw['avg_time_ms']:.6f} ms")
    print()
    
    # Анализ латентности и пропускной способности
    print("LATENCY AND BANDWIDTH ANALYSIS")
    print("-" * 80)
    
    # Оценка латентности (для малых сообщений)
    small_msgs = df[df['message_size_bytes'] <= 1024]
    if not small_msgs.empty:
        avg_latency = small_msgs['avg_time_ms'].mean()
        print(f"Estimated latency (messages ≤ 1KB): {avg_latency:.6f} ms")
    
    # Оценка пиковой пропускной способности (для больших сообщений)
    large_msgs = df[df['message_size_bytes'] >= 1048576]  # >= 1 MB
    if not large_msgs.empty:
        peak_bandwidth = large_msgs['bandwidth_mbps'].max()
        print(f"Peak bandwidth (messages ≥ 1MB): {peak_bandwidth:.2f} MB/s")
    
    print()
    
    # Анализ масштабируемости
    print("SCALABILITY ANALYSIS")
    print("-" * 80)
    
    # Вычисление отношения времени к размеру
    df['time_per_byte'] = df['avg_time_ms'] / df['message_size_bytes'] * 1000  # в микросекундах
    
    print(f"Time per byte (average): {df['time_per_byte'].mean():.6f} µs/byte")
    print(f"Time per byte (min): {df['time_per_byte'].min():.6f} µs/byte")
    print(f"Time per byte (max): {df['time_per_byte'].max():.6f} µs/byte")
    print()
    
    # Сохранение обработанных данных
    output_file = csv_file.replace('.csv', '_processed.csv')
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to: {output_file}")
    print()
    
    # Создание текстового отчета
    report_file = csv_file.replace('.csv', '_summary.txt')
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("MPI MESSAGE EXCHANGE BENCHMARK SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total measurements: {len(df)}\n")
        f.write(f"Message sizes tested: {df['message_size_bytes'].nunique()}\n\n")
        
        f.write("Performance Summary:\n")
        f.write(f"  Fastest time: {df['avg_time_ms'].min():.6f} ms\n")
        f.write(f"  Slowest time: {df['avg_time_ms'].max():.6f} ms\n")
        f.write(f"  Best bandwidth: {df['bandwidth_mbps'].max():.2f} MB/s\n")
        f.write(f"  Worst bandwidth: {df['bandwidth_mbps'].min():.2f} MB/s\n")
        
        if not small_msgs.empty:
            f.write(f"  Estimated latency: {avg_latency:.6f} ms\n")
        if not large_msgs.empty:
            f.write(f"  Peak bandwidth: {peak_bandwidth:.2f} MB/s\n")
    
    print(f"Summary report saved to: {report_file}")
    print()
    
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Next step: Generate graphs with:")
    print(f"  python3 analysis/plot_graphs.py")
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_csv_file>")
        print("Example: python3 analyze.py results/benchmark_20250108_120000.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    analyze_results(csv_file)

if __name__ == "__main__":
    main()