#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <omp.h>
#include <cmath>
#include <string>
#include <random>
#include <limits>

using Matrix = std::vector<std::vector<double>>;

Matrix generate_matrix(int N, int seed = 42) {
    Matrix matrix(N, std::vector<double>(N));
    std::mt19937 gen(seed);
    std::uniform_real_distribution<> dis(-100.0, 100.0);
    
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            matrix[i][j] = dis(gen);
        }
    }
    
    return matrix;
}

double maximin_sequential(const Matrix& matrix) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    for (int i = 0; i < N; ++i) {
        double row_min = matrix[i][0];
        for (int j = 1; j < N; ++j) {
            row_min = std::min(row_min, matrix[i][j]);
        }
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}

double maximin_flat(const Matrix& matrix, int num_threads) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(max:max_of_mins)
    for (int i = 0; i < N; ++i) {
        double row_min = matrix[i][0];
        for (int j = 1; j < N; ++j) {
            row_min = std::min(row_min, matrix[i][j]);
        }
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}

double maximin_nested(const Matrix& matrix, int outer_threads, int inner_threads) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    omp_set_nested(1);
    omp_set_max_active_levels(2);
    
    omp_set_num_threads(outer_threads);
    
    #pragma omp parallel for reduction(max:max_of_mins)
    for (int i = 0; i < N; ++i) {
        double row_min = std::numeric_limits<double>::max();
        
        #pragma omp parallel for num_threads(inner_threads) reduction(min:row_min)
        for (int j = 0; j < N; ++j) {
            row_min = std::min(row_min, matrix[i][j]);
        }
        
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}

struct BenchmarkResult {
    int N;
    int num_threads;
    int outer_threads;
    int inner_threads;
    std::string method;
    double execution_time;
    double result_value;
    int iteration;
};

std::vector<BenchmarkResult> run_benchmark(const Matrix& matrix,
                                           int num_threads,
                                           const std::string& method,
                                           int iterations,
                                           int outer_threads = 0,
                                           int inner_threads = 0) {
    std::vector<BenchmarkResult> results;
    int N = matrix.size();
    
    // Warmup
    if (method == "flat") {
        maximin_flat(matrix, num_threads);
    } else if (method == "nested") {
        maximin_nested(matrix, outer_threads, inner_threads);
    }
    
    for (int iter = 0; iter < iterations; ++iter) {
        double result = 0.0;
        double execution_time = 0.0;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        if (method == "sequential") {
            result = maximin_sequential(matrix);
        } else if (method == "flat") {
            result = maximin_flat(matrix, num_threads);
        } else if (method == "nested") {
            result = maximin_nested(matrix, outer_threads, inner_threads);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        execution_time = std::chrono::duration<double, std::milli>(end - start).count();
        
        BenchmarkResult bench_result;
        bench_result.N = N;
        bench_result.num_threads = num_threads;
        bench_result.outer_threads = outer_threads;
        bench_result.inner_threads = inner_threads;
        bench_result.method = method;
        bench_result.execution_time = execution_time;
        bench_result.result_value = result;
        bench_result.iteration = iter;
        
        results.push_back(bench_result);
    }
    
    return results;
}

bool verify_correctness() {
    std::cout << "\n=== Correctness Verification ===" << std::endl;
    
    {
        Matrix test_matrix = {
            {5.0, 3.0, 7.0},
            {2.0, 8.0, 1.0},
            {6.0, 4.0, 9.0}
        };
        
        double seq = maximin_sequential(test_matrix);
        double flat = maximin_flat(test_matrix, 2);
        double nested = maximin_nested(test_matrix, 2, 2);
        
        double expected = 4.0;
        
        std::cout << "\nTest 1: 3x3 matrix (expected = " << expected << ")" << std::endl;
        std::cout << "  Sequential: " << std::fixed << std::setprecision(6) << seq
                  << " (error: " << std::abs(seq - expected) << ")" << std::endl;
        std::cout << "  Flat:       " << flat
                  << " (error: " << std::abs(flat - expected) << ")" << std::endl;
        std::cout << "  Nested:     " << nested
                  << " (error: " << std::abs(nested - expected) << ")" << std::endl;
        
        if (std::abs(seq - expected) > 1e-6 ||
            std::abs(flat - expected) > 1e-6 ||
            std::abs(nested - expected) > 1e-6) {
            std::cout << "  ✗ FAILED" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED" << std::endl;
    }
    
    {
        int N = 100;
        Matrix test_matrix = generate_matrix(N, 12345);
        
        double seq = maximin_sequential(test_matrix);
        double flat = maximin_flat(test_matrix, 4);
        double nested = maximin_nested(test_matrix, 2, 2);
        
        std::cout << "\nTest 2: " << N << "x" << N << " random matrix" << std::endl;
        std::cout << "  Sequential: " << seq << std::endl;
        std::cout << "  Flat:       " << flat << std::endl;
        std::cout << "  Nested:     " << nested << std::endl;
        
        if (std::abs(seq - flat) > 1e-6 || std::abs(seq - nested) > 1e-6) {
            std::cout << "  ✗ FAILED - Methods give different results" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED - All methods agree" << std::endl;
    }
    
    std::cout << "\n=== Verification Complete ===" << std::endl;
    return true;
}

void check_nested_support() {
    std::cout << "\n=== Checking Nested Parallelism Support ===" << std::endl;
    
    int max_levels = omp_get_max_active_levels();
    std::cout << "Max active levels: " << max_levels << std::endl;
    
    omp_set_nested(1);
    int nested_enabled = omp_get_nested();
    std::cout << "Nested parallelism enabled: " << (nested_enabled ? "YES" : "NO") << std::endl;
    
    std::cout << "\nTesting nested parallelism:" << std::endl;
    #pragma omp parallel num_threads(2)
    {
        int outer_tid = omp_get_thread_num();
        int outer_nthreads = omp_get_num_threads();
        
        #pragma omp parallel num_threads(2)
        {
            int inner_tid = omp_get_thread_num();
            int inner_nthreads = omp_get_num_threads();
            
            #pragma omp critical
            {
                std::cout << "  Outer thread " << outer_tid << "/" << outer_nthreads
                          << " -> Inner thread " << inner_tid << "/" << inner_nthreads << std::endl;
            }
        }
    }
    
    if (nested_enabled && max_levels >= 2) {
        std::cout << "\n✓ Nested parallelism is SUPPORTED" << std::endl;
    } else {
        std::cout << "\n✗ Nested parallelism is NOT SUPPORTED or limited" << std::endl;
    }
    std::cout << "========================================\n" << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <N> <num_threads> <method> <iterations> [output_file]" << std::endl;
        std::cerr << "\nParameters:" << std::endl;
        std::cerr << "  N           - matrix size (NxN)" << std::endl;
        std::cerr << "  num_threads - total number of threads (for flat) or outer_threads:inner_threads (for nested)" << std::endl;
        std::cerr << "  method      - sequential, flat, nested" << std::endl;
        std::cerr << "  iterations  - number of runs for averaging" << std::endl;
        std::cerr << "\nExamples:" << std::endl;
        std::cerr << "  " << argv[0] << " 1000 4 flat 10" << std::endl;
        std::cerr << "  " << argv[0] << " 1000 2:2 nested 10" << std::endl;
        std::cerr << "  " << argv[0] << " 1000 4:2 nested 10" << std::endl;
        return 1;
    }
    
    int N = std::stoi(argv[1]);
    std::string threads_str = argv[2];
    std::string method = argv[3];
    int iterations = std::stoi(argv[4]);
    std::string output_file = (argc > 5) ? argv[5] : "";
    
    if (method != "sequential" && method != "flat" && method != "nested") {
        std::cerr << "Error: Invalid method '" << method << "'" << std::endl;
        return 1;
    }
    
    int num_threads = 0;
    int outer_threads = 0;
    int inner_threads = 0;
    
    if (method == "nested") {
        size_t colon_pos = threads_str.find(':');
        if (colon_pos == std::string::npos) {
            std::cerr << "Error: For nested method, use format outer:inner (e.g., 2:2)" << std::endl;
            return 1;
        }
        outer_threads = std::stoi(threads_str.substr(0, colon_pos));
        inner_threads = std::stoi(threads_str.substr(colon_pos + 1));
        num_threads = outer_threads * inner_threads;
    } else {
        num_threads = std::stoi(threads_str);
    }
    
    check_nested_support();
    
    if (!verify_correctness()) {
        std::cerr << "Error: Correctness verification failed!" << std::endl;
        return 1;
    }
    
    std::cout << "\nGenerating " << N << "x" << N << " matrix..." << std::endl;
    Matrix matrix = generate_matrix(N);
    std::cout << "Matrix generated." << std::endl;
    
    std::cout << "\nRunning benchmark..." << std::endl;
    if (method == "nested") {
        std::cout << "Method: " << method << " (outer=" << outer_threads 
                  << ", inner=" << inner_threads << ", total=" << num_threads << ")" << std::endl;
    } else {
        std::cout << "Method: " << method << " (threads=" << num_threads << ")" << std::endl;
    }
    
    auto results = run_benchmark(matrix, num_threads, method, iterations, outer_threads, inner_threads);
    
    double sum_time = 0.0;
    double min_time = results[0].execution_time;
    double max_time = results[0].execution_time;
    
    for (const auto& result : results) {
        sum_time += result.execution_time;
        min_time = std::min(min_time, result.execution_time);
        max_time = std::max(max_time, result.execution_time);
    }
    
    double avg_time = sum_time / results.size();
    
    std::cout << "\nResults:" << std::endl;
    std::cout << "  Average time: " << std::fixed << std::setprecision(3) << avg_time << " ms" << std::endl;
    std::cout << "  Min time:     " << min_time << " ms" << std::endl;
    std::cout << "  Max time:     " << max_time << " ms" << std::endl;
    std::cout << "  Result value: " << std::setprecision(6) << results[0].result_value << std::endl;
    
    if (!output_file.empty()) {
        std::ofstream out(output_file, std::ios::app);
        if (out.is_open()) {
            out.seekp(0, std::ios::end);
            if (out.tellp() == 0) {
                out << "N,num_threads,outer_threads,inner_threads,method,iteration,execution_time_ms,result_value" << std::endl;
            }
            
            for (const auto& result : results) {
                out << result.N << ","
                    << result.num_threads << ","
                    << result.outer_threads << ","
                    << result.inner_threads << ","
                    << result.method << ","
                    << result.iteration << ","
                    << std::fixed << std::setprecision(6) << result.execution_time << ","
                    << std::scientific << std::setprecision(15) << result.result_value << std::endl;
            }
            out.close();
        }
    }
    
    return 0;
}
