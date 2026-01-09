#!/usr/bin/env python3
"""
Analysis script for Task 6: Loop Scheduling Investigation

This script processes benchmark results and generates statistical analysis
comparing different OpenMP scheduling strategies (static, dynamic, guided)
with uneven workload.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def load_data(csv_file):
    """Load benchmark data from CSV file"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} benchmark results from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)

def calculate_statistics(df):
    """Calculate speedup and efficiency metrics"""
    
    # Group by configuration
    grouped = df.groupby(['num_iterations', 'num_threads', 'schedule', 'chunk_size'])
    
    # Calculate mean execution time for each configuration
    stats = grouped['execution_time_ms'].agg(['mean', 'std', 'min', 'max']).reset_index()
    stats.columns = ['num_iterations', 'num_threads', 'schedule', 'chunk_size', 
                     'mean_time_ms', 'std_time_ms', 'min_time_ms', 'max_time_ms']
    
    # Calculate speedup and efficiency for each iteration count
    results = []
    
    for iterations in stats['num_iterations'].unique():
        iter_data = stats[stats['num_iterations'] == iterations].copy()
        
        # Get sequential baseline (1 thread, sequential schedule)
        baseline = iter_data[
            (iter_data['num_threads'] == 1) & 
            (iter_data['schedule'] == 'sequential')
        ]['mean_time_ms'].values
        
        if len(baseline) == 0:
            print(f"Warning: No sequential baseline found for {iterations} iterations")
            continue
            
        baseline_time = baseline[0]
        
        # Calculate speedup and efficiency for parallel runs
        for _, row in iter_data.iterrows():
            if row['schedule'] != 'sequential':
                speedup = baseline_time / row['mean_time_ms']
                efficiency = speedup / row['num_threads']
                
                results.append({
                    'num_iterations': row['num_iterations'],
                    'num_threads': row['num_threads'],
                    'schedule': row['schedule'],
                    'chunk_size': row['chunk_size'],
                    'mean_time_ms': row['mean_time_ms'],
                    'std_time_ms': row['std_time_ms'],
                    'speedup': speedup,
                    'efficiency': efficiency,
                    'baseline_time_ms': baseline_time
                })
    
    return pd.DataFrame(results)

def print_summary(df):
    """Print summary statistics"""
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    if len(df) == 0:
        print("\nNo data to display. Make sure sequential baseline runs are included.")
        return
    
    for iterations in sorted(df['num_iterations'].unique()):
        print(f"\n{'='*80}")
        print(f"Iterations: {iterations}")
        print(f"{'='*80}")
        
        iter_data = df[df['num_iterations'] == iterations]
        
        for schedule in ['static', 'dynamic', 'guided']:
            sched_data = iter_data[iter_data['schedule'] == schedule]
            
            if len(sched_data) == 0:
                continue
            
            print(f"\n{schedule.upper()} Schedule:")
            print("-" * 80)
            print(f"{'Threads':<10} {'Chunk':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12}")
            print("-" * 80)
            
            for _, row in sched_data.sort_values(['num_threads', 'chunk_size']).iterrows():
                chunk_str = "default" if row['chunk_size'] == 0 else str(int(row['chunk_size']))
                print(f"{int(row['num_threads']):<10} {chunk_str:<10} "
                      f"{row['mean_time_ms']:>10.3f} ± {row['std_time_ms']:<5.2f} "
                      f"{row['speedup']:>8.2f}x    {row['efficiency']:>8.2%}")

def compare_schedules(df):
    """Compare different scheduling strategies"""
    
    print("\n" + "="*80)
    print("SCHEDULE COMPARISON")
    print("="*80)
    
    if len(df) == 0:
        print("\nNo data to display.")
        return
    
    for iterations in sorted(df['num_iterations'].unique()):
        print(f"\n{'='*80}")
        print(f"Iterations: {iterations}")
        print(f"{'='*80}")
        
        iter_data = df[df['num_iterations'] == iterations]
        
        # Compare at different thread counts
        for threads in sorted(iter_data['num_threads'].unique()):
            thread_data = iter_data[iter_data['num_threads'] == threads]
            
            if len(thread_data) == 0:
                continue
            
            print(f"\nThreads: {threads}")
            print("-" * 80)
            print(f"{'Schedule':<15} {'Chunk':<10} {'Time (ms)':<15} {'Speedup':<12} {'Best?':<10}")
            print("-" * 80)
            
            # Find best configuration
            best_time = thread_data['mean_time_ms'].min()
            
            for _, row in thread_data.sort_values('mean_time_ms').iterrows():
                chunk_str = "default" if row['chunk_size'] == 0 else str(int(row['chunk_size']))
                is_best = "✓ BEST" if row['mean_time_ms'] == best_time else ""
                
                print(f"{row['schedule']:<15} {chunk_str:<10} "
                      f"{row['mean_time_ms']:>10.3f} ± {row['std_time_ms']:<5.2f} "
                      f"{row['speedup']:>8.2f}x    {is_best:<10}")

def analyze_chunk_size_impact(df):
    """Analyze impact of chunk size on performance"""
    
    print("\n" + "="*80)
    print("CHUNK SIZE IMPACT ANALYSIS")
    print("="*80)
    
    if len(df) == 0:
        print("\nNo data to display.")
        return
    
    for iterations in sorted(df['num_iterations'].unique()):
        print(f"\n{'='*80}")
        print(f"Iterations: {iterations}")
        print(f"{'='*80}")
        
        iter_data = df[df['num_iterations'] == iterations]
        
        for schedule in ['static', 'dynamic', 'guided']:
            sched_data = iter_data[iter_data['schedule'] == schedule]
            
            if len(sched_data) == 0:
                continue
            
            print(f"\n{schedule.upper()} Schedule:")
            print("-" * 80)
            
            # Group by threads and compare chunk sizes
            for threads in sorted(sched_data['num_threads'].unique()):
                thread_data = sched_data[sched_data['num_threads'] == threads]
                
                if len(thread_data) <= 1:
                    continue
                
                print(f"\nThreads: {threads}")
                print(f"{'Chunk Size':<15} {'Time (ms)':<15} {'Speedup':<12} {'vs Default':<15}")
                print("-" * 40)
                
                # Get default chunk performance
                default_data = thread_data[thread_data['chunk_size'] == 0]
                if len(default_data) == 0:
                    continue
                    
                default_time = default_data['mean_time_ms'].values[0]
                
                for _, row in thread_data.sort_values('chunk_size').iterrows():
                    chunk_str = "default" if row['chunk_size'] == 0 else str(int(row['chunk_size']))
                    vs_default = ((row['mean_time_ms'] - default_time) / default_time) * 100
                    vs_str = f"{vs_default:+.1f}%" if row['chunk_size'] != 0 else "-"
                    
                    print(f"{chunk_str:<15} {row['mean_time_ms']:>10.3f} ± {row['std_time_ms']:<5.2f} "
                          f"{row['speedup']:>8.2f}x    {vs_str:<15}")

def save_processed_data(df, output_file):
    """Save processed data to CSV"""
    try:
        df.to_csv(output_file, index=False)
        print(f"\n✓ Processed data saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Error saving processed data: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_results.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print("="*80)
    print("Task 6: Loop Scheduling Investigation - Analysis")
    print("="*80)
    
    # Load data
    df = load_data(input_file)
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats_df = calculate_statistics(df)
    
    # Print analyses
    print_summary(stats_df)
    compare_schedules(stats_df)
    analyze_chunk_size_impact(stats_df)
    
    # Save processed data
    if len(stats_df) > 0:
        output_file = input_file.replace('.csv', '_processed.csv')
        save_processed_data(stats_df, output_file)
        
        print("\n" + "="*80)
        print("Analysis complete!")
        print("="*80)
        print("\nNext step: Generate graphs with plot_graphs.py")
    else:
        print("\n" + "="*80)
        print("Analysis incomplete - no data to process")
        print("="*80)
        print("\nMake sure to run sequential baseline tests:")
        print("  ./bin/loop_scheduling <iterations> 1 sequential 0 10 results.csv")
        print("\nOr re-run the full benchmark suite:")
        print("  cd scripts && ./run_benchmarks.sh")

if __name__ == "__main__":
    main()
