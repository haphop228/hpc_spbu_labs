#!/usr/bin/env python3
"""
Analysis script for Task 7: Reduction with Different Synchronization Methods
Processes benchmark results and calculates performance metrics
"""

import pandas as pd
import sys
import os
from pathlib import Path

def analyze_results(csv_file):
    """Analyze benchmark results and calculate metrics"""
    
    print("=== Task 7: Reduction Synchronization - Results Analysis ===\n")
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    print(f"Loaded {len(df)} benchmark results from {csv_file}\n")
    
    # Get unique values
    array_sizes = sorted(df['array_size'].unique())
    methods = sorted(df['method'].unique())
    threads = sorted(df['num_threads'].unique())
    
    print(f"Array sizes: {array_sizes}")
    print(f"Methods: {methods}")
    print(f"Thread counts: {threads}\n")
    
    # Calculate metrics for each array size
    for size in array_sizes:
        print(f"\n{'='*80}")
        print(f"Array Size: {size:,}")
        print(f"{'='*80}\n")
        
        size_df = df[df['array_size'] == size]
        
        # Get sequential baseline
        seq_df = size_df[size_df['method'] == 'sequential']
        if len(seq_df) == 0:
            print("Warning: No sequential baseline found")
            continue
        
        seq_time = seq_df['execution_time_ms'].values[0]
        print(f"Sequential baseline: {seq_time:.3f} ms\n")
        
        # Analyze each method
        for method in methods:
            if method == 'sequential':
                continue
            
            print(f"\n--- Method: {method.upper()} ---")
            method_df = size_df[size_df['method'] == method].sort_values('num_threads')
            
            if len(method_df) == 0:
                print(f"No data for method {method}")
                continue
            
            print(f"{'Threads':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12}")
            print("-" * 50)
            
            for _, row in method_df.iterrows():
                thread_count = row['num_threads']
                time_ms = row['execution_time_ms']
                speedup = seq_time / time_ms
                efficiency = speedup / thread_count
                
                print(f"{thread_count:<10} {time_ms:<15.3f} {speedup:<12.3f} {efficiency:<12.3f}")
        
        # Compare methods at different thread counts
        print(f"\n\n--- Method Comparison ---")
        for thread_count in threads:
            if thread_count == 1:
                continue
            
            print(f"\nThreads: {thread_count}")
            print(f"{'Method':<15} {'Time (ms)':<15} {'Speedup':<12} {'vs Builtin':<15}")
            print("-" * 60)
            
            thread_df = size_df[size_df['num_threads'] == thread_count]
            builtin_time = None
            
            # Get builtin time first
            builtin_df = thread_df[thread_df['method'] == 'builtin']
            if len(builtin_df) > 0:
                builtin_time = builtin_df['execution_time_ms'].values[0]
            
            for method in ['builtin', 'atomic', 'critical', 'lock']:
                method_row = thread_df[thread_df['method'] == method]
                if len(method_row) == 0:
                    continue
                
                time_ms = method_row['execution_time_ms'].values[0]
                speedup = seq_time / time_ms
                
                if builtin_time and method != 'builtin':
                    vs_builtin = f"{time_ms / builtin_time:.2f}x slower"
                else:
                    vs_builtin = "baseline"
                
                print(f"{method:<15} {time_ms:<15.3f} {speedup:<12.3f} {vs_builtin:<15}")
    
    # Summary statistics
    print(f"\n\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")
    
    for size in array_sizes:
        print(f"\nArray Size: {size:,}")
        size_df = df[df['array_size'] == size]
        seq_time = size_df[size_df['method'] == 'sequential']['execution_time_ms'].values[0]
        
        # Find best configuration for each method
        for method in ['builtin', 'atomic', 'critical', 'lock']:
            method_df = size_df[size_df['method'] == method]
            if len(method_df) == 0:
                continue
            
            best_row = method_df.loc[method_df['execution_time_ms'].idxmin()]
            best_threads = int(best_row['num_threads'])
            best_time = best_row['execution_time_ms']
            best_speedup = seq_time / best_time
            
            print(f"  {method:<12} - Best: {best_threads:3d} threads, "
                  f"{best_time:8.3f} ms, speedup: {best_speedup:6.3f}x")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_results.csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    analyze_results(csv_file)

if __name__ == "__main__":
    main()