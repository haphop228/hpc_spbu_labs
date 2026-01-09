#!/usr/bin/env python3
"""
Analysis script for Task 9: Nested Parallelism benchmarks
Processes CSV results and generates summary statistics
"""

import pandas as pd
import sys
import os
from pathlib import Path

def analyze_results(csv_file):
    """Analyze benchmark results from CSV file"""
    
    print("=" * 60)
    print("Task 9: Nested Parallelism - Results Analysis")
    print("=" * 60)
    print(f"\nReading data from: {csv_file}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    print(f"Total measurements: {len(df)}")
    print(f"Matrix sizes: {sorted(df['N'].unique())}")
    print(f"Methods: {df['method'].unique()}")
    print(f"Thread counts: {sorted(df['num_threads'].unique())}")
    
    # Group by configuration and calculate statistics
    grouped = df.groupby(['N', 'num_threads', 'outer_threads', 'inner_threads', 'method'])
    
    stats = grouped['execution_time_ms'].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    stats.columns = ['N', 'num_threads', 'outer_threads', 'inner_threads', 'method', 
                     'mean_time', 'std_time', 'min_time', 'max_time', 'runs']
    
    # Calculate speedup relative to sequential
    results = []
    
    for size in stats['N'].unique():
        size_data = stats[stats['N'] == size].copy()
        
        # Get sequential baseline
        seq_time = size_data[size_data['method'] == 'sequential']['mean_time'].values
        if len(seq_time) == 0:
            print(f"Warning: No sequential baseline for size {size}")
            continue
        seq_time = seq_time[0]
        
        # Calculate speedup and efficiency for each configuration
        for idx, row in size_data.iterrows():
            speedup = seq_time / row['mean_time']
            efficiency = speedup / row['num_threads'] if row['num_threads'] > 0 else 0
            
            results.append({
                'N': row['N'],
                'num_threads': row['num_threads'],
                'outer_threads': row['outer_threads'],
                'inner_threads': row['inner_threads'],
                'method': row['method'],
                'mean_time': row['mean_time'],
                'std_time': row['std_time'],
                'speedup': speedup,
                'efficiency': efficiency,
                'runs': row['runs']
            })
    
    results_df = pd.DataFrame(results)
    
    # Save processed results
    output_file = csv_file.replace('.csv', '_processed.csv')
    results_df.to_csv(output_file, index=False)
    print(f"\nProcessed results saved to: {output_file}")
    
    # Print summary tables
    print("\n" + "=" * 60)
    print("SUMMARY BY METHOD AND SIZE")
    print("=" * 60)
    
    for size in sorted(results_df['N'].unique()):
        print(f"\n{'=' * 60}")
        print(f"Matrix Size: {size}x{size}")
        print(f"{'=' * 60}")
        
        size_results = results_df[results_df['N'] == size].copy()
        
        # Sequential
        seq = size_results[size_results['method'] == 'sequential']
        if not seq.empty:
            print(f"\nSequential (baseline):")
            print(f"  Time: {seq['mean_time'].values[0]:.3f} ms")
        
        # Flat parallelism
        print(f"\nFlat Parallelism:")
        flat = size_results[size_results['method'] == 'flat'].sort_values('num_threads')
        if not flat.empty:
            print(f"{'Threads':<10} {'Time (ms)':<12} {'Speedup':<10} {'Efficiency':<12}")
            print("-" * 50)
            for _, row in flat.iterrows():
                print(f"{row['num_threads']:<10} {row['mean_time']:<12.3f} "
                      f"{row['speedup']:<10.2f} {row['efficiency']:<12.2%}")
        
        # Nested parallelism
        print(f"\nNested Parallelism:")
        nested = size_results[size_results['method'] == 'nested'].sort_values('num_threads')
        if not nested.empty:
            print(f"{'Config':<15} {'Time (ms)':<12} {'Speedup':<10} {'Efficiency':<12}")
            print("-" * 55)
            for _, row in nested.iterrows():
                config = f"{int(row['outer_threads'])}x{int(row['inner_threads'])}"
                print(f"{config:<15} {row['mean_time']:<12.3f} "
                      f"{row['speedup']:<10.2f} {row['efficiency']:<12.2%}")
    
    # Comparison: Flat vs Nested
    print("\n" + "=" * 60)
    print("FLAT vs NESTED COMPARISON")
    print("=" * 60)
    
    for size in sorted(results_df['N'].unique()):
        print(f"\nMatrix Size: {size}x{size}")
        print(f"{'Threads':<10} {'Flat (ms)':<12} {'Nested (ms)':<12} {'Difference':<12}")
        print("-" * 50)
        
        size_results = results_df[results_df['N'] == size]
        
        for threads in sorted(size_results['num_threads'].unique()):
            if threads == 1:
                continue
                
            flat_time = size_results[
                (size_results['method'] == 'flat') & 
                (size_results['num_threads'] == threads)
            ]['mean_time'].values
            
            nested_time = size_results[
                (size_results['method'] == 'nested') & 
                (size_results['num_threads'] == threads)
            ]['mean_time'].values
            
            if len(flat_time) > 0 and len(nested_time) > 0:
                flat_time = flat_time[0]
                nested_time = nested_time[0]
                diff_pct = ((nested_time - flat_time) / flat_time) * 100
                
                print(f"{threads:<10} {flat_time:<12.3f} {nested_time:<12.3f} "
                      f"{diff_pct:+.1f}%")
    
    # Best configurations
    print("\n" + "=" * 60)
    print("BEST CONFIGURATIONS")
    print("=" * 60)
    
    for size in sorted(results_df['N'].unique()):
        size_results = results_df[results_df['N'] == size]
        
        # Best flat
        best_flat = size_results[size_results['method'] == 'flat'].nsmallest(1, 'mean_time')
        if not best_flat.empty:
            row = best_flat.iloc[0]
            print(f"\nSize {size}x{size} - Best Flat:")
            print(f"  Threads: {int(row['num_threads'])}")
            print(f"  Time: {row['mean_time']:.3f} ms")
            print(f"  Speedup: {row['speedup']:.2f}x")
            print(f"  Efficiency: {row['efficiency']:.2%}")
        
        # Best nested
        best_nested = size_results[size_results['method'] == 'nested'].nsmallest(1, 'mean_time')
        if not best_nested.empty:
            row = best_nested.iloc[0]
            print(f"\nSize {size}x{size} - Best Nested:")
            print(f"  Config: {int(row['outer_threads'])}x{int(row['inner_threads'])} = {int(row['num_threads'])} threads")
            print(f"  Time: {row['mean_time']:.3f} ms")
            print(f"  Speedup: {row['speedup']:.2f}x")
            print(f"  Efficiency: {row['efficiency']:.2%}")
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nProcessed data saved to: {output_file}")
    print("\nNext step: python3 plot_graphs.py")
    
    return results_df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_results.csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    analyze_results(csv_file)
