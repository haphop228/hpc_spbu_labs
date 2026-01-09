#include <iostream>
#include <fstream>
#include <vector>
#include <random>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <omp.h>
#include <cmath>
#include <cfloat>

void initialize_vector(std::vector<double>& vec, unsigned int seed) {
    std::mt19937 gen(seed);
    std::uniform_real_distribution<double> dis(-100.0, 100.0);
    
    for (size_t i = 0; i < vec.size(); ++i) {
        vec[i] = dis(gen);
    }
}

double dot_product_sequential(const std::vector<double>& a, const std::vector<double>& b) {
    double result = 0.0;
    for (size_t i = 0; i < a.size(); ++i) {
        result += a[i] * b[i];
    }
    return result;
}

double dot_product_reduction(const std::vector<double>& a, const std::vector<double>& b, int num_threads) {
    double result = 0.0;
    size_t n = a.size();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(+:result)
    for (size_t i = 0; i < n; ++i) {
        result += a[i] * b[i];
    }
    
    return result;
}

double dot_product_no_reduction(const std::vector<double>& a, const std::vector<double>& b, int num_threads) {
    double result = 0.0;
    size_t n = a.size();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel
    {
        double local_sum = 0.0;
        
        #pragma omp for nowait
        for (size_t i = 0; i < n; ++i) {
            local_sum += a[i] * b[i];
        }
        
        #pragma omp critical
        {
            result += local_sum;
        }
    }
    
    return result;
}

struct BenchmarkResult {
    size_t vector_size;
    int num_threads;
    std::string method;
    double execution_time;
    double result_value;
    int iteration;
};

std::vector<BenchmarkResult> run_benchmark(size_t vector_size, int num_threads, 
                                           const std::string& method, int iterations) {
    std::vector<BenchmarkResult> results;
    
    std::vector<double> a(vector_size);
    std::vector<double> b(vector_size);
    initialize_vector(a, 12345);
    initialize_vector(b, 67890);
    
    for (int iter = 0; iter < iterations; ++iter) {
        double result = 0.0;
        double execution_time = 0.0;
        
        if (iter == 0) {
            if (method == "reduction") {
                dot_product_reduction(a, b, num_threads);
            } else if (method == "no-reduction") {
                dot_product_no_reduction(a, b, num_threads);
            }
        }
        
        auto start = std::chrono::high_resolution_clock::now();
        
        if (method == "reduction") {
            result = dot_product_reduction(a, b, num_threads);
        } else if (method == "no-reduction") {
            result = dot_product_no_reduction(a, b, num_threads);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        execution_time = std::chrono::duration<double, std::milli>(end - start).count();
        
        BenchmarkResult bench_result;
        bench_result.vector_size = vector_size;
        bench_result.num_threads = num_threads;
        bench_result.method = method;
        bench_result.execution_time = execution_time;
        bench_result.result_value = result;
        bench_result.iteration = iter;
        
        results.push_back(bench_result);
    }
    
    return results;
}

bool verify_correctness(size_t test_size = 10000) {
    std::vector<double> a(test_size);
    std::vector<double> b(test_size);
    initialize_vector(a, 12345);
    initialize_vector(b, 67890);
    
    double seq_result = dot_product_sequential(a, b);
    double par_reduction = dot_product_reduction(a, b, 4);
    double par_no_reduction = dot_product_no_reduction(a, b, 4);
    
    const double epsilon = 1e-6;
    double rel_error_reduction = std::abs((seq_result - par_reduction) / seq_result);
    double rel_error_no_reduction = std::abs((seq_result - par_no_reduction) / seq_result);
    
    bool reduction_ok = rel_error_reduction < epsilon;
    bool no_reduction_ok = rel_error_no_reduction < epsilon;
    
    return reduction_ok && no_reduction_ok;
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Usage: " << argv[0] << " <vector_size> <num_threads> <method> <iterations> [output_file]" << std::endl;
        std::cerr << "Methods: reduction, no-reduction" << std::endl;
        std::cerr << "Example: " << argv[0] << " 1000000 4 reduction 10" << std::endl;
        return 1;
    }
    
    size_t vector_size = std::stoull(argv[1]);
    int num_threads = std::stoi(argv[2]);
    std::string method = argv[3];
    int iterations = std::stoi(argv[4]);
    std::string output_file = (argc > 5) ? argv[5] : "";
    
    if (method != "reduction" && method != "no-reduction") {
        std::cerr << "Error: Invalid method '" << method << "'. Use 'reduction' or 'no-reduction'" << std::endl;
        return 1;
    }
    
    if (!verify_correctness()) {
        std::cerr << "Error: Correctness verification failed!" << std::endl;
        return 1;
    }

    auto results = run_benchmark(vector_size, num_threads, method, iterations);
    
    if (!output_file.empty()) {
        std::ofstream out(output_file, std::ios::app);
        if (out.is_open()) {
            out.seekp(0, std::ios::end);
            if (out.tellp() == 0) {
                out << "vector_size,num_threads,method,iteration,execution_time_ms,result_value" << std::endl;
            }
            
            for (const auto& result : results) {
                out << result.vector_size << ","
                    << result.num_threads << ","
                    << result.method << ","
                    << result.iteration << ","
                    << std::fixed << std::setprecision(6) << result.execution_time << ","
                    << std::scientific << std::setprecision(15) << result.result_value << std::endl;
            }
            out.close();
        } else {
            std::cerr << "Error: Could not open output file: " << output_file << std::endl;
        }
    }
    
    return 0;
}