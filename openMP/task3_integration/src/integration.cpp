
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <omp.h>
#include <cmath>
#include <string>

double test_function_1(double x) {
    // f(x) = x^2
    return x * x;
}

double test_function_2(double x) {
    // f(x) = sin(x)
    return std::sin(x);
}

double test_function_3(double x) {
    // f(x) = e^x
    return std::exp(x);
}

double test_function_4(double x) {
    // f(x) = 1/(1+x^2) - for testing arctangent
    return 1.0 / (1.0 + x * x);
}

double test_function_5(double x) {
    // f(x) = sqrt(1-x^2) - for testing circle area
    return std::sqrt(1.0 - x * x);
}

typedef double (*FunctionPtr)(double);

FunctionPtr get_function(const std::string& name) {
    if (name == "x2") return test_function_1;
    if (name == "sin") return test_function_2;
    if (name == "exp") return test_function_3;
    if (name == "arctan") return test_function_4;
    if (name == "circle") return test_function_5;
    return test_function_1;
}

double integrate_sequential(FunctionPtr f, double a, double b, long long N) {
    double h = (b - a) / N;
    double sum = 0.0;
    
    for (long long i = 0; i < N; ++i) {
        double x_i = a + i * h;
        sum += f(x_i);
    }
    
    return h * sum;
}

double integrate_reduction(FunctionPtr f, double a, double b, long long N, int num_threads) {
    double h = (b - a) / N;
    double sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(+:sum)
    for (long long i = 0; i < N; ++i) {
        double x_i = a + i * h;
        sum += f(x_i);
    }
    
    return h * sum;
}

struct BenchmarkResult {
    long long N;
    int num_threads;
    std::string method;
    std::string function;
    double a;
    double b;
    double execution_time;
    double result_value;
    int iteration;
};

std::vector<BenchmarkResult> run_benchmark(const std::string& function_name,
                                           double a, double b, long long N,
                                           int num_threads, const std::string& method,
                                           int iterations) {
    std::vector<BenchmarkResult> results;
    FunctionPtr f = get_function(function_name);
    
    if (method == "reduction") {
        integrate_reduction(f, a, b, N, num_threads);
    }
    
    for (int iter = 0; iter < iterations; ++iter) {
        double result = 0.0;
        double execution_time = 0.0;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        if (method == "reduction") {
            result = integrate_reduction(f, a, b, N, num_threads);
        } else if (method == "sequential") {
            result = integrate_sequential(f, a, b, N);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        execution_time = std::chrono::duration<double, std::milli>(end - start).count();
        
        BenchmarkResult bench_result;
        bench_result.N = N;
        bench_result.num_threads = num_threads;
        bench_result.method = method;
        bench_result.function = function_name;
        bench_result.a = a;
        bench_result.b = b;
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
        double a = 0.0, b = 1.0;
        long long N = 1000000;
        double exact = 1.0 / 3.0;
        
        double seq = integrate_sequential(test_function_1, a, b, N);
        double par_red = integrate_reduction(test_function_1, a, b, N, 4);
        
        std::cout << "\nTest 1: ∫₀¹ x² dx (exact = " << exact << ")" << std::endl;
        std::cout << "  Sequential:   " << std::fixed << std::setprecision(10) << seq 
                  << " (error: " << std::abs(seq - exact) << ")" << std::endl;
        std::cout << "  Reduction:    " << par_red 
                  << " (error: " << std::abs(par_red - exact) << ")" << std::endl;
    }
    
    {
        double a = 0.0, b = M_PI;
        long long N = 1000000;
        double exact = 2.0;
        
        double seq = integrate_sequential(test_function_2, a, b, N);
        double par_red = integrate_reduction(test_function_2, a, b, N, 4);
        
        std::cout << "\nTest 2: ∫₀^π sin(x) dx (exact = " << exact << ")" << std::endl;
        std::cout << "  Sequential: " << seq << " (error: " << std::abs(seq - exact) << ")" << std::endl;
        std::cout << "  Reduction:  " << par_red << " (error: " << std::abs(par_red - exact) << ")" << std::endl;
    }
    
    // Test 3: 1/(1+x²) from 0 to 1, exact = π/4
    {
        double a = 0.0, b = 1.0;
        long long N = 1000000;
        double exact = M_PI / 4.0;
        
        double seq = integrate_sequential(test_function_4, a, b, N);
        double par_red = integrate_reduction(test_function_4, a, b, N, 4);
        
        std::cout << "\nTest 3: ∫₀¹ 1/(1+x²) dx (exact = π/4 = " << exact << ")" << std::endl;
        std::cout << "  Sequential: " << seq << " (error: " << std::abs(seq - exact) << ")" << std::endl;
        std::cout << "  Reduction:  " << par_red << " (error: " << std::abs(par_red - exact) << ")" << std::endl;
    }
    
    std::cout << "\n=== Verification Complete ===" << std::endl;
    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 8) {
        std::cerr << "Usage: " << argv[0] << " <function> <a> <b> <N> <num_threads> <method> <iterations> [output_file]" << std::endl;
        std::cerr << "\nFunctions: x2, sin, exp, arctan, circle" << std::endl;
        std::cerr << "Methods: sequential, reduction" << std::endl;
        std::cerr << "\nExamples:" << std::endl;
        std::cerr << "  " << argv[0] << " x2 0 1 1000000 4 reduction 10" << std::endl;
        std::cerr << "  " << argv[0] << " sin 0 3.14159 10000000 8 reduction 5" << std::endl;
        return 1;
    }
    
    std::string function_name = argv[1];
    double a = std::stod(argv[2]);
    double b = std::stod(argv[3]);
    long long N = std::stoll(argv[4]);
    int num_threads = std::stoi(argv[5]);
    std::string method = argv[6];
    int iterations = std::stoi(argv[7]);
    std::string output_file = (argc > 8) ? argv[8] : "";
    
    if (method != "sequential" && method != "reduction") {
        std::cerr << "Error: Invalid method '" << method << "'" << std::endl;
        return 1;
    }
    
    // Run verification
    if (!verify_correctness()) {
        std::cerr << "Error: Correctness verification failed!" << std::endl;
        return 1;
    }
    
    // Run benchmark
    auto results = run_benchmark(function_name, a, b, N, num_threads, method, iterations);
    
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
    
    // Save results to file if specified
    if (!output_file.empty()) {
        std::ofstream out(output_file, std::ios::app);
        if (out.is_open()) {
            out.seekp(0, std::ios::end);
            if (out.tellp() == 0) {
                out << "function,a,b,N,num_threads,method,iteration,execution_time_ms,result_value" << std::endl;
            }
            
            for (const auto& result : results) {
                out << result.function << ","
                    << std::fixed << std::setprecision(6) << result.a << ","
                    << result.b << ","
                    << result.N << ","
                    << result.num_threads << ","
                    << result.method << ","
                    << result.iteration << ","
                    << result.execution_time << ","
                    << std::scientific << std::setprecision(15) << result.result_value << std::endl;
            }
            out.close();
        }
    }
    
    return 0;
}
