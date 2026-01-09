#!/usr/bin/env python3
"""
Enhanced graph generation script for OpenMP min/max benchmark results
Creates comprehensive visualizations for deep performance analysis
"""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.gridspec import GridSpec

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_processed_results(filepath):
    """Load processed statistics from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def plot_execution_time(stats, output_dir):
    """Plot execution time vs thread count"""
    sizes = sorted(set(s['size'] for s in stats))
    
    for size in sizes:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Execution Time vs Thread Count (Size: {size:,} elements)', 
                     fontsize=14, fontweight='bold')
        
        for idx, operation in enumerate(['min', 'max']):
            ax = axes[idx]
            
            for method in ['reduction', 'no-reduction']:
                method_stats = [s for s in stats 
                              if s['size'] == size 
                              and s['operation'] == operation 
                              and s['method'] == method]
                method_stats.sort(key=lambda x: x['threads'])
                
                threads = [s['threads'] for s in method_stats]
                times = [s['median_time_ms'] for s in method_stats]
                
                label = 'With Reduction' if method == 'reduction' else 'Without Reduction'
                marker = 'o' if method == 'reduction' else 's'
                ax.plot(threads, times, marker=marker, linewidth=2, 
                       markersize=8, label=label)
            
            ax.set_xlabel('Number of Threads', fontsize=12)
            ax.set_ylabel('Execution Time (ms)', fontsize=12)
            ax.set_title(f'{operation.upper()} Operation', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(sorted(set(s['threads'] for s in stats)))
        
        plt.tight_layout()
        output_file = output_dir / f'execution_time_size_{size}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

def plot_speedup(stats, output_dir):
    """Plot speedup vs thread count with ideal speedup line"""
    sizes = sorted(set(s['size'] for s in stats))
    
    for size in sizes:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Speedup vs Thread Count (Size: {size:,} elements)', 
                     fontsize=14, fontweight='bold')
        
        for idx, operation in enumerate(['min', 'max']):
            ax = axes[idx]
            
            # Plot ideal speedup line
            max_threads = max(s['threads'] for s in stats)
            ideal_threads = list(range(1, max_threads + 1))
            ax.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
                   label='Ideal Speedup', alpha=0.5)
            
            for method in ['reduction', 'no-reduction']:
                method_stats = [s for s in stats 
                              if s['size'] == size 
                              and s['operation'] == operation 
                              and s['method'] == method]
                method_stats.sort(key=lambda x: x['threads'])
                
                threads = [s['threads'] for s in method_stats]
                speedups = [s['speedup'] for s in method_stats]
                
                label = 'With Reduction' if method == 'reduction' else 'Without Reduction'
                marker = 'o' if method == 'reduction' else 's'
                ax.plot(threads, speedups, marker=marker, linewidth=2, 
                       markersize=8, label=label)
            
            ax.set_xlabel('Number of Threads', fontsize=12)
            ax.set_ylabel('Speedup', fontsize=12)
            ax.set_title(f'{operation.upper()} Operation', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(sorted(set(s['threads'] for s in stats)))
        
        plt.tight_layout()
        output_file = output_dir / f'speedup_size_{size}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

def plot_efficiency(stats, output_dir):
    """Plot parallel efficiency vs thread count"""
    sizes = sorted(set(s['size'] for s in stats))
    
    for size in sizes:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Parallel Efficiency vs Thread Count (Size: {size:,} elements)', 
                     fontsize=14, fontweight='bold')
        
        for idx, operation in enumerate(['min', 'max']):
            ax = axes[idx]
            
            # Plot ideal efficiency line (100%)
            max_threads = max(s['threads'] for s in stats)
            ax.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                      label='Ideal Efficiency', alpha=0.5)
            
            for method in ['reduction', 'no-reduction']:
                method_stats = [s for s in stats 
                              if s['size'] == size 
                              and s['operation'] == operation 
                              and s['method'] == method]
                method_stats.sort(key=lambda x: x['threads'])
                
                threads = [s['threads'] for s in method_stats]
                efficiencies = [s['efficiency'] for s in method_stats]
                
                label = 'With Reduction' if method == 'reduction' else 'Without Reduction'
                marker = 'o' if method == 'reduction' else 's'
                ax.plot(threads, efficiencies, marker=marker, linewidth=2, 
                       markersize=8, label=label)
            
            ax.set_xlabel('Number of Threads', fontsize=12)
            ax.set_ylabel('Efficiency', fontsize=12)
            ax.set_title(f'{operation.upper()} Operation', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(sorted(set(s['threads'] for s in stats)))
            ax.set_ylim([0, 1.1])
        
        plt.tight_layout()
        output_file = output_dir / f'efficiency_size_{size}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

def plot_comparison_reduction_methods(stats, output_dir):
    """Compare reduction vs non-reduction methods"""
    sizes = sorted(set(s['size'] for s in stats))
    operations = ['min', 'max']
    
    fig, axes = plt.subplots(len(sizes), 2, figsize=(14, 6 * len(sizes)))
    if len(sizes) == 1:
        axes = axes.reshape(1, -1)
    
    fig.suptitle('Comparison: Reduction vs Non-Reduction Methods', 
                 fontsize=16, fontweight='bold')
    
    for size_idx, size in enumerate(sizes):
        for op_idx, operation in enumerate(operations):
            ax = axes[size_idx, op_idx]
            
            for method in ['reduction', 'no-reduction']:
                method_stats = [s for s in stats 
                              if s['size'] == size 
                              and s['operation'] == operation 
                              and s['method'] == method]
                method_stats.sort(key=lambda x: x['threads'])
                
                threads = [s['threads'] for s in method_stats]
                speedups = [s['speedup'] for s in method_stats]
                
                label = 'With Reduction' if method == 'reduction' else 'Without Reduction'
                marker = 'o' if method == 'reduction' else 's'
                ax.plot(threads, speedups, marker=marker, linewidth=2, 
                       markersize=8, label=label)
            
            # Add ideal speedup
            max_threads = max(s['threads'] for s in stats)
            ideal_threads = list(range(1, max_threads + 1))
            ax.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
                   label='Ideal', alpha=0.5)
            
            ax.set_xlabel('Number of Threads', fontsize=11)
            ax.set_ylabel('Speedup', fontsize=11)
            ax.set_title(f'Size: {size:,} - {operation.upper()}', fontsize=11)
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xticks(sorted(set(s['threads'] for s in stats)))
    
    plt.tight_layout()
    output_file = output_dir / 'comparison_reduction_methods.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_scalability_analysis(stats, output_dir):
    """NEW: Analyze scalability - how speedup changes with problem size"""
    sizes = sorted(set(s['size'] for s in stats))
    if len(sizes) < 2:
        return  # Need multiple sizes for this analysis
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Scalability Analysis: Impact of Problem Size', 
                 fontsize=16, fontweight='bold')
    
    thread_counts = sorted(set(s['threads'] for s in stats if s['threads'] > 1))
    
    for method_idx, method in enumerate(['reduction', 'no-reduction']):
        for op_idx, operation in enumerate(['min', 'max']):
            ax = axes[method_idx, op_idx]
            
            for threads in thread_counts:
                speedups = []
                size_labels = []
                
                for size in sizes:
                    matching = [s for s in stats 
                              if s['size'] == size 
                              and s['threads'] == threads
                              and s['method'] == method
                              and s['operation'] == operation]
                    if matching:
                        speedups.append(matching[0]['speedup'])
                        size_labels.append(f"{size/1e6:.1f}M")
                
                if speedups:
                    ax.plot(size_labels, speedups, marker='o', linewidth=2,
                           markersize=8, label=f'{threads} threads')
            
            method_name = 'With Reduction' if method == 'reduction' else 'Without Reduction'
            ax.set_xlabel('Problem Size', fontsize=11)
            ax.set_ylabel('Speedup', fontsize=11)
            ax.set_title(f'{method_name} - {operation.upper()}', fontsize=11)
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / 'scalability_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_overhead_analysis(stats, output_dir):
    """NEW: Analyze parallelization overhead"""
    sizes = sorted(set(s['size'] for s in stats))
    
    if len(sizes) == 1:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    else:
        fig, axes = plt.subplots(len(sizes), 2, figsize=(14, 6 * len(sizes)))
    
    fig.suptitle('Parallelization Overhead Analysis',
                 fontsize=16, fontweight='bold')
    
    for size_idx, size in enumerate(sizes):
        for op_idx, operation in enumerate(['min', 'max']):
            if len(sizes) == 1:
                ax = axes[op_idx]
            else:
                ax = axes[size_idx, op_idx]
            
            for method in ['reduction', 'no-reduction']:
                method_stats = [s for s in stats 
                              if s['size'] == size 
                              and s['operation'] == operation 
                              and s['method'] == method]
                method_stats.sort(key=lambda x: x['threads'])
                
                if not method_stats:
                    continue
                
                # Calculate overhead: (sequential_time - parallel_time * threads) / sequential_time
                seq_time = method_stats[0]['median_time_ms']
                threads = []
                overheads = []
                
                for stat in method_stats[1:]:  # Skip single thread
                    ideal_time = seq_time / stat['threads']
                    actual_time = stat['median_time_ms']
                    overhead_pct = ((actual_time - ideal_time) / ideal_time) * 100
                    threads.append(stat['threads'])
                    overheads.append(overhead_pct)
                
                label = 'With Reduction' if method == 'reduction' else 'Without Reduction'
                marker = 'o' if method == 'reduction' else 's'
                ax.plot(threads, overheads, marker=marker, linewidth=2,
                       markersize=8, label=label)
            
            ax.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)
            ax.set_xlabel('Number of Threads', fontsize=11)
            ax.set_ylabel('Overhead (%)', fontsize=11)
            ax.set_title(f'Size: {size:,} - {operation.upper()}', fontsize=11)
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / 'overhead_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_performance_heatmap(stats, output_dir):
    """NEW: Heatmap showing speedup across all configurations"""
    sizes = sorted(set(s['size'] for s in stats))
    threads_list = sorted(set(s['threads'] for s in stats))
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Performance Heatmap: Speedup Across All Configurations', 
                 fontsize=16, fontweight='bold')
    
    for method_idx, method in enumerate(['reduction', 'no-reduction']):
        for op_idx, operation in enumerate(['min', 'max']):
            ax = axes[method_idx, op_idx]
            
            # Create matrix for heatmap
            speedup_matrix = np.zeros((len(sizes), len(threads_list)))
            
            for i, size in enumerate(sizes):
                for j, threads in enumerate(threads_list):
                    matching = [s for s in stats 
                              if s['size'] == size 
                              and s['threads'] == threads
                              and s['method'] == method
                              and s['operation'] == operation]
                    if matching:
                        speedup_matrix[i, j] = matching[0]['speedup']
            
            im = ax.imshow(speedup_matrix, cmap='RdYlGn', aspect='auto', 
                          vmin=0, vmax=max(threads_list))
            
            # Set ticks and labels
            ax.set_xticks(range(len(threads_list)))
            ax.set_xticklabels(threads_list)
            ax.set_yticks(range(len(sizes)))
            ax.set_yticklabels([f"{s/1e6:.1f}M" for s in sizes])
            
            # Add text annotations
            for i in range(len(sizes)):
                for j in range(len(threads_list)):
                    text = ax.text(j, i, f'{speedup_matrix[i, j]:.2f}',
                                 ha="center", va="center", color="black", fontsize=9)
            
            method_name = 'With Reduction' if method == 'reduction' else 'Without Reduction'
            ax.set_xlabel('Number of Threads', fontsize=11)
            ax.set_ylabel('Problem Size', fontsize=11)
            ax.set_title(f'{method_name} - {operation.upper()}', fontsize=11)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Speedup', fontsize=10)
    
    plt.tight_layout()
    output_file = output_dir / 'performance_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_strong_scaling(stats, output_dir):
    """NEW: Strong scaling analysis - fixed problem size, varying threads"""
    sizes = sorted(set(s['size'] for s in stats))
    
    for size in sizes:
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(2, 3, figure=fig)
        
        fig.suptitle(f'Strong Scaling Analysis (Size: {size:,} elements)', 
                     fontsize=16, fontweight='bold')
        
        # Speedup plot
        ax1 = fig.add_subplot(gs[0, :2])
        # Efficiency plot
        ax2 = fig.add_subplot(gs[1, :2])
        # Time comparison
        ax3 = fig.add_subplot(gs[:, 2])
        
        for method in ['reduction', 'no-reduction']:
            method_stats = [s for s in stats 
                          if s['size'] == size and s['method'] == method]
            
            # Combine min and max for overall view
            combined_stats = {}
            for stat in method_stats:
                key = stat['threads']
                if key not in combined_stats:
                    combined_stats[key] = {'speedup': [], 'efficiency': [], 'time': []}
                combined_stats[key]['speedup'].append(stat['speedup'])
                combined_stats[key]['efficiency'].append(stat['efficiency'])
                combined_stats[key]['time'].append(stat['median_time_ms'])
            
            threads = sorted(combined_stats.keys())
            avg_speedups = [np.mean(combined_stats[t]['speedup']) for t in threads]
            avg_efficiencies = [np.mean(combined_stats[t]['efficiency']) for t in threads]
            avg_times = [np.mean(combined_stats[t]['time']) for t in threads]
            
            label = 'With Reduction' if method == 'reduction' else 'Without Reduction'
            marker = 'o' if method == 'reduction' else 's'
            
            # Plot speedup
            ax1.plot(threads, avg_speedups, marker=marker, linewidth=2,
                    markersize=8, label=label)
            
            # Plot efficiency
            ax2.plot(threads, avg_efficiencies, marker=marker, linewidth=2,
                    markersize=8, label=label)
            
            # Plot time
            ax3.plot(threads, avg_times, marker=marker, linewidth=2,
                    markersize=8, label=label)
        
        # Ideal lines
        max_threads = max(s['threads'] for s in stats)
        ideal_threads = list(range(1, max_threads + 1))
        ax1.plot(ideal_threads, ideal_threads, 'k--', linewidth=2, 
                label='Ideal', alpha=0.5)
        ax2.axhline(y=1.0, color='k', linestyle='--', linewidth=2, 
                   label='Ideal', alpha=0.5)
        
        # Configure axes
        ax1.set_xlabel('Number of Threads', fontsize=11)
        ax1.set_ylabel('Speedup', fontsize=11)
        ax1.set_title('Average Speedup', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(sorted(set(s['threads'] for s in stats)))
        
        ax2.set_xlabel('Number of Threads', fontsize=11)
        ax2.set_ylabel('Efficiency', fontsize=11)
        ax2.set_title('Average Efficiency', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(sorted(set(s['threads'] for s in stats)))
        ax2.set_ylim([0, 1.1])
        
        ax3.set_xlabel('Number of Threads', fontsize=11)
        ax3.set_ylabel('Execution Time (ms)', fontsize=11)
        ax3.set_title('Average Execution Time', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks(sorted(set(s['threads'] for s in stats)))
        
        plt.tight_layout()
        output_file = output_dir / f'strong_scaling_size_{size}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()

def plot_method_comparison_detailed(stats, output_dir):
    """NEW: Detailed comparison between reduction methods"""
    sizes = sorted(set(s['size'] for s in stats))
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Detailed Method Comparison: Reduction vs No-Reduction', 
                 fontsize=16, fontweight='bold')
    
    # Speedup advantage
    ax1 = axes[0, 0]
    # Time difference
    ax2 = axes[0, 1]
    # Efficiency difference
    ax3 = axes[1, 0]
    # Relative performance
    ax4 = axes[1, 1]
    
    for size in sizes:
        for operation in ['min', 'max']:
            reduction_stats = [s for s in stats 
                             if s['size'] == size 
                             and s['operation'] == operation 
                             and s['method'] == 'reduction']
            no_reduction_stats = [s for s in stats 
                                if s['size'] == size 
                                and s['operation'] == operation 
                                and s['method'] == 'no-reduction']
            
            if not reduction_stats or not no_reduction_stats:
                continue
            
            reduction_stats.sort(key=lambda x: x['threads'])
            no_reduction_stats.sort(key=lambda x: x['threads'])
            
            threads = [s['threads'] for s in reduction_stats]
            
            # Speedup advantage (no-reduction speedup - reduction speedup)
            speedup_diff = [nr['speedup'] - r['speedup'] 
                          for r, nr in zip(reduction_stats, no_reduction_stats)]
            
            # Time difference (reduction time - no-reduction time)
            time_diff = [r['median_time_ms'] - nr['median_time_ms']
                        for r, nr in zip(reduction_stats, no_reduction_stats)]
            
            # Efficiency difference
            eff_diff = [nr['efficiency'] - r['efficiency']
                       for r, nr in zip(reduction_stats, no_reduction_stats)]
            
            # Relative performance (no-reduction time / reduction time)
            rel_perf = [nr['median_time_ms'] / r['median_time_ms']
                       for r, nr in zip(reduction_stats, no_reduction_stats)]
            
            label = f"Size: {size/1e6:.1f}M - {operation.upper()}"
            marker = 'o' if operation == 'min' else 's'
            
            ax1.plot(threads, speedup_diff, marker=marker, linewidth=2,
                    markersize=6, label=label, alpha=0.7)
            ax2.plot(threads, time_diff, marker=marker, linewidth=2,
                    markersize=6, label=label, alpha=0.7)
            ax3.plot(threads, eff_diff, marker=marker, linewidth=2,
                    markersize=6, label=label, alpha=0.7)
            ax4.plot(threads, rel_perf, marker=marker, linewidth=2,
                    markersize=6, label=label, alpha=0.7)
    
    # Configure axes
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xlabel('Number of Threads', fontsize=11)
    ax1.set_ylabel('Speedup Difference', fontsize=11)
    ax1.set_title('No-Reduction Speedup Advantage\n(Positive = No-Reduction Better)', fontsize=11)
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Number of Threads', fontsize=11)
    ax2.set_ylabel('Time Difference (ms)', fontsize=11)
    ax2.set_title('Time Saved by No-Reduction\n(Positive = No-Reduction Faster)', fontsize=11)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    ax3.axhline(y=0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax3.set_xlabel('Number of Threads', fontsize=11)
    ax3.set_ylabel('Efficiency Difference', fontsize=11)
    ax3.set_title('Efficiency Advantage\n(Positive = No-Reduction More Efficient)', fontsize=11)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    ax4.axhline(y=1.0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax4.set_xlabel('Number of Threads', fontsize=11)
    ax4.set_ylabel('Relative Performance', fontsize=11)
    ax4.set_title('No-Reduction / Reduction Time Ratio\n(<1 = No-Reduction Faster)', fontsize=11)
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / 'method_comparison_detailed.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_amdahls_law_analysis(stats, output_dir):
    """NEW: Amdahl's Law analysis - theoretical vs actual speedup"""
    sizes = sorted(set(s['size'] for s in stats))
    
    if len(sizes) == 1:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    else:
        fig, axes = plt.subplots(len(sizes), 2, figsize=(14, 6 * len(sizes)))
    
    fig.suptitle("Amdahl's Law Analysis: Theoretical vs Actual Speedup",
                 fontsize=16, fontweight='bold')
    
    for size_idx, size in enumerate(sizes):
        for method_idx, method in enumerate(['reduction', 'no-reduction']):
            if len(sizes) == 1:
                ax = axes[method_idx]
            else:
                ax = axes[size_idx, method_idx]
            
            method_stats = [s for s in stats 
                          if s['size'] == size and s['method'] == method]
            
            if not method_stats:
                continue
            
            # Combine min and max
            combined_stats = {}
            for stat in method_stats:
                key = stat['threads']
                if key not in combined_stats:
                    combined_stats[key] = []
                combined_stats[key].append(stat['speedup'])
            
            threads = sorted(combined_stats.keys())
            avg_speedups = [np.mean(combined_stats[t]) for t in threads]
            
            # Plot actual speedup
            ax.plot(threads, avg_speedups, 'bo-', linewidth=2, markersize=8,
                   label='Actual Speedup')
            
            # Plot ideal speedup
            ax.plot(threads, threads, 'k--', linewidth=2, label='Ideal (100% parallel)')
            
            # Plot Amdahl's law for different parallel fractions
            max_threads = max(threads)
            thread_range = np.linspace(1, max_threads, 100)
            
            for parallel_fraction in [0.95, 0.90, 0.85, 0.80]:
                amdahl_speedup = 1 / ((1 - parallel_fraction) + parallel_fraction / thread_range)
                ax.plot(thread_range, amdahl_speedup, '--', linewidth=1.5, alpha=0.6,
                       label=f"Amdahl ({parallel_fraction*100:.0f}% parallel)")
            
            method_name = 'With Reduction' if method == 'reduction' else 'Without Reduction'
            ax.set_xlabel('Number of Threads', fontsize=11)
            ax.set_ylabel('Speedup', fontsize=11)
            ax.set_title(f'{method_name} - Size: {size:,}', fontsize=11)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.set_xticks(threads)
    
    plt.tight_layout()
    output_file = output_dir / 'amdahls_law_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def generate_summary_table(stats, output_dir):
    """Generate summary table in text format"""
    output_file = output_dir / 'summary_table.txt'
    
    with open(output_file, 'w') as f:
        f.write("="*100 + "\n")
        f.write("BENCHMARK RESULTS SUMMARY TABLE\n")
        f.write("="*100 + "\n\n")
        
        sizes = sorted(set(s['size'] for s in stats))
        
        for size in sizes:
            f.write(f"\nVector Size: {size:,} elements\n")
            f.write("-"*100 + "\n")
            
            for operation in ['min', 'max']:
                f.write(f"\n{operation.upper()} Operation:\n")
                f.write(f"{'Method':<20} {'Threads':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12}\n")
                f.write(f"{'-'*20} {'-'*10} {'-'*15} {'-'*12} {'-'*12}\n")
                
                for method in ['reduction', 'no-reduction']:
                    method_stats = [s for s in stats
                                  if s['size'] == size
                                  and s['operation'] == operation
                                  and s['method'] == method]
                    method_stats.sort(key=lambda x: x['threads'])
                    
                    for stat in method_stats:
                        f.write(f"{method:<20} {stat['threads']:<10} "
                               f"{stat['median_time_ms']:<15.3f} "
                               f"{stat['speedup']:<12.2f} "
                               f"{stat['efficiency']:<12.2%}\n")
                f.write("\n")
    
    print(f"✓ Saved: {output_file}")

def main():
    # Find the most recent processed results file
    # Handle both running from analysis/ and from project root
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / 'results'
    
    if not results_dir.exists():
        print(f"Error: Results directory not found at {results_dir}")
        sys.exit(1)
    
    processed_files = list(results_dir.glob('*_processed.json'))
    
    if not processed_files:
        print("Error: No processed results found")
        print("Please run analyze.py first")
        sys.exit(1)
    
    # Use the most recent file
    input_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading processed results from: {input_file}")
    
    stats = load_processed_results(input_file)
    print(f"✓ Loaded {len(stats)} processed statistics")
    
    # Create report directory
    report_dir = script_dir.parent / 'graphs'
    report_dir.mkdir(exist_ok=True)
    
    print("\nGenerating graphs...")
    print("-" * 50)
    
    # Original graphs
    plot_execution_time(stats, report_dir)
    plot_speedup(stats, report_dir)
    plot_efficiency(stats, report_dir)
    plot_comparison_reduction_methods(stats, report_dir)
    
    # NEW: Advanced analysis graphs
    print("\nGenerating advanced analysis graphs...")
    plot_scalability_analysis(stats, report_dir)
    plot_overhead_analysis(stats, report_dir)
    plot_performance_heatmap(stats, report_dir)
    plot_strong_scaling(stats, report_dir)
    plot_method_comparison_detailed(stats, report_dir)
    plot_amdahls_law_analysis(stats, report_dir)
    
    # Summary table
    generate_summary_table(stats, report_dir)
    
    print("\n" + "="*50)
    print("✓ All graphs generated successfully!")
    print(f"✓ Output directory: {report_dir.absolute()}")
    print("\nGenerated graphs:")
    print("  - execution_time_*.png (original)")
    print("  - speedup_*.png (original)")
    print("  - efficiency_*.png (original)")
    print("  - comparison_reduction_methods.png (original)")
    print("  - scalability_analysis.png (NEW)")
    print("  - overhead_analysis.png (NEW)")
    print("  - performance_heatmap.png (NEW)")
    print("  - strong_scaling_*.png (NEW)")
    print("  - method_comparison_detailed.png (NEW)")
    print("  - amdahls_law_analysis.png (NEW)")
    print("  - summary_table.txt")
    print("="*50)

if __name__ == '__main__':
    main()
