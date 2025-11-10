/**
 * Task 8: Vector Dot Products with OpenMP Sections
 * 
 * This program computes dot products for a sequence of vector pairs.
 * It uses OpenMP sections directive to parallelize two separate tasks:
 * 1. Reading vectors from file (input task)
 * 2. Computing dot products (computation task)
 * 
 * The tasks are organized as separate sections that can run in parallel.
 */

#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <string>
#include <cmath>
#include <omp.h>

using namespace std;

// Structure to hold a pair of vectors
struct VectorPair {
    vector<double> vec1;
    vector<double> vec2;
    int id;
};

// Structure to hold computation result
struct DotProductResult {
    int pair_id;
    double result;
    double computation_time_ms;
};

// Structure to hold benchmark results
struct BenchmarkResult {
    string method;
    int num_threads;
    int num_pairs;
    int vector_size;
    double total_time_ms;
    double input_time_ms;
    double computation_time_ms;
    vector<DotProductResult> results;
};

/**
 * Generate test data file with vector pairs
 */
void generate_test_data(const string& filename, int num_pairs, int vector_size) {
    ofstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Cannot create file " << filename << endl;
        return;
    }
    
    // Write header: num_pairs, vector_size
    file << num_pairs << " " << vector_size << endl;
    
    // Generate random vector pairs
    srand(42); // Fixed seed for reproducibility
    for (int p = 0; p < num_pairs; ++p) {
        // Vector 1
        for (int i = 0; i < vector_size; ++i) {
            file << (rand() % 1000) / 10.0;
            if (i < vector_size - 1) file << " ";
        }
        file << endl;
        
        // Vector 2
        for (int i = 0; i < vector_size; ++i) {
            file << (rand() % 1000) / 10.0;
            if (i < vector_size - 1) file << " ";
        }
        file << endl;
    }
    
    file.close();
    cout << "Generated test data: " << filename << endl;
    cout << "  Pairs: " << num_pairs << ", Vector size: " << vector_size << endl;
}

/**
 * Compute dot product of two vectors
 */
double compute_dot_product(const vector<double>& vec1, const vector<double>& vec2) {
    double result = 0.0;
    for (size_t i = 0; i < vec1.size(); ++i) {
        result += vec1[i] * vec2[i];
    }
    return result;
}

/**
 * Sequential implementation (baseline)
 * Read all vectors, then compute all dot products
 */
BenchmarkResult sequential_method(const string& filename, int runs) {
    BenchmarkResult bench_result;
    bench_result.method = "sequential";
    bench_result.num_threads = 1;
    
    double total_input_time = 0.0;
    double total_computation_time = 0.0;
    vector<DotProductResult> final_results;
    
    for (int run = 0; run < runs; ++run) {
        // Input phase
        auto input_start = chrono::high_resolution_clock::now();
        
        ifstream file(filename);
        if (!file.is_open()) {
            cerr << "Error: Cannot open file " << filename << endl;
            return bench_result;
        }
        
        int num_pairs, vector_size;
        file >> num_pairs >> vector_size;
        
        vector<VectorPair> pairs(num_pairs);
        for (int p = 0; p < num_pairs; ++p) {
            pairs[p].id = p;
            pairs[p].vec1.resize(vector_size);
            pairs[p].vec2.resize(vector_size);
            
            for (int i = 0; i < vector_size; ++i) {
                file >> pairs[p].vec1[i];
            }
            for (int i = 0; i < vector_size; ++i) {
                file >> pairs[p].vec2[i];
            }
        }
        file.close();
        
        auto input_end = chrono::high_resolution_clock::now();
        chrono::duration<double, milli> input_duration = input_end - input_start;
        total_input_time += input_duration.count();
        
        // Computation phase
        auto comp_start = chrono::high_resolution_clock::now();
        
        vector<DotProductResult> results(num_pairs);
        for (int p = 0; p < num_pairs; ++p) {
            auto dot_start = chrono::high_resolution_clock::now();
            double dot_product = compute_dot_product(pairs[p].vec1, pairs[p].vec2);
            auto dot_end = chrono::high_resolution_clock::now();
            
            results[p].pair_id = p;
            results[p].result = dot_product;
            chrono::duration<double, milli> dot_duration = dot_end - dot_start;
            results[p].computation_time_ms = dot_duration.count();
        }
        
        auto comp_end = chrono::high_resolution_clock::now();
        chrono::duration<double, milli> comp_duration = comp_end - comp_start;
        total_computation_time += comp_duration.count();
        
        if (run == runs - 1) {
            final_results = results;
            bench_result.num_pairs = num_pairs;
            bench_result.vector_size = vector_size;
        }
    }
    
    bench_result.input_time_ms = total_input_time / runs;
    bench_result.computation_time_ms = total_computation_time / runs;
    bench_result.total_time_ms = bench_result.input_time_ms + bench_result.computation_time_ms;
    bench_result.results = final_results;
    
    return bench_result;
}

/**
 * Parallel implementation using OpenMP sections
 * Uses sections to parallelize input and computation tasks
 */
BenchmarkResult sections_method(const string& filename, int num_threads, int runs) {
    BenchmarkResult bench_result;
    bench_result.method = "sections";
    bench_result.num_threads = num_threads;
    
    omp_set_num_threads(num_threads);
    
    double total_time = 0.0;
    double total_input_time = 0.0;
    double total_computation_time = 0.0;
    vector<DotProductResult> final_results;
    
    for (int run = 0; run < runs; ++run) {
        auto total_start = chrono::high_resolution_clock::now();
        
        // Shared data structures
        vector<VectorPair> input_buffer;
        vector<VectorPair> compute_buffer;
        vector<DotProductResult> results;
        
        int num_pairs = 0;
        int vector_size = 0;
        bool input_done = false;
        bool computation_done = false;
        
        double input_time = 0.0;
        double computation_time = 0.0;
        
        // Read metadata first
        ifstream meta_file(filename);
        meta_file >> num_pairs >> vector_size;
        meta_file.close();
        
        results.resize(num_pairs);
        
        #pragma omp parallel sections
        {
            // Section 1: Input task - read vectors from file
            #pragma omp section
            {
                auto input_start = chrono::high_resolution_clock::now();
                
                ifstream file(filename);
                int np, vs;
                file >> np >> vs;
                
                for (int p = 0; p < np; ++p) {
                    VectorPair pair;
                    pair.id = p;
                    pair.vec1.resize(vs);
                    pair.vec2.resize(vs);
                    
                    for (int i = 0; i < vs; ++i) {
                        file >> pair.vec1[i];
                    }
                    for (int i = 0; i < vs; ++i) {
                        file >> pair.vec2[i];
                    }
                    
                    // Add to compute buffer for processing
                    #pragma omp critical
                    {
                        compute_buffer.push_back(pair);
                    }
                }
                file.close();
                
                #pragma omp critical
                {
                    input_done = true;
                }
                
                auto input_end = chrono::high_resolution_clock::now();
                chrono::duration<double, milli> duration = input_end - input_start;
                input_time = duration.count();
            }
            
            // Section 2: Computation task - compute dot products
            #pragma omp section
            {
                auto comp_start = chrono::high_resolution_clock::now();
                
                int processed = 0;
                while (processed < num_pairs) {
                    VectorPair pair;
                    bool has_work = false;
                    
                    // Get next pair to process
                    #pragma omp critical
                    {
                        if (!compute_buffer.empty()) {
                            pair = compute_buffer.front();
                            compute_buffer.erase(compute_buffer.begin());
                            has_work = true;
                        }
                    }
                    
                    if (has_work) {
                        auto dot_start = chrono::high_resolution_clock::now();
                        double dot_product = compute_dot_product(pair.vec1, pair.vec2);
                        auto dot_end = chrono::high_resolution_clock::now();
                        
                        results[pair.id].pair_id = pair.id;
                        results[pair.id].result = dot_product;
                        chrono::duration<double, milli> dot_duration = dot_end - dot_start;
                        results[pair.id].computation_time_ms = dot_duration.count();
                        
                        processed++;
                    } else {
                        // Check if input is done
                        bool done = false;
                        #pragma omp critical
                        {
                            done = input_done;
                        }
                        if (!done) {
                            // Wait a bit for more data
                            #pragma omp taskyield
                        }
                    }
                }
                
                #pragma omp critical
                {
                    computation_done = true;
                }
                
                auto comp_end = chrono::high_resolution_clock::now();
                chrono::duration<double, milli> duration = comp_end - comp_start;
                computation_time = duration.count();
            }
        }
        
        auto total_end = chrono::high_resolution_clock::now();
        chrono::duration<double, milli> total_duration = total_end - total_start;
        total_time += total_duration.count();
        total_input_time += input_time;
        total_computation_time += computation_time;
        
        if (run == runs - 1) {
            final_results = results;
            bench_result.num_pairs = num_pairs;
            bench_result.vector_size = vector_size;
        }
    }
    
    bench_result.total_time_ms = total_time / runs;
    bench_result.input_time_ms = total_input_time / runs;
    bench_result.computation_time_ms = total_computation_time / runs;
    bench_result.results = final_results;
    
    return bench_result;
}

/**
 * Verify correctness by comparing results
 */
bool verify_correctness(const string& filename) {
    cout << "\n=== Correctness Verification ===" << endl;
    
    BenchmarkResult seq_result = sequential_method(filename, 1);
    BenchmarkResult par_result = sections_method(filename, 2, 1);
    
    cout << "Sequential results:" << endl;
    for (size_t i = 0; i < min(size_t(5), seq_result.results.size()); ++i) {
        cout << "  Pair " << i << ": " << fixed << setprecision(6) 
             << seq_result.results[i].result << endl;
    }
    
    cout << "\nParallel (sections) results:" << endl;
    for (size_t i = 0; i < min(size_t(5), par_result.results.size()); ++i) {
        cout << "  Pair " << i << ": " << fixed << setprecision(6) 
             << par_result.results[i].result << endl;
    }
    
    bool all_passed = true;
    const double tolerance = 1e-6;
    
    for (size_t i = 0; i < seq_result.results.size(); ++i) {
        double error = abs(seq_result.results[i].result - par_result.results[i].result);
        if (error > tolerance) {
            cout << "\n✗ FAILED: Pair " << i << " mismatch (error: " << error << ")" << endl;
            all_passed = false;
        }
    }
    
    if (all_passed) {
        cout << "\n✓ PASSED: All results match!" << endl;
    }
    
    return all_passed;
}

/**
 * Print usage information
 */
void print_usage(const char* program_name) {
    cout << "Usage: " << program_name << " <command> [options]" << endl;
    cout << "\nCommands:" << endl;
    cout << "  generate <num_pairs> <vector_size> <output_file>" << endl;
    cout << "    Generate test data file with vector pairs" << endl;
    cout << "\n  benchmark <data_file> <num_threads> <method> <runs> [output_file]" << endl;
    cout << "    Run benchmark on existing data file" << endl;
    cout << "    method: sequential, sections" << endl;
    cout << "\n  verify <data_file>" << endl;
    cout << "    Verify correctness of parallel implementation" << endl;
    cout << "\nExamples:" << endl;
    cout << "  " << program_name << " generate 100 1000 data/vectors.txt" << endl;
    cout << "  " << program_name << " benchmark data/vectors.txt 4 sections 10" << endl;
    cout << "  " << program_name << " verify data/vectors.txt" << endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }
    
    string command = argv[1];
    
    if (command == "generate") {
        if (argc < 5) {
            cerr << "Error: Insufficient arguments for generate" << endl;
            print_usage(argv[0]);
            return 1;
        }
        
        int num_pairs = atoi(argv[2]);
        int vector_size = atoi(argv[3]);
        string output_file = argv[4];
        
        generate_test_data(output_file, num_pairs, vector_size);
        
    } else if (command == "benchmark") {
        if (argc < 6) {
            cerr << "Error: Insufficient arguments for benchmark" << endl;
            print_usage(argv[0]);
            return 1;
        }
        
        string data_file = argv[2];
        int num_threads = atoi(argv[3]);
        string method = argv[4];
        int runs = atoi(argv[5]);
        string output_file = (argc >= 7) ? argv[6] : "";
        
        cout << "=== Vector Dot Products with OpenMP Sections ===" << endl;
        cout << "Data file:      " << data_file << endl;
        cout << "Threads:        " << num_threads << endl;
        cout << "Method:         " << method << endl;
        cout << "Runs:           " << runs << endl;
        cout << "OpenMP threads: " << omp_get_max_threads() << " available" << endl;
        
        BenchmarkResult result;
        if (method == "sequential") {
            result = sequential_method(data_file, runs);
        } else if (method == "sections") {
            result = sections_method(data_file, num_threads, runs);
        } else {
            cerr << "Error: Invalid method. Must be: sequential or sections" << endl;
            return 1;
        }
        
        cout << "\n=== Results ===" << endl;
        cout << "Vector pairs:   " << result.num_pairs << endl;
        cout << "Vector size:    " << result.vector_size << endl;
        cout << "Total time:     " << fixed << setprecision(3) << result.total_time_ms << " ms" << endl;
        cout << "Input time:     " << result.input_time_ms << " ms" << endl;
        cout << "Compute time:   " << result.computation_time_ms << " ms" << endl;
        
        // Save to file if specified
        if (!output_file.empty()) {
            ofstream file;
            bool file_exists = ifstream(output_file).good();
            file.open(output_file, ios::app);
            
            if (!file_exists) {
                file << "num_pairs,vector_size,num_threads,method,total_time_ms,input_time_ms,computation_time_ms" << endl;
            }
            
            file << result.num_pairs << ","
                 << result.vector_size << ","
                 << result.num_threads << ","
                 << result.method << ","
                 << fixed << setprecision(6) << result.total_time_ms << ","
                 << result.input_time_ms << ","
                 << result.computation_time_ms << endl;
            
            file.close();
            cout << "\nResults saved to: " << output_file << endl;
        }
        
    } else if (command == "verify") {
        if (argc < 3) {
            cerr << "Error: Insufficient arguments for verify" << endl;
            print_usage(argv[0]);
            return 1;
        }
        
        string data_file = argv[2];
        bool passed = verify_correctness(data_file);
        return passed ? 0 : 1;
        
    } else {
        cerr << "Error: Unknown command: " << command << endl;
        print_usage(argv[0]);
        return 1;
    }
    
    return 0;
}