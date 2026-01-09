#!/usr/bin/env python3

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_results(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        results = []
        for line in lines:
            line = line.strip()
            if line and line not in ['[', ']', ',']:
                try:
                    results.append(json.loads(line.rstrip(',')))
                except json.JSONDecodeError:
                    continue
    return results

def group_results(results):
    grouped = defaultdict(list)
    
    for result in results:
        key = (
            result['method'],
            result['operation'],
            result['threads'],
            result['size']
        )
        grouped[key].append(result['time_ms'])
    
    return grouped

def compute_statistics(grouped_results):
    stats = []
    
    for key, times in grouped_results.items():
        method, operation, threads, size = key
        times_array = np.array(times)
        
        stat = {
            'method': method,
            'operation': operation,
            'threads': threads,
            'size': size,
            'mean_time_ms': float(np.mean(times_array)),
            'median_time_ms': float(np.median(times_array)),
            'std_time_ms': float(np.std(times_array)),
            'min_time_ms': float(np.min(times_array)),
            'max_time_ms': float(np.max(times_array)),
            'num_runs': len(times)
        }
        stats.append(stat)
    
    return stats

def compute_speedup(stats):
    baseline_times = {}
    
    for stat in stats:
        if stat['threads'] == 1:
            key = (stat['method'], stat['operation'], stat['size'])
            baseline_times[key] = stat['median_time_ms']
    
    # Add speedup to each stat
    for stat in stats:
        key = (stat['method'], stat['operation'], stat['size'])
        if key in baseline_times and baseline_times[key] > 0:
            stat['speedup'] = baseline_times[key] / stat['median_time_ms']
            stat['efficiency'] = stat['speedup'] / stat['threads']
        else:
            stat['speedup'] = 1.0
            stat['efficiency'] = 1.0
    
    return stats

def print_summary(stats):
    """Print summary of results"""
    print("\n" + "="*80)
    print("BENCHMARK RESULTS SUMMARY")
    print("="*80)
    
    # Group by size
    sizes = sorted(set(s['size'] for s in stats))
    
    for size in sizes:
        print(f"\nVector Size: {size:,} elements")
        print("-" * 80)
        
        size_stats = [s for s in stats if s['size'] == size]
        
        # Group by method and operation
        for method in ['reduction', 'no-reduction']:
            for operation in ['min', 'max']:
                print(f"\n  {method.upper()} - {operation.upper()}:")
                
                method_stats = [s for s in size_stats 
                              if s['method'] == method and s['operation'] == operation]
                method_stats.sort(key=lambda x: x['threads'])
                
                print(f"    {'Threads':<10} {'Time (ms)':<15} {'Speedup':<12} {'Efficiency':<12}")
                print(f"    {'-'*10} {'-'*15} {'-'*12} {'-'*12}")
                
                for stat in method_stats:
                    print(f"    {stat['threads']:<10} "
                          f"{stat['median_time_ms']:<15.3f} "
                          f"{stat['speedup']:<12.2f} "
                          f"{stat['efficiency']:<12.2%}")

def save_processed_results(stats, output_path):
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze.py <results_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        sys.exit(1)
    
    results = load_results(input_file)
    grouped = group_results(results)
    stats = compute_statistics(grouped)
    stats = compute_speedup(stats)
    
    print_summary(stats)
    output_file = input_file.replace('.json', '_processed.json')
    save_processed_results(stats, output_file)

if __name__ == '__main__':
    main()
