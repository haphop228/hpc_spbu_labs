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
    string method;
    int num_threads;
    int array_size;
    double execution_time_ms;
    double result;
};

void initialize_array(vector<double>& arr, int seed = 42) {
    mt19937 gen(seed);
    uniform_real_distribution<double> dist(0.0, 100.0);
    
    for (size_t i = 0; i < arr.size(); ++i) {
        arr[i] = dist(gen);
    }
}

double reduction_sequential(const vector<double>& arr) {
    double sum = 0.0;
    
    for (size_t i = 0; i < arr.size(); ++i) {
        sum += arr[i];
    }
    
    return sum;
}

double reduction_builtin(const vector<double>& arr, int num_threads) {
    double sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(+:sum)
    for (size_t i = 0; i < arr.size(); ++i) {
        sum += arr[i];
    }
    
    return sum;
}

double reduction_atomic(const vector<double>& arr, int num_threads) {
    double sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel
    {
        double local_sum = 0.0;
        
        #pragma omp for
        for (size_t i = 0; i < arr.size(); ++i) {
            local_sum += arr[i];
        }
        
        #pragma omp atomic
        sum += local_sum;
    }
    
    return sum;
}

double reduction_critical(const vector<double>& arr, int num_threads) {
    double sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel
    {
        double local_sum = 0.0;
        
        #pragma omp for
        for (size_t i = 0; i < arr.size(); ++i) {
            local_sum += arr[i];
        }
        
        #pragma omp critical
        {
            sum += local_sum;
        }
    }
    
    return sum;
}

double reduction_lock(const vector<double>& arr, int num_threads) {
    double sum = 0.0;
    omp_lock_t lock;
    omp_init_lock(&lock);
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel
    {
        double local_sum = 0.0;
        
        #pragma omp for
        for (size_t i = 0; i < arr.size(); ++i) {
            local_sum += arr[i];
        }
        
        omp_set_lock(&lock);
        sum += local_sum;
        omp_unset_lock(&lock);
    }
    
    omp_destroy_lock(&lock);
    return sum;
}


BenchmarkResult run_benchmark(const string& method, const vector<double>& arr, 
                              int num_threads, int runs) {
    BenchmarkResult result;
    result.method = method;
    result.num_threads = num_threads;
    result.array_size = arr.size();
    
    double total_time = 0.0;
    double final_result = 0.0;
    
    for (int run = 0; run < runs; ++run) {
        auto start = chrono::high_resolution_clock::now();
        
        if (method == "sequential") {
            final_result = reduction_sequential(arr);
        } else if (method == "builtin") {
            final_result = reduction_builtin(arr, num_threads);
        } else if (method == "atomic") {
            final_result = reduction_atomic(arr, num_threads);
        } else if (method == "critical") {
            final_result = reduction_critical(arr, num_threads);
        } else if (method == "lock") {
            final_result = reduction_lock(arr, num_threads);
        }
        
        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double, milli> duration = end - start;
        total_time += duration.count();
    }
    
    result.execution_time_ms = total_time / runs;
    result.result = final_result;
    
    return result;
}


bool verify_correctness(int array_size) {
    cout << "\n=== Correctness Verification ===" << endl;
    
    vector<double> arr(array_size);
    initialize_array(arr);
    
    double sequential_result = reduction_sequential(arr);
    cout << "Sequential result: " << fixed << setprecision(6) << sequential_result << endl;
    
    bool all_passed = true;
    const double tolerance = 1e-6;
    int num_threads = 4;
    
    // Test built-in reduction
    double builtin_result = reduction_builtin(arr, num_threads);
    double builtin_error = abs(builtin_result - sequential_result);
    cout << "Built-in result:   " << builtin_result << " (error: " << scientific << builtin_error << ")" << endl;
    if (builtin_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    // Test atomic
    double atomic_result = reduction_atomic(arr, num_threads);
    double atomic_error = abs(atomic_result - sequential_result);
    cout << "Atomic result:     " << atomic_result << " (error: " << scientific << atomic_error << ")" << endl;
    if (atomic_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    // Test critical
    double critical_result = reduction_critical(arr, num_threads);
    double critical_error = abs(critical_result - sequential_result);
    cout << "Critical result:   " << critical_result << " (error: " << scientific << critical_error << ")" << endl;
    if (critical_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    // Test lock
    double lock_result = reduction_lock(arr, num_threads);
    double lock_error = abs(lock_result - sequential_result);
    cout << "Lock result:       " << lock_result << " (error: " << scientific << lock_error << ")" << endl;
    if (lock_error > tolerance) {
        cout << "  ✗ FAILED" << endl;
        all_passed = false;
    } else {
        cout << "  ✓ PASSED" << endl;
    }
    
    cout << fixed;
    return all_passed;
}

void print_usage(const char* program_name) {
    cout << "Usage: " << program_name << " <array_size> <num_threads> <method> <runs> [output_file]" << endl;
    cout << "\nParameters:" << endl;
    cout << "  array_size   - Size of the array (e.g., 1000000, 10000000, 100000000)" << endl;
    cout << "  num_threads  - Number of OpenMP threads (1, 2, 4, 8, 16, 32, 64, 128)" << endl;
    cout << "  method       - Synchronization method: sequential, builtin, atomic, critical, lock" << endl;
    cout << "  runs         - Number of runs for averaging" << endl;
    cout << "  output_file  - (Optional) CSV file to save results" << endl;
    cout << "\nMethods:" << endl;
    cout << "  sequential - Sequential execution (baseline)" << endl;
    cout << "  builtin    - OpenMP reduction clause (recommended)" << endl;
    cout << "  atomic     - Atomic operations (#pragma omp atomic)" << endl;
    cout << "  critical   - Critical sections (#pragma omp critical)" << endl;
    cout << "  lock       - Manual locks (omp_lock_t)" << endl;
    cout << "\nExamples:" << endl;
    cout << "  " << program_name << " 10000000 4 builtin 10" << endl;
    cout << "  " << program_name << " 10000000 8 atomic 10 results.csv" << endl;
    cout << "  " << program_name << " 100000000 16 critical 5" << endl;
}

int main(int argc, char* argv[]) {
    // Check for help flag
    if (argc == 2 && (string(argv[1]) == "-h" || string(argv[1]) == "--help")) {
        print_usage(argv[0]);
        return 0;
    }
    
    // Check for verification mode
    if (argc == 2 && string(argv[1]) == "--verify") {
        bool passed = verify_correctness(10000);
        return passed ? 0 : 1;
    }
    
    // Check arguments
    if (argc < 5) {
        cerr << "Error: Insufficient arguments" << endl;
        print_usage(argv[0]);
        return 1;
    }
    
    // Parse arguments
    int array_size = atoi(argv[1]);
    int num_threads = atoi(argv[2]);
    string method = argv[3];
    int runs = atoi(argv[4]);
    string output_file = (argc >= 6) ? argv[5] : "";
    
    // Validate arguments
    if (array_size <= 0 || num_threads <= 0 || runs <= 0) {
        cerr << "Error: Invalid arguments" << endl;
        return 1;
    }
    
    if (method != "sequential" && method != "builtin" && method != "atomic" && 
        method != "critical" && method != "lock") {
        cerr << "Error: Invalid method. Must be: sequential, builtin, atomic, critical, or lock" << endl;
        return 1;
    }
    
    // Print configuration
    cout << "=== Reduction Operations with Different Synchronization Methods ===" << endl;
    cout << "Array size:     " << array_size << endl;
    cout << "Threads:        " << num_threads << endl;
    cout << "Method:         " << method << endl;
    cout << "Runs:           " << runs << endl;
    cout << "OpenMP threads: " << omp_get_max_threads() << " available" << endl;
    cout << "\n=== Initializing Array ===" << endl;
    
    // Initialize array
    vector<double> arr(array_size);
    initialize_array(arr);
    cout << "Array initialized with " << array_size << " random values" << endl;
    
    cout << "\n=== Running Benchmark ===" << endl;
    
    // Run benchmark
    BenchmarkResult result = run_benchmark(method, arr, num_threads, runs);
    
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
            file << "array_size,num_threads,method,execution_time_ms,result" << endl;
        }
        
        file << array_size << ","
             << num_threads << ","
             << method << ","
             << fixed << setprecision(6) << result.execution_time_ms << ","
             << result.result << endl;
        
        file.close();
        cout << "\nResults saved to: " << output_file << endl;
    }
    
    return 0;
}
