#!/usr/bin/env python3
"""
Graph generation script for Task 8: Vector Dot Products with OpenMP Sections
Creates performance visualization graphs
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from pathlib import Path

def find_latest_results(results_dir):
    """Find the most recent processed results file"""
    results_path = Path(results_dir)
    processed_files = list(results_path.glob('benchmark_*_processed.csv'))
    
    if not processed_files:
        print("Error: No processed results files found")
        print("Please run analyze.py first")
        return None
    
    # Get the most recent file
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)

def plot_graphs(csv_file, output_dir):
    """Generate performance graphs"""
    
    print(f"=== Generating graphs from {csv_file} ===\n")
    
    # Read processed results
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get unique configurations
    configs = df.groupby(['num_pairs', 'vector_size'])
    
    # 1. Execution time vs threads for each configuration
    for (pairs, size), group in configs:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        
        ax.plot(par_data['num_threads'], par_data['total_time_ms'], 
                'o-', linewidth=2, markersize=8, label='Total time')
        ax.plot(par_data['num_threads'], par_data['input_time_ms'], 
                's--', linewidth=1.5, markersize=6, label='Input time')
        ax.plot(par_data['num_threads'], par_data['computation_time_ms'], 
                '^--', linewidth=1.5, markersize=6, label='Computation time')
        
        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Execution Time (ms)', fontsize=12)
        ax.set_title(f'Execution Time vs Threads\n({pairs} pairs × {size} elements)', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        
        filename = f'{output_dir}/execution_time_{pairs}x{size}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {filename}")
    
    # 2. Speedup vs threads for each configuration
    for (pairs, size), group in configs:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        threads = par_data['num_threads'].values
        speedup = par_data['speedup'].values
        
        ax.plot(threads, speedup, 'o-', linewidth=2, markersize=8, 
                label='Actual speedup', color='blue')
        ax.plot(threads, threads, '--', linewidth=2, 
                label='Ideal speedup', color='red', alpha=0.5)
        
        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Speedup', fontsize=12)
        ax.set_title(f'Speedup vs Threads\n({pairs} pairs × {size} elements)', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log', base=2)
        
        filename = f'{output_dir}/speedup_{pairs}x{size}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {filename}")
    
    # 3. Efficiency vs threads for each configuration
    for (pairs, size), group in configs:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        threads = par_data['num_threads'].values
        efficiency = par_data['speedup'].values / threads
        
        ax.plot(threads, efficiency * 100, 'o-', linewidth=2, markersize=8, color='green')
        ax.axhline(y=100, color='red', linestyle='--', linewidth=2, 
                   label='Ideal efficiency (100%)', alpha=0.5)
        
        ax.set_xlabel('Number of Threads', fontsize=12)
        ax.set_ylabel('Efficiency (%)', fontsize=12)
        ax.set_title(f'Parallel Efficiency vs Threads\n({pairs} pairs × {size} elements)', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_ylim(0, 110)
        
        filename = f'{output_dir}/efficiency_{pairs}x{size}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Created: {filename}")
    
    # 4. Comparison across all configurations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 4a. Speedup comparison
    ax = axes[0, 0]
    for (pairs, size), group in configs:
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        ax.plot(par_data['num_threads'], par_data['speedup'], 
                'o-', linewidth=2, markersize=6, label=f'{pairs}×{size}')
    
    threads_range = df['num_threads'].unique()
    ax.plot(threads_range, threads_range, '--', linewidth=2, 
            label='Ideal', color='red', alpha=0.5)
    ax.set_xlabel('Number of Threads', fontsize=11)
    ax.set_ylabel('Speedup', fontsize=11)
    ax.set_title('Speedup Comparison', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)
    
    # 4b. Efficiency comparison
    ax = axes[0, 1]
    for (pairs, size), group in configs:
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        efficiency = (par_data['speedup'] / par_data['num_threads']) * 100
        ax.plot(par_data['num_threads'], efficiency, 
                'o-', linewidth=2, markersize=6, label=f'{pairs}×{size}')
    
    ax.axhline(y=100, color='red', linestyle='--', linewidth=2, alpha=0.5)
    ax.set_xlabel('Number of Threads', fontsize=11)
    ax.set_ylabel('Efficiency (%)', fontsize=11)
    ax.set_title('Efficiency Comparison', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_ylim(0, 110)
    
    # 4c. Input vs Computation time
    ax = axes[1, 0]
    for (pairs, size), group in configs:
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        input_ratio = (par_data['input_time_ms'] / par_data['total_time_ms']) * 100
        ax.plot(par_data['num_threads'], input_ratio, 
                'o-', linewidth=2, markersize=6, label=f'{pairs}×{size}')
    
    ax.set_xlabel('Number of Threads', fontsize=11)
    ax.set_ylabel('Input Time Ratio (%)', fontsize=11)
    ax.set_title('Input Time as % of Total', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    # 4d. Absolute performance
    ax = axes[1, 1]
    for (pairs, size), group in configs:
        par_data = group[group['method'] == 'sections'].sort_values('num_threads')
        ax.plot(par_data['num_threads'], par_data['total_time_ms'], 
                'o-', linewidth=2, markersize=6, label=f'{pairs}×{size}')
    
    ax.set_xlabel('Number of Threads', fontsize=11)
    ax.set_ylabel('Total Time (ms)', fontsize=11)
    ax.set_title('Absolute Performance', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_yscale('log')
    
    plt.tight_layout()
    filename = f'{output_dir}/comparison_all.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Created: {filename}")
    
    # 5. Summary table
    summary_file = f'{output_dir}/summary_table.txt'
    with open(summary_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("Task 8: Vector Dot Products with OpenMP Sections - Performance Summary\n")
        f.write("="*100 + "\n\n")
        
        for (pairs, size), group in configs:
            f.write(f"\nConfiguration: {pairs} pairs × {size} elements\n")
            f.write("-"*100 + "\n")
            f.write(f"{'Threads':<10} {'Total(ms)':<15} {'Input(ms)':<15} {'Compute(ms)':<15} {'Speedup':<12} {'Efficiency':<12}\n")
            f.write("-"*100 + "\n")
            
            par_data = group[group['method'] == 'sections'].sort_values('num_threads')
            for _, row in par_data.iterrows():
                efficiency = (row['speedup'] / row['num_threads']) * 100
                f.write(f"{row['num_threads']:<10} {row['total_time_ms']:<15.3f} "
                       f"{row['input_time_ms']:<15.3f} {row['computation_time_ms']:<15.3f} "
                       f"{row['speedup']:<12.3f} {efficiency:<12.1f}%\n")
            
            best_idx = par_data['speedup'].idxmax()
            best = par_data.loc[best_idx]
            f.write(f"\nBest: {best['num_threads']} threads, "
                   f"Speedup: {best['speedup']:.3f}x, "
                   f"Efficiency: {(best['speedup']/best['num_threads'])*100:.1f}%\n")
    
    print(f"✓ Created: {summary_file}")
    print(f"\n✓ All graphs generated successfully in {output_dir}/")

if __name__ == "__main__":
    # Determine script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    results_dir = project_root / 'results'
    graphs_dir = project_root / 'graphs'
    
    # Find latest processed results
    csv_file = find_latest_results(results_dir)
    
    if csv_file is None:
        sys.exit(1)
    
    print(f"Using results file: {csv_file}\n")
    plot_graphs(csv_file, str(graphs_dir))