#!/usr/bin/env python3
"""
Graph generation script for dot product benchmark results
Creates comprehensive performance visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from pathlib import Path
import glob

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def find_latest_processed_file():
    """Find the most recent processed CSV file"""
    results_dir = Path(__file__).parent.parent / 'results'
    processed_files = list(results_dir.glob('*_processed.csv'))
    
    if not processed_files:
        print("✗ No processed CSV files found in results/")
        print("  Run analyze.py first to process benchmark data")
        sys.exit(1)
    
    # Sort by modification time and get the latest
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
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
    sizes = sorted(df['vector_size'].unique())
    
    for size in sizes:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        size_data = df[df['vector_size'] == size]
        
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            
            ax.plot(method_data['num_threads'], method_data['mean'], 
                   marker='o', linewidth=2, markersize=8, label=method)
            
            # Add error bars
            ax.errorbar(method_data['num_threads'], method_data['mean'],
                       yerr=method_data['std'], fmt='none', alpha=0.3, capsize=5)
        
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title(f'Execution Time vs Threads (Vector Size: {size:,})', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        
        filename = output_dir / f'execution_time_size_{size}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {filename}")
        plt.close()

def plot_speedup(df, output_dir):
    """Plot speedup vs number of threads with ideal line"""
    sizes = sorted(df['vector_size'].unique())
    
    for size in sizes:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        size_data = df[df['vector_size'] == size]
        
        # Plot ideal speedup line
        max_threads = size_data['num_threads'].max()
        ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
        ideal_threads = ideal_threads[ideal_threads <= max_threads]
        ax.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
               label='Ideal (Linear)', alpha=0.7)
        
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            
            ax.plot(method_data['num_threads'], method_data['speedup'], 
                   marker='o', linewidth=2, markersize=8, label=method)
        
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Speedup', fontsize=12, fontweight='bold')
        ax.set_title(f'Speedup vs Threads (Vector Size: {size:,})', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log', base=2)
        
        filename = output_dir / f'speedup_size_{size}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {filename}")
        plt.close()

def plot_efficiency(df, output_dir):
    """Plot parallel efficiency vs number of threads"""
    sizes = sorted(df['vector_size'].unique())
    
    for size in sizes:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        size_data = df[df['vector_size'] == size]
        
        # Plot ideal efficiency line (100%)
        max_threads = size_data['num_threads'].max()
        ax.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                  label='Ideal (100%)', alpha=0.7)
        
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            
            ax.plot(method_data['num_threads'], method_data['efficiency'], 
                   marker='o', linewidth=2, markersize=8, label=method)
        
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Efficiency', fontsize=12, fontweight='bold')
        ax.set_title(f'Parallel Efficiency vs Threads (Vector Size: {size:,})', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_ylim(0, 1.2)
        
        filename = output_dir / f'efficiency_size_{size}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {filename}")
        plt.close()

def plot_method_comparison(df, output_dir):
    """Compare methods across all configurations"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Method Comparison: Reduction vs No-Reduction', 
                fontsize=16, fontweight='bold')
    
    sizes = sorted(df['vector_size'].unique())
    
    # Plot 1: Speedup comparison
    ax = axes[0, 0]
    for size in sizes:
        size_data = df[df['vector_size'] == size]
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            label = f'{method} (size={size:,})'
            ax.plot(method_data['num_threads'], method_data['speedup'], 
                   marker='o', linewidth=2, label=label)
    
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Speedup', fontweight='bold')
    ax.set_title('Speedup Comparison', fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    # Plot 2: Efficiency comparison
    ax = axes[0, 1]
    for size in sizes:
        size_data = df[df['vector_size'] == size]
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            label = f'{method} (size={size:,})'
            ax.plot(method_data['num_threads'], method_data['efficiency'], 
                   marker='o', linewidth=2, label=label)
    
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Efficiency', fontweight='bold')
    ax.set_title('Efficiency Comparison', fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    # Plot 3: Execution time comparison
    ax = axes[1, 0]
    for size in sizes:
        size_data = df[df['vector_size'] == size]
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            label = f'{method} (size={size:,})'
            ax.plot(method_data['num_threads'], method_data['mean'], 
                   marker='o', linewidth=2, label=label)
    
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontweight='bold')
    ax.set_title('Execution Time Comparison', fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_yscale('log')
    
    # Plot 4: Best speedup by size
    ax = axes[1, 1]
    best_speedups = []
    for size in sizes:
        size_data = df[df['vector_size'] == size]
        for method in sorted(size_data['method'].unique()):
            method_data = size_data[size_data['method'] == method]
            best_speedup = method_data['speedup'].max()
            best_threads = method_data.loc[method_data['speedup'].idxmax(), 'num_threads']
            best_speedups.append({
                'size': size,
                'method': method,
                'speedup': best_speedup,
                'threads': best_threads
            })
    
    best_df = pd.DataFrame(best_speedups)
    x = np.arange(len(sizes))
    width = 0.35
    
    for i, method in enumerate(sorted(best_df['method'].unique())):
        method_best = best_df[best_df['method'] == method]
        offset = width * (i - 0.5)
        bars = ax.bar(x + offset, method_best['speedup'], width, label=method)
        
        # Add thread count labels on bars
        for j, (idx, row) in enumerate(method_best.iterrows()):
            ax.text(x[j] + offset, row['speedup'], f"{int(row['threads'])}t",
                   ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('Vector Size', fontweight='bold')
    ax.set_ylabel('Best Speedup', fontweight='bold')
    ax.set_title('Best Speedup by Vector Size', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{s:,}' for s in sizes], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    filename = output_dir / 'comparison_methods.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {filename}")
    plt.close()

def create_summary_table(df, output_dir):
    """Create a text summary table"""
    filename = output_dir / 'summary_table.txt'
    
    with open(filename, 'w') as f:
        f.write("="*100 + "\n")
        f.write("DOT PRODUCT BENCHMARK SUMMARY TABLE\n")
        f.write("="*100 + "\n\n")
        
        for size in sorted(df['vector_size'].unique()):
            f.write(f"\nVector Size: {size:,} elements\n")
            f.write("-"*100 + "\n")
            
            size_data = df[df['vector_size'] == size]
            
            for method in sorted(size_data['method'].unique()):
                method_data = size_data[size_data['method'] == method].sort_values('num_threads')
                
                f.write(f"\nMethod: {method}\n")
                f.write(f"{'Threads':<10} {'Time(ms)':<15} {'Speedup':<12} {'Efficiency':<12} {'StdDev':<12}\n")
                f.write("-"*100 + "\n")
                
                for _, row in method_data.iterrows():
                    f.write(f"{int(row['num_threads']):<10} "
                           f"{row['mean']:<15.6f} "
                           f"{row['speedup']:<12.4f} "
                           f"{row['efficiency']:<12.4f} "
                           f"{row['std']:<12.6f}\n")
                
                best_idx = method_data['speedup'].idxmax()
                best = method_data.loc[best_idx]
                f.write(f"\n  → Best: {best['speedup']:.4f}x speedup at {int(best['num_threads'])} threads "
                       f"(efficiency: {best['efficiency']:.4f})\n")
            
            f.write("\n")
    
    print(f"  ✓ Saved: {filename}")

def main():
    print("="*80)
    print("DOT PRODUCT BENCHMARK GRAPH GENERATION")
    print("="*80)
    print()
    
    # Find latest processed file
    csv_file = find_latest_processed_file()
    print(f"Using file: {csv_file}")
    print()
    
    # Load data
    df = load_data(csv_file)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'graphs'
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()
    
    # Generate plots
    print("Generating graphs...")
    print("\n1. Execution Time plots:")
    plot_execution_time(df, output_dir)
    
    print("\n2. Speedup plots:")
    plot_speedup(df, output_dir)
    
    print("\n3. Efficiency plots:")
    plot_efficiency(df, output_dir)
    
    print("\n4. Method comparison plot:")
    plot_method_comparison(df, output_dir)
    
    print("\n5. Summary table:")
    create_summary_table(df, output_dir)
    
    print("\n" + "="*80)
    print("GRAPH GENERATION COMPLETE")
    print("="*80)
    print(f"\nAll graphs saved to: {output_dir}")
    print("\nGenerated files:")
    for f in sorted(output_dir.glob('*.png')):
        print(f"  - {f.name}")
    print(f"  - summary_table.txt")
    print()

if __name__ == "__main__":
    main()