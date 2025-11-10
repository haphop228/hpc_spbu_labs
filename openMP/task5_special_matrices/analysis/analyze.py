#!/usr/bin/env python3
"""
Analysis script for Task 5: Special Matrices benchmarks
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
    stats = df.groupby(['N', 'matrix_type', 'bandwidth', 'num_threads', 'schedule', 'chunk_size']).agg({
        'execution_time_ms': ['mean', 'min', 'max', 'std'],
        'result_value': 'mean'
    }).reset_index()
    
    # Flatten column names
    stats.columns = ['N', 'matrix_type', 'bandwidth', 'num_threads', 'schedule', 'chunk_size',
                     'time_mean', 'time_min', 'time_max', 'time_std', 'result']
    
    return stats

def calculate_speedup(stats):
    """Calculate speedup relative to single thread"""
    results = []
    
    for size in stats['N'].unique():
        for matrix_type in stats['matrix_type'].unique():
            for schedule in stats['schedule'].unique():
                for chunk in stats['chunk_size'].unique():
                    subset = stats[
                        (stats['N'] == size) & 
                        (stats['matrix_type'] == matrix_type) &
                        (stats['schedule'] == schedule) &
                        (stats['chunk_size'] == chunk)
                    ]
                    
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
                            'matrix_type': matrix_type,
                            'bandwidth': row['bandwidth'],
                            'num_threads': row['num_threads'],
                            'schedule': schedule,
                            'chunk_size': chunk,
                            'time_mean': row['time_mean'],
                            'time_std': row['time_std'],
                            'result': row['result'],
                            'speedup': speedup,
                            'efficiency': efficiency
                        })
    
    return pd.DataFrame(results)

def print_summary(df_analysis):
    """Print summary tables"""
    print("\n" + "="*100)
    print("PERFORMANCE SUMMARY - SPECIAL MATRICES (MAXIMIN)")
    print("="*100)
    
    for size in sorted(df_analysis['N'].unique()):
        for matrix_type in sorted(df_analysis['matrix_type'].unique()):
            print(f"\n{'='*100}")
            print(f"Matrix Size: {size}x{size}, Type: {matrix_type.upper()}")
            print(f"{'='*100}")
            
            subset = df_analysis[
                (df_analysis['N'] == size) & 
                (df_analysis['matrix_type'] == matrix_type)
            ]
            
            print(f"\n{'Schedule':<10} {'Chunk':<8} {'Threads':<8} {'Time (ms)':<12} {'Speedup':<10} {'Efficiency':<12}")
            print("-" * 100)
            
            for schedule in sorted(subset['schedule'].unique()):
                schedule_data = subset[subset['schedule'] == schedule]
                
                for chunk in sorted(schedule_data['chunk_size'].unique()):
                    chunk_data = schedule_data[schedule_data['chunk_size'] == chunk].sort_values('num_threads')
                    
                    chunk_label = "default" if chunk == 0 else str(chunk)
                    
                    for _, row in chunk_data.iterrows():
                        print(f"{schedule:<10} {chunk_label:<8} {row['num_threads']:<8} "
                              f"{row['time_mean']:>10.3f}  "
                              f"{row['speedup']:>8.2f}x  "
                              f"{row['efficiency']:>10.1%}")
                    
                    if len(chunk_data) > 0:
                        print()

def compare_schedules(df_analysis):
    """Compare different scheduling strategies"""
    print("\n" + "="*100)
    print("SCHEDULING STRATEGY COMPARISON")
    print("="*100)
    
    for size in sorted(df_analysis['N'].unique()):
        for matrix_type in sorted(df_analysis['matrix_type'].unique()):
            print(f"\nMatrix Size: {size}x{size}, Type: {matrix_type.upper()}")
            print("-" * 100)
            
            subset = df_analysis[
                (df_analysis['N'] == size) & 
                (df_analysis['matrix_type'] == matrix_type)
            ]
            
            # Compare at different thread counts
            for threads in sorted(subset['num_threads'].unique()):
                thread_data = subset[subset['num_threads'] == threads]
                
                if len(thread_data) > 1:
                    print(f"\n  Threads: {threads}")
                    for _, row in thread_data.iterrows():
                        chunk_label = "default" if row['chunk_size'] == 0 else f"chunk={row['chunk_size']}"
                        print(f"    {row['schedule']:<10} ({chunk_label:<12}): {row['time_mean']:>8.3f} ms "
                              f"(speedup: {row['speedup']:>6.2f}x, efficiency: {row['efficiency']:>6.1%})")

def compare_matrix_types(df_analysis):
    """Compare different matrix types"""
    print("\n" + "="*100)
    print("MATRIX TYPE COMPARISON")
    print("="*100)
    
    for size in sorted(df_analysis['N'].unique()):
        print(f"\nMatrix Size: {size}x{size}")
        print("-" * 100)
        
        subset = df_analysis[df_analysis['N'] == size]
        
        # Compare at different thread counts with static schedule
        for threads in sorted(subset['num_threads'].unique()):
            thread_data = subset[
                (subset['num_threads'] == threads) & 
                (subset['schedule'] == 'static') &
                (subset['chunk_size'] == 0)
            ]
            
            if len(thread_data) > 1:
                print(f"\n  Threads: {threads} (static schedule)")
                for _, row in thread_data.iterrows():
                    print(f"    {row['matrix_type']:<12}: {row['time_mean']:>8.3f} ms "
                          f"(speedup: {row['speedup']:>6.2f}x, efficiency: {row['efficiency']:>6.1%})")

def save_processed_data(df_analysis, output_file):
    """Save processed data to CSV"""
    df_analysis.to_csv(output_file, index=False)
    print(f"\n✓ Processed data saved to: {output_file}")

def generate_summary_table(df_analysis, output_dir):
    """Generate text summary table"""
    output_file = os.path.join(output_dir, 'summary_table.txt')
    
    with open(output_file, 'w') as f:
        f.write("="*120 + "\n")
        f.write("SPECIAL MATRICES (MAXIMIN) - PERFORMANCE SUMMARY\n")
        f.write("Task 5: Matrix types (banded, triangular) with OpenMP scheduling strategies\n")
        f.write("Formula: y = max(min(row_i)) for i=1..N\n")
        f.write("="*120 + "\n\n")
        
        for size in sorted(df_analysis['N'].unique()):
            for matrix_type in sorted(df_analysis['matrix_type'].unique()):
                f.write(f"\n{'='*120}\n")
                f.write(f"Matrix Size: {size}x{size}, Type: {matrix_type.upper()}\n")
                f.write(f"{'='*120}\n")
                
                subset = df_analysis[
                    (df_analysis['N'] == size) & 
                    (df_analysis['matrix_type'] == matrix_type)
                ]
                
                f.write(f"\n{'Schedule':<12} {'Chunk':<10} {'Threads':<8} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12}\n")
                f.write("-" * 120 + "\n")
                
                for schedule in sorted(subset['schedule'].unique()):
                    schedule_data = subset[subset['schedule'] == schedule]
                    
                    for chunk in sorted(schedule_data['chunk_size'].unique()):
                        chunk_data = schedule_data[schedule_data['chunk_size'] == chunk].sort_values('num_threads')
                        
                        chunk_label = "default" if chunk == 0 else str(chunk)
                        
                        for _, row in chunk_data.iterrows():
                            f.write(f"{schedule:<12} {chunk_label:<10} {row['num_threads']:<8} "
                                   f"{row['time_mean']:>13.3f}  "
                                   f"{row['speedup']:>10.2f}x  "
                                   f"{row['efficiency']:>10.1%}\n")
                        
                        if len(chunk_data) > 0:
                            f.write("\n")
        
        # Add scheduling comparison
        f.write("\n" + "="*120 + "\n")
        f.write("SCHEDULING STRATEGY COMPARISON\n")
        f.write("="*120 + "\n\n")
        
        for size in sorted(df_analysis['N'].unique()):
            for matrix_type in sorted(df_analysis['matrix_type'].unique()):
                f.write(f"\nMatrix Size: {size}x{size}, Type: {matrix_type.upper()}\n")
                f.write("-" * 120 + "\n")
                
                subset = df_analysis[
                    (df_analysis['N'] == size) & 
                    (df_analysis['matrix_type'] == matrix_type)
                ]
                
                for threads in sorted(subset['num_threads'].unique()):
                    thread_data = subset[subset['num_threads'] == threads]
                    
                    if len(thread_data) > 1:
                        f.write(f"\n  Threads: {threads}\n")
                        for _, row in thread_data.iterrows():
                            chunk_label = "default" if row['chunk_size'] == 0 else f"chunk={row['chunk_size']}"
                            f.write(f"    {row['schedule']:<10} ({chunk_label:<12}): {row['time_mean']:>8.3f} ms "
                                   f"(speedup: {row['speedup']:>6.2f}x, efficiency: {row['efficiency']:>6.1%})\n")
                f.write("\n")
        
        # Add matrix type comparison
        f.write("\n" + "="*120 + "\n")
        f.write("MATRIX TYPE COMPARISON\n")
        f.write("="*120 + "\n\n")
        
        for size in sorted(df_analysis['N'].unique()):
            f.write(f"\nMatrix Size: {size}x{size}\n")
            f.write("-" * 120 + "\n")
            
            subset = df_analysis[df_analysis['N'] == size]
            
            for threads in sorted(subset['num_threads'].unique()):
                thread_data = subset[
                    (subset['num_threads'] == threads) & 
                    (subset['schedule'] == 'static') &
                    (subset['chunk_size'] == 0)
                ]
                
                if len(thread_data) > 1:
                    f.write(f"\n  Threads: {threads} (static schedule)\n")
                    for _, row in thread_data.iterrows():
                        f.write(f"    {row['matrix_type']:<12}: {row['time_mean']:>8.3f} ms "
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
    
    print("="*100)
    print("SPECIAL MATRICES (MAXIMIN) - BENCHMARK ANALYSIS")
    print("="*100)
    
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
    
    # Compare schedules
    compare_schedules(df_analysis)
    
    # Compare matrix types
    compare_matrix_types(df_analysis)
    
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
    
    print("\n" + "="*100)
    print("ANALYSIS COMPLETE")
    print("="*100)
    print("\nNext step: Generate graphs with plot_graphs.py")

if __name__ == '__main__':
    main()