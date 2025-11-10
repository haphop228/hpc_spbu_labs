#!/usr/bin/env python3
"""
Graph generation script for Task 6: Loop Scheduling Investigation

Generates comprehensive visualizations comparing different OpenMP scheduling
strategies (static, dynamic, guided) with uneven workload.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def find_latest_processed_file():
    """Find the most recent processed CSV file"""
    results_dir = Path(__file__).parent.parent / 'results'
    processed_files = list(results_dir.glob('*_processed.csv'))
    
    if not processed_files:
        print("Error: No processed CSV files found in results/")
        print("Please run analyze.py first")
        sys.exit(1)
    
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    return latest_file

def load_data(csv_file):
    """Load processed benchmark data"""
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} processed results from {csv_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)

def plot_execution_time_vs_threads(df, output_dir):
    """Plot execution time vs number of threads for each schedule"""
    
    for iterations in sorted(df['num_iterations'].unique()):
        iter_data = df[df['num_iterations'] == iterations]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        schedules = ['static', 'dynamic', 'guided']
        colors = {'static': 'blue', 'dynamic': 'red', 'guided': 'green'}
        markers = {'static': 'o', 'dynamic': 's', 'guided': '^'}
        
        for schedule in schedules:
            # Use default chunk size (0) for main comparison
            sched_data = iter_data[
                (iter_data['schedule'] == schedule) & 
                (iter_data['chunk_size'] == 0)
            ].sort_values('num_threads')
            
            if len(sched_data) > 0:
                ax.plot(sched_data['num_threads'], sched_data['mean_time_ms'],
                       marker=markers[schedule], label=schedule.capitalize(),
                       color=colors[schedule], linewidth=2, markersize=8)
        
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title(f'Execution Time vs Threads ({iterations} iterations)\nUneven Workload Loop',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        
        output_file = output_dir / f'execution_time_iter_{iterations}.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def plot_speedup_vs_threads(df, output_dir):
    """Plot speedup vs number of threads with ideal speedup line"""
    
    for iterations in sorted(df['num_iterations'].unique()):
        iter_data = df[df['num_iterations'] == iterations]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        schedules = ['static', 'dynamic', 'guided']
        colors = {'static': 'blue', 'dynamic': 'red', 'guided': 'green'}
        markers = {'static': 'o', 'dynamic': 's', 'guided': '^'}
        
        max_threads = 0
        
        for schedule in schedules:
            # Use default chunk size (0)
            sched_data = iter_data[
                (iter_data['schedule'] == schedule) & 
                (iter_data['chunk_size'] == 0)
            ].sort_values('num_threads')
            
            if len(sched_data) > 0:
                ax.plot(sched_data['num_threads'], sched_data['speedup'],
                       marker=markers[schedule], label=schedule.capitalize(),
                       color=colors[schedule], linewidth=2, markersize=8)
                max_threads = max(max_threads, sched_data['num_threads'].max())
        
        # Plot ideal speedup line
        ideal_threads = np.array([1, 2, 4, 8, 16, 32, 64, 128])
        ideal_threads = ideal_threads[ideal_threads <= max_threads]
        ax.plot(ideal_threads, ideal_threads, 'k--', label='Ideal Speedup',
               linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Speedup', fontsize=12, fontweight='bold')
        ax.set_title(f'Speedup vs Threads ({iterations} iterations)\nUneven Workload Loop',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log', base=2)
        
        output_file = output_dir / f'speedup_iter_{iterations}.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def plot_efficiency_vs_threads(df, output_dir):
    """Plot efficiency vs number of threads"""
    
    for iterations in sorted(df['num_iterations'].unique()):
        iter_data = df[df['num_iterations'] == iterations]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        schedules = ['static', 'dynamic', 'guided']
        colors = {'static': 'blue', 'dynamic': 'red', 'guided': 'green'}
        markers = {'static': 'o', 'dynamic': 's', 'guided': '^'}
        
        for schedule in schedules:
            # Use default chunk size (0)
            sched_data = iter_data[
                (iter_data['schedule'] == schedule) & 
                (iter_data['chunk_size'] == 0)
            ].sort_values('num_threads')
            
            if len(sched_data) > 0:
                ax.plot(sched_data['num_threads'], sched_data['efficiency'] * 100,
                       marker=markers[schedule], label=schedule.capitalize(),
                       color=colors[schedule], linewidth=2, markersize=8)
        
        # Plot 100% efficiency line
        ax.axhline(y=100, color='k', linestyle='--', label='Ideal (100%)',
                  linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Efficiency (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'Efficiency vs Threads ({iterations} iterations)\nUneven Workload Loop',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)
        ax.set_ylim(0, 110)
        
        output_file = output_dir / f'efficiency_iter_{iterations}.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def plot_schedule_comparison(df, output_dir):
    """Compare all schedules at different thread counts"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Schedule Comparison Across Different Configurations',
                fontsize=16, fontweight='bold')
    
    iterations_list = sorted(df['num_iterations'].unique())
    
    for idx, iterations in enumerate(iterations_list[:4]):  # Max 4 subplots
        ax = axes[idx // 2, idx % 2]
        iter_data = df[
            (df['num_iterations'] == iterations) & 
            (df['chunk_size'] == 0)
        ]
        
        schedules = ['static', 'dynamic', 'guided']
        x = np.arange(len(iter_data['num_threads'].unique()))
        width = 0.25
        
        for i, schedule in enumerate(schedules):
            sched_data = iter_data[iter_data['schedule'] == schedule].sort_values('num_threads')
            if len(sched_data) > 0:
                ax.bar(x + i * width, sched_data['speedup'], width,
                      label=schedule.capitalize())
        
        ax.set_xlabel('Number of Threads', fontsize=11, fontweight='bold')
        ax.set_ylabel('Speedup', fontsize=11, fontweight='bold')
        ax.set_title(f'{iterations} iterations', fontsize=12, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels(sorted(iter_data['num_threads'].unique()))
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    output_file = output_dir / 'schedule_comparison.png'
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file}")

def plot_chunk_size_impact(df, output_dir):
    """Plot impact of chunk size on performance"""
    
    for iterations in sorted(df['num_iterations'].unique()):
        iter_data = df[df['num_iterations'] == iterations]
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle(f'Chunk Size Impact ({iterations} iterations)',
                    fontsize=14, fontweight='bold')
        
        schedules = ['static', 'dynamic', 'guided']
        
        for idx, schedule in enumerate(schedules):
            ax = axes[idx]
            sched_data = iter_data[iter_data['schedule'] == schedule]
            
            # Group by threads
            for threads in sorted(sched_data['num_threads'].unique()):
                thread_data = sched_data[sched_data['num_threads'] == threads].sort_values('chunk_size')
                
                if len(thread_data) > 1:  # Only plot if multiple chunk sizes
                    chunk_labels = ['default' if c == 0 else str(int(c)) 
                                  for c in thread_data['chunk_size']]
                    ax.plot(range(len(thread_data)), thread_data['speedup'],
                           marker='o', label=f'{threads} threads', linewidth=2)
            
            ax.set_xlabel('Chunk Size', fontsize=11, fontweight='bold')
            ax.set_ylabel('Speedup', fontsize=11, fontweight='bold')
            ax.set_title(f'{schedule.capitalize()} Schedule', fontsize=12, fontweight='bold')
            
            # Set x-axis labels
            if len(sched_data['chunk_size'].unique()) > 1:
                chunk_labels = ['default' if c == 0 else str(int(c)) 
                              for c in sorted(sched_data['chunk_size'].unique())]
                ax.set_xticks(range(len(chunk_labels)))
                ax.set_xticklabels(chunk_labels)
            
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
        
        output_file = output_dir / f'chunk_size_impact_iter_{iterations}.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: {output_file}")

def create_summary_table(df, output_dir):
    """Create a text summary table"""
    
    output_file = output_dir / 'summary_table.txt'
    
    with open(output_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("TASK 6: LOOP SCHEDULING INVESTIGATION - SUMMARY TABLE\n")
        f.write("="*100 + "\n\n")
        
        for iterations in sorted(df['num_iterations'].unique()):
            f.write(f"\n{'='*100}\n")
            f.write(f"ITERATIONS: {iterations}\n")
            f.write(f"{'='*100}\n\n")
            
            iter_data = df[df['num_iterations'] == iterations]
            
            for schedule in ['static', 'dynamic', 'guided']:
                sched_data = iter_data[
                    (iter_data['schedule'] == schedule) & 
                    (iter_data['chunk_size'] == 0)
                ].sort_values('num_threads')
                
                if len(sched_data) == 0:
                    continue
                
                f.write(f"\n{schedule.upper()} Schedule (default chunk size):\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'Threads':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12} {'vs Sequential':<15}\n")
                f.write("-" * 100 + "\n")
                
                for _, row in sched_data.iterrows():
                    vs_seq = (row['baseline_time_ms'] - row['mean_time_ms']) / row['baseline_time_ms'] * 100
                    f.write(f"{int(row['num_threads']):<10} "
                           f"{row['mean_time_ms']:>10.3f}      "
                           f"{row['speedup']:>8.2f}x    "
                           f"{row['efficiency']:>8.1%}      "
                           f"{vs_seq:>+6.1f}%\n")
        
        f.write("\n" + "="*100 + "\n")
        f.write("KEY FINDINGS:\n")
        f.write("="*100 + "\n")
        f.write("1. Uneven workload pattern: 10% heavy, 10% medium, 80% light iterations\n")
        f.write("2. Dynamic and guided schedules handle load imbalance better than static\n")
        f.write("3. Chunk size significantly affects performance for dynamic/guided schedules\n")
        f.write("4. Efficiency decreases with more threads due to overhead and load imbalance\n")
    
    print(f"✓ Saved: {output_file}")

def main():
    print("="*80)
    print("Task 6: Loop Scheduling Investigation - Graph Generation")
    print("="*80)
    
    # Find and load data
    if len(sys.argv) > 1:
        csv_file = Path(sys.argv[1])
    else:
        csv_file = find_latest_processed_file()
    
    print(f"\nUsing data file: {csv_file}")
    df = load_data(csv_file)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'graphs'
    output_dir.mkdir(exist_ok=True)
    
    print("\nGenerating graphs...")
    
    # Generate all plots
    plot_execution_time_vs_threads(df, output_dir)
    plot_speedup_vs_threads(df, output_dir)
    plot_efficiency_vs_threads(df, output_dir)
    plot_schedule_comparison(df, output_dir)
    plot_chunk_size_impact(df, output_dir)
    create_summary_table(df, output_dir)
    
    print("\n" + "="*80)
    print("Graph generation complete!")
    print("="*80)
    print(f"\nGraphs saved to: {output_dir}")
    print("\nGenerated files:")
    print("  - execution_time_iter_*.png")
    print("  - speedup_iter_*.png")
    print("  - efficiency_iter_*.png")
    print("  - schedule_comparison.png")
    print("  - chunk_size_impact_iter_*.png")
    print("  - summary_table.txt")

if __name__ == "__main__":
    main()