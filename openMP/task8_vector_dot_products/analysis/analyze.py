#!/usr/bin/env python3
"""
Analysis script for Task 8: Vector Dot Products with OpenMP Sections
Processes benchmark results and calculates performance metrics
"""

import pandas as pd
import sys
import os

def analyze_results(csv_file):
    """Analyze benchmark results from CSV file"""
    
    print("=== Task 8: Vector Dot Products - Results Analysis ===\n")
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: File not found: {csv_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"Loaded {len(df)} benchmark results from {csv_file}\n")
    
    # Display column names
    print("Columns:", df.columns.tolist())
    print()
    
    # Group by configuration
    configs = df.groupby(['num_pairs', 'vector_size'])
    
    for (pairs, size), group in configs:
        print(f"\n{'='*80}")
        print(f"Configuration: {pairs} pairs × {size} elements")
        print(f"{'='*80}\n")
        
        # Get sequential baseline
        seq_data = group[group['method'] == 'sequential']
        if len(seq_data) == 0:
            print("Warning: No sequential baseline found")
            continue
        
        seq_time = seq_data['total_time_ms'].values[0]
        seq_input = seq_data['input_time_ms'].values[0]
        seq_compute = seq_data['computation_time_ms'].values[0]
        
        print(f"Sequential Baseline:")
        print(f"  Total time:   {seq_time:8.3f} ms")
        print(f"  Input time:   {seq_input:8.3f} ms ({seq_input/seq_time*100:5.1f}%)")
        print(f"  Compute time: {seq_compute:8.3f} ms ({seq_compute/seq_time*100:5.1f}%)")
        print()
        
        # Analyze parallel results
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        
        if len(par_data) == 0:
            print("Warning: No parallel results found")
            continue
        
        print(f"{'Threads':<8} {'Total(ms)':<12} {'Input(ms)':<12} {'Compute(ms)':<12} {'Speedup':<10} {'Efficiency':<10}")
        print(f"{'-'*80}")
        
        for _, row in par_data.iterrows():
            threads = row['num_threads']
            total_time = row['total_time_ms']
            input_time = row['input_time_ms']
            compute_time = row['computation_time_ms']
            
            speedup = seq_time / total_time if total_time > 0 else 0
            efficiency = speedup / threads if threads > 0 else 0
            
            print(f"{threads:<8} {total_time:<12.3f} {input_time:<12.3f} {compute_time:<12.3f} {speedup:<10.3f} {efficiency:<10.3f}")
        
        print()
        
        # Find best configuration
        best_idx = par_data['total_time_ms'].idxmin()
        best_row = par_data.loc[best_idx]
        best_speedup = seq_time / best_row['total_time_ms']
        
        print(f"Best Performance:")
        print(f"  Threads:   {best_row['num_threads']}")
        print(f"  Time:      {best_row['total_time_ms']:.3f} ms")
        print(f"  Speedup:   {best_speedup:.3f}x")
        print(f"  Efficiency: {best_speedup/best_row['num_threads']:.3f}")
    
    # Overall summary
    print(f"\n{'='*80}")
    print("Overall Summary")
    print(f"{'='*80}\n")
    
    # Best speedup across all configurations
    seq_times = df[df['method'] == 'sequential'].set_index(['num_pairs', 'vector_size'])['total_time_ms']
    par_df = df[df['method'] == 'sections'].copy()
    
    par_df['speedup'] = par_df.apply(
        lambda row: seq_times.loc[(row['num_pairs'], row['vector_size'])] / row['total_time_ms']
        if (row['num_pairs'], row['vector_size']) in seq_times.index else 0,
        axis=1
    )
    
    best_overall = par_df.loc[par_df['speedup'].idxmax()]
    print(f"Best Overall Speedup:")
    print(f"  Configuration: {best_overall['num_pairs']} pairs × {best_overall['vector_size']} elements")
    print(f"  Threads:       {best_overall['num_threads']}")
    print(f"  Speedup:       {best_overall['speedup']:.3f}x")
    print(f"  Efficiency:    {best_overall['speedup']/best_overall['num_threads']:.3f}")
    print()
    
    # Scalability analysis
    print("Scalability Analysis:")
    print(f"  Configurations tested: {len(configs)}")
    print(f"  Thread counts tested:  {sorted(df['num_threads'].unique())}")
    print(f"  Average speedup (all): {par_df['speedup'].mean():.3f}x")
    print(f"  Max speedup achieved:  {par_df['speedup'].max():.3f}x")
    print()
    
    # Save processed results
    output_file = csv_file.replace('.csv', '_processed.csv')
    par_df.to_csv(output_file, index=False)
    print(f"Processed results saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_results.csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    analyze_results(csv_file)