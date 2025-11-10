#!/usr/bin/env python3
"""
Graph generation script for Task 9: Nested Parallelism
Creates visualization of flat vs nested parallelism performance
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from pathlib import Path

def find_latest_processed_csv(results_dir):
    """Find the most recent processed CSV file"""
    csv_files = list(Path(results_dir).glob("*_processed.csv"))
    if not csv_files:
        return None
    return max(csv_files, key=os.path.getctime)

def plot_graphs(csv_file, output_dir):
    """Generate all graphs from processed results"""
    
    print("=" * 60)
    print("Task 9: Nested Parallelism - Graph Generation")
    print("=" * 60)
    print(f"\nReading data from: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    colors = {'sequential': 'gray', 'flat': 'blue', 'nested': 'red'}
    
    sizes = sorted(df['N'].unique())
    
    # 1. Execution time comparison for each size
    for size in sizes:
        size_data = df[df['N'] == size]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        for method in ['flat', 'nested']:
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            if not method_data.empty:
                ax.plot(method_data['num_threads'], method_data['mean_time'],
                       marker='o', label=method.capitalize(), color=colors[method],
                       linewidth=2, markersize=8)
        
        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Execution Time (ms)', fontsize=12)
        ax.set_title(f'Execution Time vs Threads (Matrix {size}x{size})', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        
        filename = f"{output_dir}/execution_time_size_{size}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {filename}")
    
    # 2. Speedup comparison for each size
    for size in sizes:
        size_data = df[df['N'] == size]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Plot ideal speedup
        max_threads = size_data['num_threads'].max()
        ideal_threads = [1, 2, 4, 8, 16, 32, 64, 128]
        ideal_threads = [t for t in ideal_threads if t <= max_threads]
        ax.plot(ideal_threads, ideal_threads, 'k--', label='Ideal', linewidth=2, alpha=0.5)
        
        for method in ['flat', 'nested']:
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            if not method_data.empty:
                ax.plot(method_data['num_threads'], method_data['speedup'],
                       marker='o', label=method.capitalize(), color=colors[method],
                       linewidth=2, markersize=8)
        
        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Speedup', fontsize=12)
        ax.set_title(f'Speedup vs Threads (Matrix {size}x{size})', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        
        filename = f"{output_dir}/speedup_size_{size}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {filename}")
    
    # 3. Efficiency comparison for each size
    for size in sizes:
        size_data = df[df['N'] == size]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Plot ideal efficiency (100%)
        max_threads = size_data['num_threads'].max()
        ax.axhline(y=1.0, color='k', linestyle='--', label='Ideal (100%)', linewidth=2, alpha=0.5)
        
        for method in ['flat', 'nested']:
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            if not method_data.empty:
                ax.plot(method_data['num_threads'], method_data['efficiency'],
                       marker='o', label=method.capitalize(), color=colors[method],
                       linewidth=2, markersize=8)
        
        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Efficiency', fontsize=12)
        ax.set_title(f'Efficiency vs Threads (Matrix {size}x{size})', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_ylim(0, 1.2)
        
        filename = f"{output_dir}/efficiency_size_{size}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {filename}")
    
    # 4. Comparison: Flat vs Nested (all sizes)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, size in enumerate(sizes):
        ax = axes[idx]
        size_data = df[df['N'] == size]
        
        threads = []
        flat_times = []
        nested_times = []
        
        for t in sorted(size_data['num_threads'].unique()):
            if t == 1:
                continue
            
            flat = size_data[(size_data['method'] == 'flat') & (size_data['num_threads'] == t)]
            nested = size_data[(size_data['method'] == 'nested') & (size_data['num_threads'] == t)]
            
            if not flat.empty and not nested.empty:
                threads.append(t)
                flat_times.append(flat['mean_time'].values[0])
                nested_times.append(nested['mean_time'].values[0])
        
        x = np.arange(len(threads))
        width = 0.35
        
        ax.bar(x - width/2, flat_times, width, label='Flat', color=colors['flat'], alpha=0.8)
        ax.bar(x + width/2, nested_times, width, label='Nested', color=colors['nested'], alpha=0.8)
        
        ax.set_xlabel('Number of Threads', fontsize=11)
        ax.set_ylabel('Execution Time (ms)', fontsize=11)
        ax.set_title(f'Matrix {size}x{size}', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(threads)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Flat vs Nested Parallelism Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    filename = f"{output_dir}/comparison_flat_vs_nested.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: {filename}")
    
    # 5. Speedup comparison across sizes
    fig, ax = plt.subplots(figsize=(14, 8))
    
    markers = ['o', 's', '^']
    for idx, size in enumerate(sizes):
        size_data = df[df['N'] == size]
        
        for method in ['flat', 'nested']:
            method_data = size_data[size_data['method'] == method].sort_values('num_threads')
            if not method_data.empty:
                label = f'{method.capitalize()} ({size}x{size})'
                linestyle = '-' if method == 'flat' else '--'
                ax.plot(method_data['num_threads'], method_data['speedup'],
                       marker=markers[idx], label=label, linestyle=linestyle,
                       linewidth=2, markersize=8)
    
    # Ideal line
    max_threads = df['num_threads'].max()
    ideal_threads = [1, 2, 4, 8, 16, 32, 64, 128]
    ideal_threads = [t for t in ideal_threads if t <= max_threads]
    ax.plot(ideal_threads, ideal_threads, 'k--', label='Ideal', linewidth=2, alpha=0.5)
    
    ax.set_xlabel('Number of Threads', fontsize=12)
    ax.set_ylabel('Speedup', fontsize=12)
    ax.set_title('Speedup Comparison: Flat vs Nested Parallelism', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    filename = f"{output_dir}/speedup_comparison_all.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: {filename}")
    
    # 6. Create summary table
    summary_file = f"{output_dir}/summary_table.txt"
    with open(summary_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("Task 9: Nested Parallelism - Summary Table\n")
        f.write("=" * 80 + "\n\n")
        
        for size in sizes:
            size_data = df[df['N'] == size]
            
            f.write(f"\nMatrix Size: {size}x{size}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Method':<10} {'Threads':<10} {'Config':<15} {'Time (ms)':<12} {'Speedup':<10} {'Efficiency':<12}\n")
            f.write("-" * 80 + "\n")
            
            for _, row in size_data.sort_values(['method', 'num_threads']).iterrows():
                if row['method'] == 'sequential':
                    config = '-'
                elif row['method'] == 'flat':
                    config = f"{int(row['num_threads'])}"
                else:  # nested
                    config = f"{int(row['outer_threads'])}x{int(row['inner_threads'])}"
                
                f.write(f"{row['method']:<10} {int(row['num_threads']):<10} {config:<15} "
                       f"{row['mean_time']:<12.3f} {row['speedup']:<10.2f} {row['efficiency']:<12.2%}\n")
            
            f.write("\n")
    
    print(f"✓ Created: {summary_file}")
    
    print("\n" + "=" * 60)
    print("Graph Generation Complete!")
    print("=" * 60)
    print(f"\nAll graphs saved to: {output_dir}/")
    print("\nGenerated files:")
    print("  - execution_time_size_*.png")
    print("  - speedup_size_*.png")
    print("  - efficiency_size_*.png")
    print("  - comparison_flat_vs_nested.png")
    print("  - speedup_comparison_all.png")
    print("  - summary_table.txt")

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / "results"
    graphs_dir = script_dir.parent / "graphs"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = find_latest_processed_csv(results_dir)
        if csv_file is None:
            print("Error: No processed CSV file found in results directory")
            print("Usage: python3 plot_graphs.py [processed_results.csv]")
            sys.exit(1)
        print(f"Using latest processed file: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    plot_graphs(csv_file, str(graphs_dir))