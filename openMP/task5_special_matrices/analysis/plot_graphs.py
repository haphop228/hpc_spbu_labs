#!/usr/bin/env python3
"""
Graph generation script for Task 5: Special Matrices benchmarks
Creates visualization of performance metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def find_latest_processed_file():
    """Find the most recent processed CSV file"""
    results_dir = Path('../results')
    processed_files = list(results_dir.glob('*_processed.csv'))
    
    if not processed_files:
        print("✗ No processed CSV files found in ../results/")
        print("  Run analyze.py first to process benchmark results")
        sys.exit(1)
    
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    return str(latest_file)

def load_data(csv_file=None):
    """Load processed benchmark data"""
    if csv_file is None:
        csv_file = find_latest_processed_file()
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} records from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        sys.exit(1)

def plot_execution_time_by_schedule(df, output_dir):
    """Plot execution time vs threads for different schedules"""
    for size in sorted(df['N'].unique()):
        for matrix_type in sorted(df['matrix_type'].unique()):
            subset = df[
                (df['N'] == size) & 
                (df['matrix_type'] == matrix_type) &
                (df['chunk_size'] == 0)  # Use default chunk size
            ]
            
            if len(subset) == 0:
                continue
            
            plt.figure(figsize=(12, 8))
            
            for schedule in sorted(subset['schedule'].unique()):
                schedule_data = subset[subset['schedule'] == schedule].sort_values('num_threads')
                plt.plot(schedule_data['num_threads'], schedule_data['time_mean'], 
                        marker='o', linewidth=2, markersize=8, label=schedule.upper())
            
            plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
            plt.ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
            plt.title(f'Execution Time vs Threads\nMatrix: {size}x{size} {matrix_type.upper()}', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log', base=2)
            plt.yscale('log')
            
            filename = f'execution_time_{matrix_type}_size_{size}.png'
            plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Created {filename}")

def plot_speedup_by_schedule(df, output_dir):
    """Plot speedup vs threads for different schedules"""
    for size in sorted(df['N'].unique()):
        for matrix_type in sorted(df['matrix_type'].unique()):
            subset = df[
                (df['N'] == size) & 
                (df['matrix_type'] == matrix_type) &
                (df['chunk_size'] == 0)
            ]
            
            if len(subset) == 0:
                continue
            
            plt.figure(figsize=(12, 8))
            
            # Plot ideal speedup
            max_threads = subset['num_threads'].max()
            ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
            ideal_threads = ideal_threads[ideal_threads <= max_threads]
            plt.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, label='Ideal', alpha=0.5)
            
            for schedule in sorted(subset['schedule'].unique()):
                schedule_data = subset[subset['schedule'] == schedule].sort_values('num_threads')
                plt.plot(schedule_data['num_threads'], schedule_data['speedup'], 
                        marker='o', linewidth=2, markersize=8, label=schedule.upper())
            
            plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
            plt.ylabel('Speedup', fontsize=12, fontweight='bold')
            plt.title(f'Speedup vs Threads\nMatrix: {size}x{size} {matrix_type.upper()}', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log', base=2)
            plt.yscale('log', base=2)
            
            filename = f'speedup_{matrix_type}_size_{size}.png'
            plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Created {filename}")

def plot_efficiency_by_schedule(df, output_dir):
    """Plot efficiency vs threads for different schedules"""
    for size in sorted(df['N'].unique()):
        for matrix_type in sorted(df['matrix_type'].unique()):
            subset = df[
                (df['N'] == size) & 
                (df['matrix_type'] == matrix_type) &
                (df['chunk_size'] == 0)
            ]
            
            if len(subset) == 0:
                continue
            
            plt.figure(figsize=(12, 8))
            
            # Plot ideal efficiency (100%)
            plt.axhline(y=1.0, color='k', linestyle='--', linewidth=2, label='Ideal', alpha=0.5)
            
            for schedule in sorted(subset['schedule'].unique()):
                schedule_data = subset[subset['schedule'] == schedule].sort_values('num_threads')
                plt.plot(schedule_data['num_threads'], schedule_data['efficiency'], 
                        marker='o', linewidth=2, markersize=8, label=schedule.upper())
            
            plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
            plt.ylabel('Efficiency', fontsize=12, fontweight='bold')
            plt.title(f'Efficiency vs Threads\nMatrix: {size}x{size} {matrix_type.upper()}', 
                     fontsize=14, fontweight='bold')
            plt.legend(fontsize=11)
            plt.grid(True, alpha=0.3)
            plt.xscale('log', base=2)
            plt.ylim(0, 1.1)
            
            filename = f'efficiency_{matrix_type}_size_{size}.png'
            plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Created {filename}")

def plot_schedule_comparison(df, output_dir):
    """Compare scheduling strategies across matrix types"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Scheduling Strategy Comparison\n(16 threads, default chunk size)', 
                 fontsize=16, fontweight='bold')
    
    # Select data for 16 threads
    subset = df[(df['num_threads'] == 16) & (df['chunk_size'] == 0)]
    
    if len(subset) == 0:
        print("  ⚠ No data for 16 threads, skipping schedule comparison")
        plt.close()
        return
    
    matrix_types = sorted(subset['matrix_type'].unique())
    schedules = sorted(subset['schedule'].unique())
    
    # Plot 1: Execution time by matrix type
    ax = axes[0, 0]
    x = np.arange(len(matrix_types))
    width = 0.25
    for i, schedule in enumerate(schedules):
        times = [subset[(subset['matrix_type'] == mt) & (subset['schedule'] == schedule)]['time_mean'].mean() 
                for mt in matrix_types]
        ax.bar(x + i*width, times, width, label=schedule.upper())
    ax.set_xlabel('Matrix Type', fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontweight='bold')
    ax.set_title('Execution Time by Matrix Type')
    ax.set_xticks(x + width)
    ax.set_xticklabels([mt.upper() for mt in matrix_types])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Speedup by matrix type
    ax = axes[0, 1]
    for i, schedule in enumerate(schedules):
        speedups = [subset[(subset['matrix_type'] == mt) & (subset['schedule'] == schedule)]['speedup'].mean() 
                   for mt in matrix_types]
        ax.bar(x + i*width, speedups, width, label=schedule.upper())
    ax.set_xlabel('Matrix Type', fontweight='bold')
    ax.set_ylabel('Speedup', fontweight='bold')
    ax.set_title('Speedup by Matrix Type')
    ax.set_xticks(x + width)
    ax.set_xticklabels([mt.upper() for mt in matrix_types])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Efficiency by matrix type
    ax = axes[1, 0]
    for i, schedule in enumerate(schedules):
        efficiencies = [subset[(subset['matrix_type'] == mt) & (subset['schedule'] == schedule)]['efficiency'].mean() 
                       for mt in matrix_types]
        ax.bar(x + i*width, efficiencies, width, label=schedule.upper())
    ax.set_xlabel('Matrix Type', fontweight='bold')
    ax.set_ylabel('Efficiency', fontweight='bold')
    ax.set_title('Efficiency by Matrix Type')
    ax.set_xticks(x + width)
    ax.set_xticklabels([mt.upper() for mt in matrix_types])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.1)
    
    # Plot 4: Schedule performance across sizes
    ax = axes[1, 1]
    sizes = sorted(subset['N'].unique())
    for schedule in schedules:
        times = [subset[(subset['N'] == size) & (subset['schedule'] == schedule)]['time_mean'].mean() 
                for size in sizes]
        ax.plot(sizes, times, marker='o', linewidth=2, markersize=8, label=schedule.upper())
    ax.set_xlabel('Matrix Size', fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontweight='bold')
    ax.set_title('Performance vs Matrix Size')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    plt.tight_layout()
    filename = 'schedule_comparison.png'
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Created {filename}")

def plot_matrix_type_comparison(df, output_dir):
    """Compare different matrix types"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Matrix Type Comparison\n(Static schedule, default chunk size)', 
                 fontsize=16, fontweight='bold')
    
    # Use static schedule with default chunk
    subset = df[(df['schedule'] == 'static') & (df['chunk_size'] == 0)]
    
    if len(subset) == 0:
        print("  ⚠ No data for static schedule, skipping matrix type comparison")
        plt.close()
        return
    
    matrix_types = sorted(subset['matrix_type'].unique())
    
    # Plot 1: Execution time vs threads
    ax = axes[0]
    for matrix_type in matrix_types:
        mt_data = subset[subset['matrix_type'] == matrix_type].sort_values('num_threads')
        ax.plot(mt_data['num_threads'], mt_data['time_mean'], 
               marker='o', linewidth=2, markersize=8, label=matrix_type.upper())
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Execution Time (ms)', fontweight='bold')
    ax.set_title('Execution Time vs Threads')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_yscale('log')
    
    # Plot 2: Speedup vs threads
    ax = axes[1]
    max_threads = subset['num_threads'].max()
    ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
    ideal_threads = ideal_threads[ideal_threads <= max_threads]
    ax.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, label='Ideal', alpha=0.5)
    
    for matrix_type in matrix_types:
        mt_data = subset[subset['matrix_type'] == matrix_type].sort_values('num_threads')
        ax.plot(mt_data['num_threads'], mt_data['speedup'], 
               marker='o', linewidth=2, markersize=8, label=matrix_type.upper())
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Speedup', fontweight='bold')
    ax.set_title('Speedup vs Threads')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)
    
    # Plot 3: Efficiency vs threads
    ax = axes[2]
    ax.axhline(y=1.0, color='k', linestyle='--', linewidth=2, label='Ideal', alpha=0.5)
    
    for matrix_type in matrix_types:
        mt_data = subset[subset['matrix_type'] == matrix_type].sort_values('num_threads')
        ax.plot(mt_data['num_threads'], mt_data['efficiency'], 
               marker='o', linewidth=2, markersize=8, label=matrix_type.upper())
    ax.set_xlabel('Number of Threads', fontweight='bold')
    ax.set_ylabel('Efficiency', fontweight='bold')
    ax.set_title('Efficiency vs Threads')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    filename = 'matrix_type_comparison.png'
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Created {filename}")

def main():
    print("="*80)
    print("SPECIAL MATRICES - GRAPH GENERATION")
    print("="*80)
    
    # Load data
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    df = load_data(csv_file)
    
    # Create output directory
    output_dir = '../graphs'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nGenerating graphs...")
    
    # Generate plots
    print("\n1. Execution time plots...")
    plot_execution_time_by_schedule(df, output_dir)
    
    print("\n2. Speedup plots...")
    plot_speedup_by_schedule(df, output_dir)
    
    print("\n3. Efficiency plots...")
    plot_efficiency_by_schedule(df, output_dir)
    
    print("\n4. Schedule comparison...")
    plot_schedule_comparison(df, output_dir)
    
    print("\n5. Matrix type comparison...")
    plot_matrix_type_comparison(df, output_dir)
    
    print("\n" + "="*80)
    print("GRAPH GENERATION COMPLETE")
    print("="*80)
    print(f"\nGraphs saved to: {output_dir}/")
    print("\nGenerated files:")
    for file in sorted(os.listdir(output_dir)):
        if file.endswith('.png'):
            print(f"  - {file}")

if __name__ == '__main__':
    main()