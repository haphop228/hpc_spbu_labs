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

// Matrix types
enum class MatrixType {
    DENSE,
    BANDED,
    LOWER_TRIANGULAR,
    UPPER_TRIANGULAR
};

// Scheduling types
enum class ScheduleType {
    STATIC,
    DYNAMIC,
    GUIDED
};

// Matrix class for special types
class SpecialMatrix {
private:
    std::vector<std::vector<double>> data;
    int N;
    MatrixType type;
    int bandwidth; // for banded matrices
    
public:
    SpecialMatrix(int size, MatrixType mat_type, int band = 5, int seed = 42)
        : N(size), type(mat_type), bandwidth(band) {
        data.resize(N, std::vector<double>(N, 0.0));
        generate(seed);
    }
    
    void generate(int seed) {
        std::mt19937 gen(seed);
        std::uniform_real_distribution<> dis(-100.0, 100.0);
        
        switch (type) {
            case MatrixType::DENSE:
                // Full matrix
                for (int i = 0; i < N; ++i) {
                    for (int j = 0; j < N; ++j) {
                        data[i][j] = dis(gen);
                    }
                }
                break;
                
            case MatrixType::BANDED:
                // Banded matrix: non-zero only within bandwidth from diagonal
                for (int i = 0; i < N; ++i) {
                    for (int j = 0; j < N; ++j) {
                        if (std::abs(i - j) <= bandwidth) {
                            data[i][j] = dis(gen);
                        } else {
                            data[i][j] = 0.0;
                        }
                    }
                }
                break;
                
            case MatrixType::LOWER_TRIANGULAR:
                // Lower triangular: non-zero only when i >= j
                for (int i = 0; i < N; ++i) {
                    for (int j = 0; j <= i; ++j) {
                        data[i][j] = dis(gen);
                    }
                }
                break;
                
            case MatrixType::UPPER_TRIANGULAR:
                // Upper triangular: non-zero only when i <= j
                for (int i = 0; i < N; ++i) {
                    for (int j = i; j < N; ++j) {
                        data[i][j] = dis(gen);
                    }
                }
                break;
        }
    }
    
    double get(int i, int j) const {
        return data[i][j];
    }
    
    int size() const { return N; }
    
    MatrixType getType() const { return type; }
    
    int getBandwidth() const { return bandwidth; }
    
    // Get row minimum considering matrix structure
    double getRowMin(int row) const {
        double row_min = std::numeric_limits<double>::max();
        
        switch (type) {
            case MatrixType::DENSE:
                for (int j = 0; j < N; ++j) {
                    row_min = std::min(row_min, data[row][j]);
                }
                break;
                
            case MatrixType::BANDED:
                // Only check within bandwidth
                {
                    int j_start = std::max(0, row - bandwidth);
                    int j_end = std::min(N - 1, row + bandwidth);
                    for (int j = j_start; j <= j_end; ++j) {
                        row_min = std::min(row_min, data[row][j]);
                    }
                }
                break;
                
            case MatrixType::LOWER_TRIANGULAR:
                // Only check j <= row
                for (int j = 0; j <= row; ++j) {
                    row_min = std::min(row_min, data[row][j]);
                }
                break;
                
            case MatrixType::UPPER_TRIANGULAR:
                // Only check j >= row
                for (int j = row; j < N; ++j) {
                    row_min = std::min(row_min, data[row][j]);
                }
                break;
        }
        
        return row_min;
    }
};

// Convert string to MatrixType
MatrixType stringToMatrixType(const std::string& str) {
    if (str == "dense") return MatrixType::DENSE;
    if (str == "banded") return MatrixType::BANDED;
    if (str == "lower") return MatrixType::LOWER_TRIANGULAR;
    if (str == "upper") return MatrixType::UPPER_TRIANGULAR;
    return MatrixType::DENSE;
}

// Convert string to ScheduleType
ScheduleType stringToScheduleType(const std::string& str) {
    if (str == "static") return ScheduleType::STATIC;
    if (str == "dynamic") return ScheduleType::DYNAMIC;
    if (str == "guided") return ScheduleType::GUIDED;
    return ScheduleType::STATIC;
}

// Convert MatrixType to string
std::string matrixTypeToString(MatrixType type) {
    switch (type) {
        case MatrixType::DENSE: return "dense";
        case MatrixType::BANDED: return "banded";
        case MatrixType::LOWER_TRIANGULAR: return "lower";
        case MatrixType::UPPER_TRIANGULAR: return "upper";
        default: return "unknown";
    }
}

// Convert ScheduleType to string
std::string scheduleTypeToString(ScheduleType type) {
    switch (type) {
        case ScheduleType::STATIC: return "static";
        case ScheduleType::DYNAMIC: return "dynamic";
        case ScheduleType::GUIDED: return "guided";
        default: return "unknown";
    }
}

// Sequential method
double maximin_sequential(const SpecialMatrix& matrix) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    for (int i = 0; i < N; ++i) {
        double row_min = matrix.getRowMin(i);
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}

// Parallel method with different scheduling strategies
double maximin_parallel(const SpecialMatrix& matrix, int num_threads, ScheduleType schedule, int chunk_size = 0) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    omp_set_num_threads(num_threads);
    
    switch (schedule) {
        case ScheduleType::STATIC:
            if (chunk_size > 0) {
                #pragma omp parallel for schedule(static, chunk_size) reduction(max:max_of_mins)
                for (int i = 0; i < N; ++i) {
                    double row_min = matrix.getRowMin(i);
                    max_of_mins = std::max(max_of_mins, row_min);
                }
            } else {
                #pragma omp parallel for schedule(static) reduction(max:max_of_mins)
                for (int i = 0; i < N; ++i) {
                    double row_min = matrix.getRowMin(i);
                    max_of_mins = std::max(max_of_mins, row_min);
                }
            }
            break;
            
        case ScheduleType::DYNAMIC:
            if (chunk_size > 0) {
                #pragma omp parallel for schedule(dynamic, chunk_size) reduction(max:max_of_mins)
                for (int i = 0; i < N; ++i) {
                    double row_min = matrix.getRowMin(i);
                    max_of_mins = std::max(max_of_mins, row_min);
                }
            } else {
                #pragma omp parallel for schedule(dynamic) reduction(max:max_of_mins)
                for (int i = 0; i < N; ++i) {
                    double row_min = matrix.getRowMin(i);
                    max_of_mins = std::max(max_of_mins, row_min);
                }
            }
            break;
            
        case ScheduleType::GUIDED:
            if (chunk_size > 0) {
                #pragma omp parallel for schedule(guided, chunk_size) reduction(max:max_of_mins)
                for (int i = 0; i < N; ++i) {
                    double row_min = matrix.getRowMin(i);
                    max_of_mins = std::max(max_of_mins, row_min);
                }
            } else {
                #pragma omp parallel for schedule(guided) reduction(max:max_of_mins)
                for (int i = 0; i < N; ++i) {
                    double row_min = matrix.getRowMin(i);
                    max_of_mins = std::max(max_of_mins, row_min);
                }
            }
            break;
    }
    
    return max_of_mins;
}

struct BenchmarkResult {
    int N;
    std::string matrix_type;
    int bandwidth;
    int num_threads;
    std::string schedule;
    int chunk_size;
    double execution_time;
    double result_value;
    int iteration;
};

std::vector<BenchmarkResult> run_benchmark(const SpecialMatrix& matrix,
                                          int num_threads,
                                          ScheduleType schedule,
                                          int chunk_size,
                                          int iterations) {
    std::vector<BenchmarkResult> results;
    int N = matrix.size();
    
    // Warmup
    maximin_parallel(matrix, num_threads, schedule, chunk_size);
    
    for (int iter = 0; iter < iterations; ++iter) {
        auto start = std::chrono::high_resolution_clock::now();
        double result = maximin_parallel(matrix, num_threads, schedule, chunk_size);
        auto end = std::chrono::high_resolution_clock::now();
        
        double execution_time = std::chrono::duration<double, std::milli>(end - start).count();
        
        BenchmarkResult bench_result;
        bench_result.N = N;
        bench_result.matrix_type = matrixTypeToString(matrix.getType());
        bench_result.bandwidth = matrix.getBandwidth();
        bench_result.num_threads = num_threads;
        bench_result.schedule = scheduleTypeToString(schedule);
        bench_result.chunk_size = chunk_size;
        bench_result.execution_time = execution_time;
        bench_result.result_value = result;
        bench_result.iteration = iter;
        
        results.push_back(bench_result);
    }
    
    return results;
}

bool verify_correctness() {
    std::cout << "\n=== Correctness Verification ===" << std::endl;
    
    // Test 1: Small dense matrix
    {
        SpecialMatrix test_matrix(3, MatrixType::DENSE, 0, 12345);
        
        double seq = maximin_sequential(test_matrix);
        double par_static = maximin_parallel(test_matrix, 2, ScheduleType::STATIC, 0);
        double par_dynamic = maximin_parallel(test_matrix, 2, ScheduleType::DYNAMIC, 0);
        double par_guided = maximin_parallel(test_matrix, 2, ScheduleType::GUIDED, 0);
        
        std::cout << "\nTest 1: 3x3 dense matrix" << std::endl;
        std::cout << "  Sequential: " << std::fixed << std::setprecision(6) << seq << std::endl;
        std::cout << "  Static:     " << par_static << std::endl;
        std::cout << "  Dynamic:    " << par_dynamic << std::endl;
        std::cout << "  Guided:     " << par_guided << std::endl;
        
        if (std::abs(seq - par_static) > 1e-6 ||
            std::abs(seq - par_dynamic) > 1e-6 ||
            std::abs(seq - par_guided) > 1e-6) {
            std::cout << "  ✗ FAILED" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED" << std::endl;
    }
    
    // Test 2: Banded matrix
    {
        SpecialMatrix test_matrix(100, MatrixType::BANDED, 5, 54321);
        
        double seq = maximin_sequential(test_matrix);
        double par_static = maximin_parallel(test_matrix, 4, ScheduleType::STATIC, 0);
        double par_dynamic = maximin_parallel(test_matrix, 4, ScheduleType::DYNAMIC, 0);
        double par_guided = maximin_parallel(test_matrix, 4, ScheduleType::GUIDED, 0);
        
        std::cout << "\nTest 2: 100x100 banded matrix (bandwidth=5)" << std::endl;
        std::cout << "  Sequential: " << seq << std::endl;
        std::cout << "  Static:     " << par_static << std::endl;
        std::cout << "  Dynamic:    " << par_dynamic << std::endl;
        std::cout << "  Guided:     " << par_guided << std::endl;
        
        if (std::abs(seq - par_static) > 1e-6 ||
            std::abs(seq - par_dynamic) > 1e-6 ||
            std::abs(seq - par_guided) > 1e-6) {
            std::cout << "  ✗ FAILED" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED" << std::endl;
    }
    
    // Test 3: Lower triangular matrix
    {
        SpecialMatrix test_matrix(100, MatrixType::LOWER_TRIANGULAR, 0, 11111);
        
        double seq = maximin_sequential(test_matrix);
        double par = maximin_parallel(test_matrix, 4, ScheduleType::STATIC, 0);
        
        std::cout << "\nTest 3: 100x100 lower triangular matrix" << std::endl;
        std::cout << "  Sequential: " << seq << std::endl;
        std::cout << "  Parallel:   " << par << std::endl;
        
        if (std::abs(seq - par) > 1e-6) {
            std::cout << "  ✗ FAILED" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED" << std::endl;
    }
    
    // Test 4: Upper triangular matrix
    {
        SpecialMatrix test_matrix(100, MatrixType::UPPER_TRIANGULAR, 0, 22222);
        
        double seq = maximin_sequential(test_matrix);
        double par = maximin_parallel(test_matrix, 4, ScheduleType::DYNAMIC, 0);
        
        std::cout << "\nTest 4: 100x100 upper triangular matrix" << std::endl;
        std::cout << "  Sequential: " << seq << std::endl;
        std::cout << "  Parallel:   " << par << std::endl;
        
        if (std::abs(seq - par) > 1e-6) {
            std::cout << "  ✗ FAILED" << std::endl;
            return false;
        }
        std::cout << "  ✓ PASSED" << std::endl;
    }
    
    std::cout << "\n=== Verification Complete ===" << std::endl;
    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 7) {
        std::cerr << "Usage: " << argv[0] << " <N> <matrix_type> <bandwidth> <num_threads> <schedule> <chunk_size> <iterations> [output_file]" << std::endl;
        std::cerr << "\nParameters:" << std::endl;
        std::cerr << "  N           - matrix size (NxN)" << std::endl;
        std::cerr << "  matrix_type - dense, banded, lower, upper" << std::endl;
        std::cerr << "  bandwidth   - bandwidth for banded matrices (ignored for others)" << std::endl;
        std::cerr << "  num_threads - number of OpenMP threads" << std::endl;
        std::cerr << "  schedule    - static, dynamic, guided" << std::endl;
        std::cerr << "  chunk_size  - chunk size for scheduling (0 = default)" << std::endl;
        std::cerr << "  iterations  - number of runs for averaging" << std::endl;
        std::cerr << "\nExamples:" << std::endl;
        std::cerr << "  " << argv[0] << " 1000 banded 5 4 static 0 10" << std::endl;
        std::cerr << "  " << argv[0] << " 2000 lower 0 8 dynamic 10 5" << std::endl;
        std::cerr << "  " << argv[0] << " 3000 upper 0 16 guided 0 10" << std::endl;
        return 1;
    }
    
    int N = std::stoi(argv[1]);
    std::string matrix_type_str = argv[2];
    int bandwidth = std::stoi(argv[3]);
    int num_threads = std::stoi(argv[4]);
    std::string schedule_str = argv[5];
    int chunk_size = std::stoi(argv[6]);
    int iterations = std::stoi(argv[7]);
    std::string output_file = (argc > 8) ? argv[8] : "";
    
    MatrixType matrix_type = stringToMatrixType(matrix_type_str);
    ScheduleType schedule = stringToScheduleType(schedule_str);
    
    // Run verification
    if (!verify_correctness()) {
        std::cerr << "Error: Correctness verification failed!" << std::endl;
        return 1;
    }
    
    // Generate matrix
    std::cout << "\nGenerating " << N << "x" << N << " " << matrix_type_str << " matrix";
    if (matrix_type == MatrixType::BANDED) {
        std::cout << " (bandwidth=" << bandwidth << ")";
    }
    std::cout << "..." << std::endl;
    
    SpecialMatrix matrix(N, matrix_type, bandwidth);
    std::cout << "Matrix generated." << std::endl;
    
    // Run benchmark
    std::cout << "\nRunning benchmark..." << std::endl;
    auto results = run_benchmark(matrix, num_threads, schedule, chunk_size, iterations);
    
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
                out << "N,matrix_type,bandwidth,num_threads,schedule,chunk_size,iteration,execution_time_ms,result_value" << std::endl;
            }
            
            for (const auto& result : results) {
                out << result.N << ","
                    << result.matrix_type << ","
                    << result.bandwidth << ","
                    << result.num_threads << ","
                    << result.schedule << ","
                    << result.chunk_size << ","
                    << result.iteration << ","
                    << std::fixed << std::setprecision(6) << result.execution_time << ","
                    << std::scientific << std::setprecision(15) << result.result_value << std::endl;
            }
            out.close();
        }
    }
    
    return 0;
}