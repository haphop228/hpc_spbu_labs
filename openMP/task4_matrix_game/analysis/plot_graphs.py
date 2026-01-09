#!/usr/bin/env python3
"""
Graph generation script for Task 4: Matrix Game (Maximin) benchmarks
Creates performance visualization graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

def find_latest_processed_file(results_dir='../results'):
    """Find the most recent processed CSV file"""
    processed_files = list(Path(results_dir).glob('*_processed.csv'))
    if not processed_files:
        print("✗ No processed CSV files found in results directory")
        print("  Run analyze.py first to process benchmark results")
        sys.exit(1)
    
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)

def load_data(csv_file):
    """Load processed benchmark data"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} records from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        sys.exit(1)

def plot_execution_time(df, output_dir):
    """Plot execution time vs threads for each size"""
    sizes = sorted(df['N'].unique())
    methods = sorted(df['method'].unique())
    
    for size in sizes:
        plt.figure(figsize=(12, 7))
        
        subset = df[df['N'] == size]
        
        method_data = subset.sort_values('num_threads')
        plt.plot(method_data['num_threads'], method_data['time_mean'],
                marker='o', linewidth=2, markersize=8, label='OpenMP Reduction', color='#2E86AB')
        
        plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
        plt.ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        plt.title(f'Execution Time vs Threads - Matrix Size {size}x{size}', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xscale('log', base=2)
        plt.yscale('log')
        
        output_file = os.path.join(output_dir, f'execution_time_size_{size}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def plot_speedup(df, output_dir):
    """Plot speedup vs threads for each size"""
    sizes = sorted(df['N'].unique())
    methods = sorted(df['method'].unique())
    
    for size in sizes:
        plt.figure(figsize=(12, 7))
        
        subset = df[df['N'] == size]
        
        # Plot ideal speedup
        max_threads = subset['num_threads'].max()
        ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
        ideal_threads = ideal_threads[ideal_threads <= max_threads]
        plt.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
                label='Ideal Speedup', alpha=0.5)
        
        method_data = subset.sort_values('num_threads')
        plt.plot(method_data['num_threads'], method_data['speedup'],
                marker='o', linewidth=2, markersize=8, label='OpenMP Reduction', color='#2E86AB')
        
        plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
        plt.ylabel('Speedup', fontsize=12, fontweight='bold')
        plt.title(f'Speedup vs Threads - Matrix Size {size}x{size}', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xscale('log', base=2)
        plt.yscale('log', base=2)
        
        output_file = os.path.join(output_dir, f'speedup_size_{size}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def plot_efficiency(df, output_dir):
    """Plot efficiency vs threads for each size"""
    sizes = sorted(df['N'].unique())
    methods = sorted(df['method'].unique())
    
    for size in sizes:
        plt.figure(figsize=(12, 7))
        
        subset = df[df['N'] == size]
        
        # Plot ideal efficiency (100%)
        plt.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                   label='Ideal Efficiency', alpha=0.5)
        
        method_data = subset.sort_values('num_threads')
        plt.plot(method_data['num_threads'], method_data['efficiency'],
                marker='o', linewidth=2, markersize=8, label='OpenMP Reduction', color='#2E86AB')
        
        plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
        plt.ylabel('Efficiency', fontsize=12, fontweight='bold')
        plt.title(f'Efficiency vs Threads - Matrix Size {size}x{size}', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xscale('log', base=2)
        plt.ylim(0, 1.1)
        
        output_file = os.path.join(output_dir, f'efficiency_size_{size}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def plot_size_comparison(df, output_dir):
    """Compare performance across different matrix sizes"""
    sizes = sorted(df['N'].unique())
    
    # Select a few thread counts for comparison
    thread_counts = [1, 4, 8, 16, 32]
    available_threads = sorted(df['num_threads'].unique())
    thread_counts = [t for t in thread_counts if t in available_threads]
    
    plt.figure(figsize=(14, 8))
    
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(thread_counts)))
    
    for i, threads in enumerate(thread_counts):
        times = []
        for size in sizes:
            subset = df[(df['N'] == size) & (df['num_threads'] == threads)]
            if len(subset) > 0:
                times.append(subset['time_mean'].values[0])
            else:
                times.append(np.nan)
        
        plt.plot(sizes, times, marker='o', linewidth=2, markersize=8,
                label=f'{threads} threads', color=colors[i])
    
    plt.xlabel('Matrix Size (N×N)', fontsize=12, fontweight='bold')
    plt.ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
    plt.title('Performance Scaling with Matrix Size',
             fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.xscale('log')
    
    output_file = os.path.join(output_dir, 'size_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file}")

def plot_scalability_analysis(df, output_dir):
    """Plot strong scaling analysis"""
    plt.figure(figsize=(12, 7))
    
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(df['N'].unique())))
    
    for idx, size in enumerate(sorted(df['N'].unique())):
        size_data = df[df['N'] == size].sort_values('num_threads')
        plt.plot(size_data['num_threads'], size_data['speedup'],
               marker='o', linewidth=2, markersize=8, label=f'{size}×{size}', color=colors[idx])
    
    # Ideal speedup
    max_threads = df['num_threads'].max()
    ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64])
    ideal_threads = ideal_threads[ideal_threads <= max_threads]
    plt.plot(ideal_threads, ideal_threads, 'k--', linewidth=2,
           label='Ideal Speedup', alpha=0.5)
    
    plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
    plt.ylabel('Speedup', fontsize=12, fontweight='bold')
    plt.title('Strong Scaling Analysis - OpenMP Reduction', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log', base=2)
    plt.yscale('log', base=2)
    
    output_file = os.path.join(output_dir, 'scalability_analysis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file}")

def main():
    print("="*80)
    print("MATRIX GAME (MAXIMIN) - GRAPH GENERATION")
    print("="*80)
    
    # Find or use specified processed file
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        print("\nSearching for latest processed results...")
        csv_file = find_latest_processed_file()
    
    if not os.path.exists(csv_file):
        print(f"✗ File not found: {csv_file}")
        sys.exit(1)
    
    print(f"Using file: {csv_file}\n")
    
    # Load data
    df = load_data(csv_file)
    
    # Create output directory
    output_dir = '../graphs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate graphs
    print("\nGenerating graphs...")
    print("-" * 80)
    
    plot_execution_time(df, output_dir)
    plot_speedup(df, output_dir)
    plot_efficiency(df, output_dir)
    plot_size_comparison(df, output_dir)
    plot_scalability_analysis(df, output_dir)
    
    print("-" * 80)
    print(f"\n✓ All graphs saved to: {output_dir}")
    
    print("\n" + "="*80)
    print("GRAPH GENERATION COMPLETE")
    print("="*80)
    print(f"\nGenerated graphs:")
    print(f"  - execution_time_size_*.png")
    print(f"  - speedup_size_*.png")
    print(f"  - efficiency_size_*.png")
    print(f"  - size_comparison.png")
    print(f"  - scalability_analysis.png")

if __name__ == '__main__':
    main()
