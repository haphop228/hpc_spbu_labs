#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <fstream>
#include <string>
#include <omp.h>

using namespace std;

struct BenchmarkResult {
    string schedule_type;
    int chunk_size;
    int num_threads;
    int num_iterations;
    double execution_time_ms;
    double result;
};

double heavy_work(int iteration, int work_amount) {
    mt19937 gen(iteration * 12345);
    uniform_real_distribution<double> dist(0.0, 1.0);
    
    double sum = 0.0;
    for (int i = 0; i < work_amount; ++i) {
        double val = dist(gen);
        sum += sin(val) * cos(val) + sqrt(val) + log(val + 1.0);
    }
    
    return sum;
}

double light_work(int iteration) {
    return static_cast<double>(iteration) * 0.001;
}
double uneven_workload_loop_sequential(int num_iterations) {
    double total_sum = 0.0;
    
    for (int i = 0; i < num_iterations; ++i) {
        if (i % 10 == 0) {
            total_sum += heavy_work(i, 10000);
        } else if (i % 5 == 0) {
            total_sum += heavy_work(i, 5000);
        } else {
            total_sum += light_work(i);
        }
    }
    
    return total_sum;
}

double uneven_workload_loop_static(int num_iterations, int num_threads, int chunk_size) {
    double total_sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    if (chunk_size > 0) {
        #pragma omp parallel for schedule(static, chunk_size) reduction(+:total_sum)
        for (int i = 0; i < num_iterations; ++i) {
            if (i % 10 == 0) {
                total_sum += heavy_work(i, 10000);
            } else if (i % 5 == 0) {
                total_sum += heavy_work(i, 5000);
            } else {
                total_sum += light_work(i);
            }
        }
    } else {
        #pragma omp parallel for schedule(static) reduction(+:total_sum)
        for (int i = 0; i < num_iterations; ++i) {
            if (i % 10 == 0) {
                total_sum += heavy_work(i, 10000);
            } else if (i % 5 == 0) {
                total_sum += heavy_work(i, 5000);
            } else {
                total_sum += light_work(i);
            }
        }
    }
    
    return total_sum;
}
double uneven_workload_loop_dynamic(int num_iterations, int num_threads, int chunk_size) {
    double total_sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    if (chunk_size > 0) {
        #pragma omp parallel for schedule(dynamic, chunk_size) reduction(+:total_sum)
        for (int i = 0; i < num_iterations; ++i) {
            if (i % 10 == 0) {
                total_sum += heavy_work(i, 10000);
            } else if (i % 5 == 0) {
                total_sum += heavy_work(i, 5000);
            } else {
                total_sum += light_work(i);
            }
        }
    } else {
        #pragma omp parallel for schedule(dynamic) reduction(+:total_sum)
        for (int i = 0; i < num_iterations; ++i) {
            if (i % 10 == 0) {
                total_sum += heavy_work(i, 10000);
            } else if (i % 5 == 0) {
                total_sum += heavy_work(i, 5000);
            } else {
                total_sum += light_work(i);
            }
        }
    }
    
    return total_sum;
}

double uneven_workload_loop_guided(int num_iterations, int num_threads, int chunk_size) {
    double total_sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    if (chunk_size > 0) {
        #pragma omp parallel for schedule(guided, chunk_size) reduction(+:total_sum)
        for (int i = 0; i < num_iterations; ++i) {
            if (i % 10 == 0) {
                total_sum += heavy_work(i, 10000);
            } else if (i % 5 == 0) {
                total_sum += heavy_work(i, 5000);
            } else {
                total_sum += light_work(i);
            }
        }
    } else {
        #pragma omp parallel for schedule(guided) reduction(+:total_sum)
        for (int i = 0; i < num_iterations; ++i) {
            if (i % 10 == 0) {
                total_sum += heavy_work(i, 10000);
            } else if (i % 5 == 0) {
                total_sum += heavy_work(i, 5000);
            } else {
                total_sum += light_work(i);
            }
        }
    }
    
    return total_sum;
}

BenchmarkResult run_benchmark(const string& schedule_type, int num_iterations, 
                              int num_threads, int chunk_size, int runs) {
    BenchmarkResult result;
    result.schedule_type = schedule_type;
    result.chunk_size = chunk_size;
    result.num_threads = num_threads;
    result.num_iterations = num_iterations;
    
    double total_time = 0.0;
    double final_result = 0.0;
    
    for (int run = 0; run < runs; ++run) {
        auto start = chrono::high_resolution_clock::now();
        
        if (schedule_type == "sequential") {
            final_result = uneven_workload_loop_sequential(num_iterations);
        } else if (schedule_type == "static") {
            final_result = uneven_workload_loop_static(num_iterations, num_threads, chunk_size);
        } else if (schedule_type == "dynamic") {
            final_result = uneven_workload_loop_dynamic(num_iterations, num_threads, chunk_size);
        } else if (schedule_type == "guided") {
            final_result = uneven_workload_loop_guided(num_iterations, num_threads, chunk_size);
        }
        
        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double, milli> duration = end - start;
        total_time += duration.count();
    }
    
    result.execution_time_ms = total_time / runs;
    result.result = final_result;
    
    return result;
}

bool verify_correctness(int num_iterations) {
    cout << "\n=== Correctness Verification ===" << endl;
    
    double sequential_result = uneven_workload_loop_sequential(num_iterations);
    cout << "Sequential result: " << fixed << setprecision(6) << sequential_result << endl;
    
    bool all_passed = true;
    const double tolerance = 1e-6;
    
    double static_result = uneven_workload_loop_static(num_iterations, 4, 0);
    double static_error = abs(static_result - sequential_result);
    cout << "Static result:     " << static_result << " (error: " << scientific << static_error << ")" << endl;
    if (static_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    // Test dynamic
    double dynamic_result = uneven_workload_loop_dynamic(num_iterations, 4, 0);
    double dynamic_error = abs(dynamic_result - sequential_result);
    cout << "Dynamic result:    " << dynamic_result << " (error: " << scientific << dynamic_error << ")" << endl;
    if (dynamic_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    // Test guided
    double guided_result = uneven_workload_loop_guided(num_iterations, 4, 0);
    double guided_error = abs(guided_result - sequential_result);
    cout << "Guided result:     " << guided_result << " (error: " << scientific << guided_error << ")" << endl;
    if (guided_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    cout << fixed;
    return all_passed;
}

void print_usage(const char* program_name) {
    cout << "Usage: " << program_name << " <num_iterations> <num_threads> <schedule> <chunk_size> <runs> [output_file]" << endl;
    cout << "\nParameters:" << endl;
    cout << "  num_iterations - Number of loop iterations (e.g., 1000, 5000, 10000)" << endl;
    cout << "  num_threads    - Number of OpenMP threads (1, 2, 4, 8, 16, 32, 64, 128)" << endl;
    cout << "  schedule       - Scheduling strategy: sequential, static, dynamic, guided" << endl;
    cout << "  chunk_size     - Chunk size for scheduling (0 = default)" << endl;
    cout << "  runs           - Number of runs for averaging" << endl;
    cout << "  output_file    - (Optional) CSV file to save results" << endl;
    cout << "\nExamples:" << endl;
    cout << "  " << program_name << " 5000 4 static 0 10" << endl;
    cout << "  " << program_name << " 5000 8 dynamic 10 10 results.csv" << endl;
    cout << "  " << program_name << " 10000 16 guided 0 5" << endl;
}

int main(int argc, char* argv[]) {
    // Check for help flag
    if (argc == 2 && (string(argv[1]) == "-h" || string(argv[1]) == "--help")) {
        print_usage(argv[0]);
        return 0;
    }
    
    // Check for verification mode
    if (argc == 2 && string(argv[1]) == "--verify") {
        bool passed = verify_correctness(1000);
        return passed ? 0 : 1;
    }
    
    // Check arguments
    if (argc < 6) {
        cerr << "Error: Insufficient arguments" << endl;
        print_usage(argv[0]);
        return 1;
    }
    
    // Parse arguments
    int num_iterations = atoi(argv[1]);
    int num_threads = atoi(argv[2]);
    string schedule_type = argv[3];
    int chunk_size = atoi(argv[4]);
    int runs = atoi(argv[5]);
    string output_file = (argc >= 7) ? argv[6] : "";
    
    // Validate arguments
    if (num_iterations <= 0 || num_threads <= 0 || runs <= 0) {
        cerr << "Error: Invalid arguments" << endl;
        return 1;
    }
    
    if (schedule_type != "sequential" && schedule_type != "static" && 
        schedule_type != "dynamic" && schedule_type != "guided") {
        cerr << "Error: Invalid schedule type. Must be: sequential, static, dynamic, or guided" << endl;
        return 1;
    }
    
    // Print configuration
    cout << "=== OpenMP Loop Scheduling Investigation ===" << endl;
    cout << "Iterations:     " << num_iterations << endl;
    cout << "Threads:        " << num_threads << endl;
    cout << "Schedule:       " << schedule_type << endl;
    cout << "Chunk size:     " << (chunk_size == 0 ? "default" : to_string(chunk_size)) << endl;
    cout << "Runs:           " << runs << endl;
    cout << "OpenMP threads: " << omp_get_max_threads() << " available" << endl;
    cout << "\nWorkload pattern:" << endl;
    cout << "  - Every 10th iteration: very heavy (10000 operations)" << endl;
    cout << "  - Every 5th iteration:  medium (5000 operations)" << endl;
    cout << "  - Other iterations:     light (minimal work)" << endl;
    cout << "\n=== Running Benchmark ===" << endl;
    
    // Run benchmark
    BenchmarkResult result = run_benchmark(schedule_type, num_iterations, num_threads, 
                                          chunk_size, runs);
    
    // Print results
    cout << "\n=== Results ===" << endl;
    cout << "Average execution time: " << fixed << setprecision(3) 
         << result.execution_time_ms << " ms" << endl;
    cout << "Result value: " << setprecision(6) << result.result << endl;
    
    // Save to file if specified
    if (!output_file.empty()) {
        ofstream file;
        bool file_exists = ifstream(output_file).good();
        file.open(output_file, ios::app);
        
        if (!file_exists) {
            // Write header
            file << "num_iterations,num_threads,schedule,chunk_size,execution_time_ms,result" << endl;
        }
        
        file << num_iterations << ","
             << num_threads << ","
             << schedule_type << ","
             << chunk_size << ","
             << fixed << setprecision(6) << result.execution_time_ms << ","
             << result.result << endl;
        
        file.close();
        cout << "\nResults saved to: " << output_file << endl;
    }
    
    return 0;
}