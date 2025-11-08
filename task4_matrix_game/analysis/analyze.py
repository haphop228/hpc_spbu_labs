#!/usr/bin/env python3
"""
Analysis script for Task 4: Matrix Game (Maximin) benchmarks
Processes CSV results and calculates performance metrics
"""

import pandas as pd
import sys
import os
from pathlib import Path

def load_data(csv_file):
    """Load benchmark data from CSV file"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} records from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        sys.exit(1)

def calculate_statistics(df):
    """Calculate mean, min, max, std for each configuration"""
    stats = df.groupby(['N', 'num_threads', 'method']).agg({
        'execution_time_ms': ['mean', 'min', 'max', 'std'],
        'result_value': 'mean'
    }).reset_index()
    
    # Flatten column names
    stats.columns = ['N', 'num_threads', 'method', 
                     'time_mean', 'time_min', 'time_max', 'time_std', 'result']
    
    return stats

def calculate_speedup(stats):
    """Calculate speedup relative to single thread"""
    results = []
    
    for size in stats['N'].unique():
        for method in stats['method'].unique():
            subset = stats[(stats['N'] == size) & (stats['method'] == method)]
            
            if len(subset) == 0:
                continue
            
            # Get baseline (1 thread)
            baseline = subset[subset['num_threads'] == 1]
            if len(baseline) == 0:
                continue
            
            baseline_time = baseline['time_mean'].values[0]
            
            for _, row in subset.iterrows():
                speedup = baseline_time / row['time_mean']
                efficiency = speedup / row['num_threads']
                
                results.append({
                    'N': size,
                    'num_threads': row['num_threads'],
                    'method': method,
                    'time_mean': row['time_mean'],
                    'time_std': row['time_std'],
                    'result': row['result'],
                    'speedup': speedup,
                    'efficiency': efficiency
                })
    
    return pd.DataFrame(results)

def print_summary(df_analysis):
    """Print summary tables"""
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY - MATRIX GAME (MAXIMIN)")
    print("="*80)
    
    for size in sorted(df_analysis['N'].unique()):
        print(f"\n{'='*80}")
        print(f"Matrix Size: {size}x{size}")
        print(f"{'='*80}")
        
        subset = df_analysis[df_analysis['N'] == size]
        
        print(f"\n{'Method':<15} {'Threads':<8} {'Time (ms)':<12} {'Speedup':<10} {'Efficiency':<12}")
        print("-" * 80)
        
        for method in sorted(subset['method'].unique()):
            method_data = subset[subset['method'] == method].sort_values('num_threads')
            
            for _, row in method_data.iterrows():
                print(f"{method:<15} {row['num_threads']:<8} "
                      f"{row['time_mean']:>10.3f}  "
                      f"{row['speedup']:>8.2f}x  "
                      f"{row['efficiency']:>10.1%}")
        
        print()

def compare_methods(df_analysis):
    """Compare different methods"""
    print("\n" + "="*80)
    print("METHOD COMPARISON")
    print("="*80)
    
    for size in sorted(df_analysis['N'].unique()):
        print(f"\nMatrix Size: {size}x{size}")
        print("-" * 80)
        
        subset = df_analysis[df_analysis['N'] == size]
        
        # Compare at different thread counts
        for threads in sorted(subset['num_threads'].unique()):
            thread_data = subset[subset['num_threads'] == threads]
            
            if len(thread_data) > 1:
                print(f"\n  Threads: {threads}")
                for _, row in thread_data.iterrows():
                    print(f"    {row['method']:<12}: {row['time_mean']:>8.3f} ms "
                          f"(speedup: {row['speedup']:>6.2f}x, efficiency: {row['efficiency']:>6.1%})")

def save_processed_data(df_analysis, output_file):
    """Save processed data to CSV"""
    df_analysis.to_csv(output_file, index=False)
    print(f"\n✓ Processed data saved to: {output_file}")

def generate_summary_table(df_analysis, output_dir):
    """Generate text summary table"""
    output_file = os.path.join(output_dir, 'summary_table.txt')
    
    with open(output_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("MATRIX GAME (MAXIMIN) - PERFORMANCE SUMMARY\n")
        f.write("Formula: y = max(min(row_i)) for i=1..N\n")
        f.write("="*100 + "\n\n")
        
        for size in sorted(df_analysis['N'].unique()):
            f.write(f"\n{'='*100}\n")
            f.write(f"Matrix Size: {size}x{size}\n")
            f.write(f"{'='*100}\n")
            
            subset = df_analysis[df_analysis['N'] == size]
            
            f.write(f"\n{'Method':<15} {'Threads':<8} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12} {'Result':<20}\n")
            f.write("-" * 100 + "\n")
            
            for method in sorted(subset['method'].unique()):
                method_data = subset[subset['method'] == method].sort_values('num_threads')
                
                for _, row in method_data.iterrows():
                    f.write(f"{method:<15} {row['num_threads']:<8} "
                           f"{row['time_mean']:>13.3f}  "
                           f"{row['speedup']:>10.2f}x  "
                           f"{row['efficiency']:>10.1%}  "
                           f"{row['result']:>18.6f}\n")
            
            f.write("\n")
        
        # Add method comparison
        f.write("\n" + "="*100 + "\n")
        f.write("METHOD COMPARISON\n")
        f.write("="*100 + "\n\n")
        
        for size in sorted(df_analysis['N'].unique()):
            f.write(f"\nMatrix Size: {size}x{size}\n")
            f.write("-" * 100 + "\n")
            
            subset = df_analysis[df_analysis['N'] == size]
            
            for threads in sorted(subset['num_threads'].unique()):
                thread_data = subset[subset['num_threads'] == threads]
                
                if len(thread_data) > 1:
                    f.write(f"\n  Threads: {threads}\n")
                    for _, row in thread_data.iterrows():
                        f.write(f"    {row['method']:<12}: {row['time_mean']:>8.3f} ms "
                               f"(speedup: {row['speedup']:>6.2f}x, efficiency: {row['efficiency']:>6.1%})\n")
            f.write("\n")
    
    print(f"✓ Summary table saved to: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <benchmark_results.csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"✗ File not found: {csv_file}")
        sys.exit(1)
    
    print("="*80)
    print("MATRIX GAME (MAXIMIN) - BENCHMARK ANALYSIS")
    print("="*80)
    
    # Load data
    df = load_data(csv_file)
    
    # Calculate statistics
    print("\nCalculating statistics...")
    stats = calculate_statistics(df)
    
    # Calculate speedup and efficiency
    print("Calculating speedup and efficiency...")
    df_analysis = calculate_speedup(stats)
    
    # Print summary
    print_summary(df_analysis)
    
    # Compare methods
    compare_methods(df_analysis)
    
    # Save processed data
    output_file = csv_file.replace('.csv', '_processed.csv')
    save_processed_data(df_analysis, output_file)
    
    # Generate summary table
    output_dir = os.path.dirname(csv_file)
    if not output_dir:
        output_dir = '.'
    graphs_dir = os.path.join(os.path.dirname(output_dir), 'graphs')
    os.makedirs(graphs_dir, exist_ok=True)
    generate_summary_table(df_analysis, graphs_dir)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nNext step: Generate graphs with plot_graphs.py")

if __name__ == '__main__':
    main()