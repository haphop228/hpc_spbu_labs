#!/usr/bin/env python3
"""
Graph generation script for Task 3: Numerical Integration
Creates performance visualization graphs for single method (reduction)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pathlib import Path
import glob

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def find_latest_processed_file():
    """Find the most recent processed CSV file"""
    results_dir = '../results'
    pattern = os.path.join(results_dir, '*_processed.csv')
    files = glob.glob(pattern)
    
    if not files:
        print("✗ No processed CSV files found in ../results/")
        print("  Run analyze.py first to process benchmark results")
        sys.exit(1)
    
    latest_file = max(files, key=os.path.getctime)
    return latest_file

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
    """Plot execution time vs number of threads"""
    for func in df['function'].unique():
        for size in df['N'].unique():
            subset = df[(df['function'] == func) & (df['N'] == size)]
            
            plt.figure(figsize=(12, 8))
            
            # Plot reduction method
            method_data = subset[subset['method'] == 'reduction'].sort_values('num_threads')
            plt.plot(method_data['num_threads'], method_data['time_mean'], 
                    marker='o', linewidth=2, markersize=8, label='OpenMP Reduction', color='#2E86AB')
            
            plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
            plt.ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
            plt.title(f'Execution Time vs Threads\nFunction: {func}, N={size:,}', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log', base=2)
            plt.yscale('log')
            
            filename = f'execution_time_{func}_size_{size}.png'
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ {filename}")

def plot_speedup(df, output_dir):
    """Plot speedup vs number of threads with ideal line"""
    for func in df['function'].unique():
        for size in df['N'].unique():
            subset = df[(df['function'] == func) & (df['N'] == size)]
            
            plt.figure(figsize=(12, 8))
            
            # Plot ideal speedup
            max_threads = subset['num_threads'].max()
            ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
            ideal_threads = ideal_threads[ideal_threads <= max_threads]
            plt.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
                    label='Ideal Speedup', alpha=0.7)
            
            # Plot reduction method
            method_data = subset[subset['method'] == 'reduction'].sort_values('num_threads')
            plt.plot(method_data['num_threads'], method_data['speedup'], 
                    marker='o', linewidth=2, markersize=8, label='OpenMP Reduction', color='#2E86AB')
            
            plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
            plt.ylabel('Speedup', fontsize=12, fontweight='bold')
            plt.title(f'Speedup vs Threads\nFunction: {func}, N={size:,}', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log', base=2)
            plt.yscale('log', base=2)
            
            filename = f'speedup_{func}_size_{size}.png'
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ {filename}")

def plot_efficiency(df, output_dir):
    """Plot efficiency vs number of threads"""
    for func in df['function'].unique():
        for size in df['N'].unique():
            subset = df[(df['function'] == func) & (df['N'] == size)]
            
            plt.figure(figsize=(12, 8))
            
            # Plot ideal efficiency (100%)
            plt.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                       label='Ideal Efficiency (100%)', alpha=0.7)
            
            # Plot reduction method
            method_data = subset[subset['method'] == 'reduction'].sort_values('num_threads')
            plt.plot(method_data['num_threads'], method_data['efficiency'], 
                    marker='o', linewidth=2, markersize=8, label='OpenMP Reduction', color='#2E86AB')
            
            plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
            plt.ylabel('Efficiency', fontsize=12, fontweight='bold')
            plt.title(f'Parallel Efficiency vs Threads\nFunction: {func}, N={size:,}', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log', base=2)
            plt.ylim(0, 1.1)
            
            filename = f'efficiency_{func}_size_{size}.png'
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ {filename}")

def plot_size_comparison(df, output_dir):
    """Compare performance across different problem sizes"""
    for func in df['function'].unique():
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Performance Analysis - Function: {func}', 
                    fontsize=16, fontweight='bold')
        
        sizes = sorted(df['N'].unique())
        thread_counts = [4, 8, 16, 32]
        
        # Speedup comparison
        ax = axes[0, 0]
        for size in sizes:
            subset = df[(df['function'] == func) & (df['N'] == size) & (df['method'] == 'reduction')]
            subset = subset.sort_values('num_threads')
            ax.plot(subset['num_threads'], subset['speedup'], 
                   marker='o', linewidth=2, markersize=8, label=f'N={size:,}')
        
        ax.set_xlabel('Number of Threads', fontsize=11, fontweight='bold')
        ax.set_ylabel('Speedup', fontsize=11, fontweight='bold')
        ax.set_title('Speedup vs Threads', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        
        # Efficiency comparison
        ax = axes[0, 1]
        for size in sizes:
            subset = df[(df['function'] == func) & (df['N'] == size) & (df['method'] == 'reduction')]
            subset = subset.sort_values('num_threads')
            ax.plot(subset['num_threads'], subset['efficiency'], 
                   marker='o', linewidth=2, markersize=8, label=f'N={size:,}')
        
        ax.axhline(y=1.0, color='k', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Number of Threads', fontsize=11, fontweight='bold')
        ax.set_ylabel('Efficiency', fontsize=11, fontweight='bold')
        ax.set_title('Efficiency vs Threads', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_ylim(0, 1.1)
        
        # Execution time comparison
        ax = axes[1, 0]
        for size in sizes:
            subset = df[(df['function'] == func) & (df['N'] == size) & (df['method'] == 'reduction')]
            subset = subset.sort_values('num_threads')
            ax.plot(subset['num_threads'], subset['time_mean'], 
                   marker='o', linewidth=2, markersize=8, label=f'N={size:,}')
        
        ax.set_xlabel('Number of Threads', fontsize=11, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=11, fontweight='bold')
        ax.set_title('Execution Time vs Threads', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        
        # Speedup at fixed thread counts
        ax = axes[1, 1]
        speedups_by_threads = []
        for threads in thread_counts:
            speedups = []
            for size in sizes:
                subset = df[(df['function'] == func) & 
                           (df['N'] == size) & 
                           (df['method'] == 'reduction') & 
                           (df['num_threads'] == threads)]
                if len(subset) > 0:
                    speedups.append(subset['speedup'].values[0])
                else:
                    speedups.append(0)
            speedups_by_threads.append(speedups)
        
        x = np.arange(len(sizes))
        width = 0.2
        for i, threads in enumerate(thread_counts):
            ax.bar(x + i * width, speedups_by_threads[i], width, 
                  label=f'{threads} threads')
        
        ax.set_xlabel('Problem Size', fontsize=11, fontweight='bold')
        ax.set_ylabel('Speedup', fontsize=11, fontweight='bold')
        ax.set_title('Speedup by Problem Size', fontsize=12, fontweight='bold')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels([f'{s:,}' for s in sizes], rotation=45)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filename = f'size_comparison_{func}.png'
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {filename}")

def plot_scalability_analysis(df, output_dir):
    """Analyze scalability across different problem sizes"""
    for func in df['function'].unique():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(f'Scalability Analysis - Function: {func}', 
                    fontsize=16, fontweight='bold')
        
        # Strong scaling (fixed problem size)
        for size in sorted(df['N'].unique()):
            subset = df[(df['function'] == func) & 
                       (df['N'] == size) & 
                       (df['method'] == 'reduction')]
            if len(subset) > 0:
                subset = subset.sort_values('num_threads')
                ax1.plot(subset['num_threads'], subset['speedup'], 
                        marker='o', linewidth=2, markersize=8, 
                        label=f'N={size:,}')
        
        # Ideal line
        max_threads = df['num_threads'].max()
        ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
        ideal_threads = ideal_threads[ideal_threads <= max_threads]
        ax1.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
                label='Ideal', alpha=0.7)
        
        ax1.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Speedup', fontsize=12, fontweight='bold')
        ax1.set_title('Strong Scaling', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xscale('log', base=2)
        ax1.set_yscale('log', base=2)
        
        # Efficiency comparison
        for size in sorted(df['N'].unique()):
            subset = df[(df['function'] == func) & 
                       (df['N'] == size) & 
                       (df['method'] == 'reduction')]
            if len(subset) > 0:
                subset = subset.sort_values('num_threads')
                ax2.plot(subset['num_threads'], subset['efficiency'], 
                        marker='o', linewidth=2, markersize=8, 
                        label=f'N={size:,}')
        
        ax2.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                   label='Ideal (100%)', alpha=0.7)
        ax2.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Efficiency', fontsize=12, fontweight='bold')
        ax2.set_title('Parallel Efficiency', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_xscale('log', base=2)
        ax2.set_ylim(0, 1.1)
        
        plt.tight_layout()
        filename = f'scalability_analysis_{func}.png'
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {filename}")

def main():
    print("="*80)
    print("NUMERICAL INTEGRATION - GRAPH GENERATION")
    print("="*80)
    
    # Find or use specified file
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        print("\nSearching for latest processed results...")
        csv_file = find_latest_processed_file()
    
    print(f"Using file: {csv_file}\n")
    
    # Load data
    df = load_data(csv_file)
    
    # Create output directory
    output_dir = '../graphs'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate graphs
    print("\nGenerating graphs...")
    print("\n1. Execution Time graphs:")
    plot_execution_time(df, output_dir)
    
    print("\n2. Speedup graphs:")
    plot_speedup(df, output_dir)
    
    print("\n3. Efficiency graphs:")
    plot_efficiency(df, output_dir)
    
    print("\n4. Size comparison graphs:")
    plot_size_comparison(df, output_dir)
    
    print("\n5. Scalability analysis:")
    plot_scalability_analysis(df, output_dir)
    
    print("\n" + "="*80)
    print("GRAPH GENERATION COMPLETE")
    print("="*80)
    print(f"\nGraphs saved to: {output_dir}/")
    print("\nGenerated graphs:")
    print("  - execution_time_*.png - Execution time vs threads")
    print("  - speedup_*.png - Speedup vs threads (with ideal line)")
    print("  - efficiency_*.png - Parallel efficiency vs threads")
    print("  - size_comparison_*.png - Performance across problem sizes")
    print("  - scalability_analysis_*.png - Strong scaling analysis")

if __name__ == '__main__':
    main()
