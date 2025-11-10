#!/usr/bin/env python3
"""
Graph generation script for Task 7: Reduction with Different Synchronization Methods
Creates visualizations of benchmark results
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

def find_latest_results(results_dir):
    """Find the most recent benchmark results file"""
    results_path = Path(results_dir)
    csv_files = list(results_path.glob("benchmark_*.csv"))
    
    if not csv_files:
        return None
    
    # Sort by modification time and return the latest
    latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)

def plot_execution_time(df, size, output_dir):
    """Plot execution time vs number of threads for each method"""
    size_df = df[df['array_size'] == size]
    methods = ['builtin', 'atomic', 'critical', 'lock']
    
    plt.figure(figsize=(12, 8))
    
    for method in methods:
        method_df = size_df[size_df['method'] == method].sort_values('num_threads')
        if len(method_df) > 0:
            plt.plot(method_df['num_threads'], method_df['execution_time_ms'], 
                    marker='o', linewidth=2, markersize=8, label=method.capitalize())
    
    plt.xlabel('Number of Threads', fontsize=12)
    plt.ylabel('Execution Time (ms)', fontsize=12)
    plt.title(f'Execution Time vs Threads (Array Size: {size:,})', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log', base=2)
    plt.yscale('log')
    
    # Set x-axis ticks
    threads = sorted(size_df['num_threads'].unique())
    plt.xticks(threads, [str(t) for t in threads])
    
    plt.tight_layout()
    output_file = output_dir / f'execution_time_size_{size}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created: {output_file}")
    plt.close()

def plot_speedup(df, size, output_dir):
    """Plot speedup vs number of threads for each method"""
    size_df = df[df['array_size'] == size]
    methods = ['builtin', 'atomic', 'critical', 'lock']
    
    # Get sequential baseline
    seq_time = size_df[size_df['method'] == 'sequential']['execution_time_ms'].values[0]
    
    plt.figure(figsize=(12, 8))
    
    for method in methods:
        method_df = size_df[size_df['method'] == method].sort_values('num_threads')
        if len(method_df) > 0:
            speedup = seq_time / method_df['execution_time_ms']
            plt.plot(method_df['num_threads'], speedup, 
                    marker='o', linewidth=2, markersize=8, label=method.capitalize())
    
    # Plot ideal speedup line
    threads = sorted(size_df['num_threads'].unique())
    plt.plot(threads, threads, 'k--', linewidth=2, label='Ideal Speedup', alpha=0.5)
    
    plt.xlabel('Number of Threads', fontsize=12)
    plt.ylabel('Speedup', fontsize=12)
    plt.title(f'Speedup vs Threads (Array Size: {size:,})', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log', base=2)
    plt.yscale('log', base=2)
    
    plt.xticks(threads, [str(t) for t in threads])
    
    plt.tight_layout()
    output_file = output_dir / f'speedup_size_{size}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created: {output_file}")
    plt.close()

def plot_efficiency(df, size, output_dir):
    """Plot efficiency vs number of threads for each method"""
    size_df = df[df['array_size'] == size]
    methods = ['builtin', 'atomic', 'critical', 'lock']
    
    # Get sequential baseline
    seq_time = size_df[size_df['method'] == 'sequential']['execution_time_ms'].values[0]
    
    plt.figure(figsize=(12, 8))
    
    for method in methods:
        method_df = size_df[size_df['method'] == method].sort_values('num_threads')
        if len(method_df) > 0:
            speedup = seq_time / method_df['execution_time_ms']
            efficiency = speedup / method_df['num_threads']
            plt.plot(method_df['num_threads'], efficiency, 
                    marker='o', linewidth=2, markersize=8, label=method.capitalize())
    
    # Plot ideal efficiency line (100%)
    threads = sorted(size_df['num_threads'].unique())
    plt.axhline(y=1.0, color='k', linestyle='--', linewidth=2, label='Ideal Efficiency', alpha=0.5)
    
    plt.xlabel('Number of Threads', fontsize=12)
    plt.ylabel('Efficiency', fontsize=12)
    plt.title(f'Efficiency vs Threads (Array Size: {size:,})', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log', base=2)
    
    plt.xticks(threads, [str(t) for t in threads])
    plt.ylim(0, 1.2)
    
    plt.tight_layout()
    output_file = output_dir / f'efficiency_size_{size}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created: {output_file}")
    plt.close()

def plot_method_comparison(df, output_dir):
    """Compare all methods across different array sizes and thread counts"""
    methods = ['builtin', 'atomic', 'critical', 'lock']
    sizes = sorted(df['array_size'].unique())
    
    fig, axes = plt.subplots(1, len(sizes), figsize=(6*len(sizes), 6))
    if len(sizes) == 1:
        axes = [axes]
    
    for idx, size in enumerate(sizes):
        ax = axes[idx]
        size_df = df[df['array_size'] == size]
        seq_time = size_df[size_df['method'] == 'sequential']['execution_time_ms'].values[0]
        
        for method in methods:
            method_df = size_df[size_df['method'] == method].sort_values('num_threads')
            if len(method_df) > 0:
                speedup = seq_time / method_df['execution_time_ms']
                ax.plot(method_df['num_threads'], speedup, 
                       marker='o', linewidth=2, markersize=6, label=method.capitalize())
        
        threads = sorted(size_df['num_threads'].unique())
        ax.plot(threads, threads, 'k--', linewidth=1.5, label='Ideal', alpha=0.5)
        
        ax.set_xlabel('Number of Threads', fontsize=11)
        ax.set_ylabel('Speedup', fontsize=11)
        ax.set_title(f'Array Size: {size:,}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log', base=2)
        ax.set_xticks(threads)
        ax.set_xticklabels([str(t) for t in threads])
    
    plt.suptitle('Method Comparison Across Array Sizes', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    output_file = output_dir / 'method_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created: {output_file}")
    plt.close()

def plot_overhead_analysis(df, output_dir):
    """Analyze synchronization overhead by comparing with builtin reduction"""
    sizes = sorted(df['array_size'].unique())
    methods = ['atomic', 'critical', 'lock']
    
    fig, axes = plt.subplots(1, len(sizes), figsize=(6*len(sizes), 6))
    if len(sizes) == 1:
        axes = [axes]
    
    for idx, size in enumerate(sizes):
        ax = axes[idx]
        size_df = df[df['array_size'] == size]
        
        builtin_df = size_df[size_df['method'] == 'builtin'].sort_values('num_threads')
        
        for method in methods:
            method_df = size_df[size_df['method'] == method].sort_values('num_threads')
            if len(method_df) > 0 and len(builtin_df) > 0:
                # Calculate overhead as ratio to builtin
                overhead = method_df['execution_time_ms'].values / builtin_df['execution_time_ms'].values
                ax.plot(method_df['num_threads'], overhead, 
                       marker='o', linewidth=2, markersize=6, label=method.capitalize())
        
        ax.axhline(y=1.0, color='k', linestyle='--', linewidth=1.5, label='Builtin (baseline)', alpha=0.5)
        
        ax.set_xlabel('Number of Threads', fontsize=11)
        ax.set_ylabel('Overhead (relative to builtin)', fontsize=11)
        ax.set_title(f'Array Size: {size:,}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        
        threads = sorted(size_df['num_threads'].unique())
        ax.set_xticks(threads)
        ax.set_xticklabels([str(t) for t in threads])
    
    plt.suptitle('Synchronization Overhead Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    output_file = output_dir / 'overhead_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created: {output_file}")
    plt.close()

def generate_summary_table(df, output_dir):
    """Generate a summary table of results"""
    sizes = sorted(df['array_size'].unique())
    methods = ['builtin', 'atomic', 'critical', 'lock']
    
    output_file = output_dir / 'summary_table.txt'
    
    with open(output_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("SUMMARY TABLE: Reduction Operations with Different Synchronization Methods\n")
        f.write("="*100 + "\n\n")
        
        for size in sizes:
            f.write(f"\nArray Size: {size:,}\n")
            f.write("-"*100 + "\n")
            
            size_df = df[df['array_size'] == size]
            seq_time = size_df[size_df['method'] == 'sequential']['execution_time_ms'].values[0]
            
            f.write(f"Sequential baseline: {seq_time:.3f} ms\n\n")
            
            # Header
            f.write(f"{'Method':<12} {'Threads':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12} {'vs Builtin':<15}\n")
            f.write("-"*100 + "\n")
            
            threads = sorted(size_df['num_threads'].unique())
            for thread_count in threads:
                thread_df = size_df[size_df['num_threads'] == thread_count]
                
                builtin_time = None
                builtin_row = thread_df[thread_df['method'] == 'builtin']
                if len(builtin_row) > 0:
                    builtin_time = builtin_row['execution_time_ms'].values[0]
                
                for method in methods:
                    method_row = thread_df[thread_df['method'] == method]
                    if len(method_row) == 0:
                        continue
                    
                    time_ms = method_row['execution_time_ms'].values[0]
                    speedup = seq_time / time_ms
                    efficiency = speedup / thread_count
                    
                    if builtin_time and method != 'builtin':
                        vs_builtin = f"{time_ms / builtin_time:.2f}x"
                    else:
                        vs_builtin = "baseline"
                    
                    f.write(f"{method:<12} {thread_count:<10} {time_ms:<15.3f} {speedup:<12.3f} {efficiency:<12.3f} {vs_builtin:<15}\n")
                
                f.write("\n")
            
            f.write("\n")
        
        f.write("="*100 + "\n")
    
    print(f"Created: {output_file}")

def main():
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    results_dir = project_root / 'results'
    graphs_dir = project_root / 'graphs'
    
    # Create graphs directory
    graphs_dir.mkdir(exist_ok=True)
    
    # Find latest results file
    csv_file = find_latest_results(results_dir)
    
    if csv_file is None:
        print("Error: No benchmark results found in results directory")
        print("Please run run_benchmarks.sh first")
        sys.exit(1)
    
    print(f"=== Task 7: Reduction Synchronization - Graph Generation ===\n")
    print(f"Using results file: {csv_file}\n")
    
    # Read data
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(df)} benchmark results\n")
    
    # Get unique array sizes
    sizes = sorted(df['array_size'].unique())
    
    print("Generating graphs...\n")
    
    # Generate graphs for each array size
    for size in sizes:
        print(f"Processing array size: {size:,}")
        plot_execution_time(df, size, graphs_dir)
        plot_speedup(df, size, graphs_dir)
        plot_efficiency(df, size, graphs_dir)
    
    # Generate comparison graphs
    print("\nGenerating comparison graphs...")
    plot_method_comparison(df, graphs_dir)
    plot_overhead_analysis(df, graphs_dir)
    
    # Generate summary table
    print("\nGenerating summary table...")
    generate_summary_table(df, graphs_dir)
    
    print("\n" + "="*80)
    print("Graph generation complete!")
    print(f"Graphs saved to: {graphs_dir}")
    print("="*80)

if __name__ == "__main__":
    main()