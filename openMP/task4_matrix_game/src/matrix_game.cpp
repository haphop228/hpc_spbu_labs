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

double maximin_reduction(const Matrix& matrix, int num_threads) {
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


struct BenchmarkResult {
    int N;
    int num_threads;
    std::string method;
    double execution_time;
    double result_value;
    int iteration;
};

std::vector<BenchmarkResult> run_benchmark(const Matrix& matrix,
                                           int num_threads,
                                           const std::string& method,
                                           int iterations) {
    std::vector<BenchmarkResult> results;
    int N = matrix.size();
    
    // Warmup
    if (method == "reduction") {
        maximin_reduction(matrix, num_threads);
    }
    
    for (int iter = 0; iter < iterations; ++iter) {
        double result = 0.0;
        double execution_time = 0.0;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        if (method == "reduction") {
            result = maximin_reduction(matrix, num_threads);
        } else if (method == "sequential") {
            result = maximin_sequential(matrix);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        execution_time = std::chrono::duration<double, std::milli>(end - start).count();
        
        BenchmarkResult bench_result;
        bench_result.N = N;
        bench_result.num_threads = num_threads;
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
    
    // Test 1: Small matrix with known result
    {
        Matrix test_matrix = {
            {5.0, 3.0, 7.0},
            {2.0, 8.0, 1.0},
            {6.0, 4.0, 9.0}
        };
        
        double seq = maximin_sequential(test_matrix);
        double par_red = maximin_reduction(test_matrix, 2);
        
        // Expected: row mins are [3.0, 1.0, 4.0], max is 4.0
        double expected = 4.0;
        
        std::cout << "\nTest 1: 3x3 matrix (expected = " << expected << ")" << std::endl;
        std::cout << "  Sequential: " << std::fixed << std::setprecision(6) << seq
                  << " (error: " << std::abs(seq - expected) << ")" << std::endl;
        std::cout << "  Reduction:  " << par_red
                  << " (error: " << std::abs(par_red - expected) << ")" << std::endl;
        
        if (std::abs(seq - expected) > 1e-6 ||
            std::abs(par_red - expected) > 1e-6) {
            std::cout << "  ✗ FAILED" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED" << std::endl;
    }
    
    // Test 2: Larger random matrix - all methods should give same result
    {
        int N = 100;
        Matrix test_matrix = generate_matrix(N, 12345);
        
        double seq = maximin_sequential(test_matrix);
        double par_red = maximin_reduction(test_matrix, 4);
        
        std::cout << "\nTest 2: " << N << "x" << N << " random matrix" << std::endl;
        std::cout << "  Sequential: " << seq << std::endl;
        std::cout << "  Reduction:  " << par_red << std::endl;
        
        if (std::abs(seq - par_red) > 1e-6) {
            std::cout << "  ✗ FAILED - Methods give different results" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED - Both methods agree" << std::endl;
    }
    
    std::cout << "\n=== Verification Complete ===" << std::endl;
    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <N> <num_threads> <method> <iterations> [output_file]" << std::endl;
        std::cerr << "\nParameters:" << std::endl;
        std::cerr << "  N           - matrix size (NxN)" << std::endl;
        std::cerr << "  num_threads - number of OpenMP threads" << std::endl;
        std::cerr << "  method      - sequential, reduction" << std::endl;
        std::cerr << "  iterations  - number of runs for averaging" << std::endl;
        std::cerr << "\nExamples:" << std::endl;
        std::cerr << "  " << argv[0] << " 1000 4 reduction 10" << std::endl;
        std::cerr << "  " << argv[0] << " 5000 8 critical 5" << std::endl;
        return 1;
    }
    
    int N = std::stoi(argv[1]);
    int num_threads = std::stoi(argv[2]);
    std::string method = argv[3];
    int iterations = std::stoi(argv[4]);
    std::string output_file = (argc > 5) ? argv[5] : "";
    
    if (method != "sequential" && method != "reduction") {
        std::cerr << "Error: Invalid method '" << method << "'" << std::endl;
        return 1;
    }
    
    // Run verification
    if (!verify_correctness()) {
        std::cerr << "Error: Correctness verification failed!" << std::endl;
        return 1;
    }
    
    // Generate matrix
    std::cout << "\nGenerating " << N << "x" << N << " matrix..." << std::endl;
    Matrix matrix = generate_matrix(N);
    std::cout << "Matrix generated." << std::endl;
    
    // Run benchmark
    std::cout << "\nRunning benchmark..." << std::endl;
    auto results = run_benchmark(matrix, num_threads, method, iterations);
    
    // Calculate statistics
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
    
    // Save results to file if specified
    if (!output_file.empty()) {
        std::ofstream out(output_file, std::ios::app);
        if (out.is_open()) {
            out.seekp(0, std::ios::end);
            if (out.tellp() == 0) {
                out << "N,num_threads,method,iteration,execution_time_ms,result_value" << std::endl;
            }
            
            for (const auto& result : results) {
                out << result.N << ","
                    << result.num_threads << ","
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