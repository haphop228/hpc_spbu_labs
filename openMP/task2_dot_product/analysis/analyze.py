#!/usr/bin/env python3

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

def load_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        sys.exit(1)

def calculate_statistics(df):
    grouped = df.groupby(['vector_size', 'num_threads', 'method'])
    
    stats = grouped['execution_time_ms'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max'),
        ('count', 'count')
    ]).reset_index()
    
    return stats

def calculate_speedup(stats):
    results = []
    
    for size in stats['vector_size'].unique():
        for method in stats['method'].unique():
            # Get baseline (1 thread) time
            baseline = stats[
                (stats['vector_size'] == size) & 
                (stats['num_threads'] == 1) & 
                (stats['method'] == method)
            ]
            
            if len(baseline) == 0:
                continue
                
            baseline_time = baseline['mean'].values[0]
            
            # Calculate speedup for all thread counts
            method_data = stats[
                (stats['vector_size'] == size) & 
                (stats['method'] == method)
            ].copy()
            
            method_data['speedup'] = baseline_time / method_data['mean']
            method_data['efficiency'] = method_data['speedup'] / method_data['num_threads']
            
            results.append(method_data)
    
    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()

def print_summary(stats_with_speedup):
    """Print summary tables"""
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    
    for size in sorted(stats_with_speedup['vector_size'].unique()):
        print(f"\n{'='*80}")
        print(f"Vector Size: {size:,} elements")
        print(f"{'='*80}")
        
        size_data = stats_with_speedup[stats_with_speedup['vector_size'] == size]
        
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            
            print(f"\nMethod: {method}")
            print("-" * 80)
            print(f"{'Threads':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12} {'Std Dev':<12}")
            print("-" * 80)
            
            for _, row in method_data.iterrows():
                print(f"{row['num_threads']:<10} "
                      f"{row['mean']:<15.6f} "
                      f"{row['speedup']:<12.4f} "
                      f"{row['efficiency']:<12.4f} "
                      f"{row['std']:<12.6f}")
            
            # Find best configuration
            best_speedup_idx = method_data['speedup'].idxmax()
            best_row = method_data.loc[best_speedup_idx]
            print(f"\n  → Best speedup: {best_row['speedup']:.4f}x at {int(best_row['num_threads'])} threads")
            print(f"  → Efficiency: {best_row['efficiency']:.4f}")

def save_processed_data(stats_with_speedup, output_file):
    stats_with_speedup.to_csv(output_file, index=False)

def compare_methods(stats_with_speedup):
    print("\n" + "="*80)
    print("METHOD COMPARISON")
    print("="*80)
    
    for size in sorted(stats_with_speedup['vector_size'].unique()):
        print(f"\nVector Size: {size:,} elements")
        print("-" * 80)
        
        size_data = stats_with_speedup[stats_with_speedup['vector_size'] == size]
        
        for threads in sorted(size_data['num_threads'].unique()):
            thread_data = size_data[size_data['num_threads'] == threads]
            
            if len(thread_data) >= 2:
                reduction = thread_data[thread_data['method'] == 'reduction']
                no_reduction = thread_data[thread_data['method'] == 'no-reduction']
                
                if len(reduction) > 0 and len(no_reduction) > 0:
                    red_time = reduction['mean'].values[0]
                    no_red_time = no_reduction['mean'].values[0]
                    
                    faster = "reduction" if red_time < no_red_time else "no-reduction"
                    ratio = max(red_time, no_red_time) / min(red_time, no_red_time)
                    
                    print(f"  {threads:3d} threads: {faster:15s} is {ratio:.2f}x faster "
                          f"(reduction: {red_time:.4f}ms, no-reduction: {no_red_time:.4f}ms)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_csv_file>")
        print("Example: python3 analyze.py ../results/benchmark_20240101_120000.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        sys.exit(1)
    
    df = load_data(csv_file)
    stats = calculate_statistics(df)
    stats_with_speedup = calculate_speedup(stats)
    
    if len(stats_with_speedup) == 0:
        sys.exit(1)
    
    print_summary(stats_with_speedup)
    compare_methods(stats_with_speedup)
    output_file = csv_file.replace('.csv', '_processed.csv')
    save_processed_data(stats_with_speedup, output_file)

if __name__ == "__main__":
    main()