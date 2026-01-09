#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <string>
#include <cmath>
#include <queue>
#include <atomic>
#include <omp.h>

using namespace std;

struct VectorPair {
    vector<double> vec1;
    vector<double> vec2;
    int id;
};

struct DotProductResult {
    int pair_id;
    double result;
    double computation_time_ms;
};

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

// Потокобезопасная очередь для producer-consumer паттерна
class ThreadSafeQueue {
private:
    queue<VectorPair> q;
    omp_lock_t lock;
    
public:
    ThreadSafeQueue() {
        omp_init_lock(&lock);
    }
    
    ~ThreadSafeQueue() {
        omp_destroy_lock(&lock);
    }
    
    void push(const VectorPair& item) {
        omp_set_lock(&lock);
        q.push(item);
        omp_unset_lock(&lock);
    }
    
    bool try_pop(VectorPair& item) {
        omp_set_lock(&lock);
        if (q.empty()) {
            omp_unset_lock(&lock);
            return false;
        }
        item = q.front();
        q.pop();
        omp_unset_lock(&lock);
        return true;
    }
    
    size_t size() {
        omp_set_lock(&lock);
        size_t s = q.size();
        omp_unset_lock(&lock);
        return s;
    }
    
    bool empty() {
        omp_set_lock(&lock);
        bool e = q.empty();
        omp_unset_lock(&lock);
        return e;
    }
};

void generate_test_data(const string& filename, int num_pairs, int vector_size) {
    ofstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Cannot create file " << filename << endl;
        return;
    }
    
    file << num_pairs << " " << vector_size << endl;
    
    srand(42);
    for (int p = 0; p < num_pairs; ++p) {
        for (int i = 0; i < vector_size; ++i) {
            file << (rand() % 1000) / 10.0;
            if (i < vector_size - 1) file << " ";
        }
        file << endl;
        
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

// Вычисление скалярного произведения с утяжелением для демонстрации
double compute_dot_product(const vector<double>& vec1, const vector<double>& vec2) {
    double result = 0.0;
    
    // Утяжеление вычислений для демонстрации эффекта параллелизма
    for (int repeat = 0; repeat < 100; ++repeat) {
        double temp = 0.0;
        for (size_t i = 0; i < vec1.size(); ++i) {
            temp += vec1[i] * vec2[i];
        }
        result = temp;
    }
    
    return result;
}

// Последовательный метод для сравнения
BenchmarkResult sequential_method(const string& filename, int runs) {
    BenchmarkResult bench_result;
    bench_result.method = "sequential";
    bench_result.num_threads = 1;
    
    double total_input_time = 0.0;
    double total_computation_time = 0.0;
    vector<DotProductResult> final_results;
    
    for (int run = 0; run < runs; ++run) {
        // Фаза 1: Чтение всех данных
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
        
        // Фаза 2: Вычисление всех скалярных произведений
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

// Параллельный метод с использованием sections
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
        
        // Читаем метаданные
        int num_pairs = 0;
        int vector_size = 0;
        {
            ifstream meta_file(filename);
            meta_file >> num_pairs >> vector_size;
            meta_file.close();
        }
        
        // Потокобезопасная очередь для передачи данных между секциями
        ThreadSafeQueue work_queue;
        
        // Результаты вычислений
        vector<DotProductResult> results(num_pairs);
        
        // Атомарные флаги для синхронизации
        atomic<bool> input_done(false);
        atomic<int> processed_count(0);
        
        // Время выполнения секций
        double input_time = 0.0;
        double computation_time = 0.0;
        
        #pragma omp parallel sections shared(work_queue, results, input_done, processed_count, input_time, computation_time)
        {
            // ============================================
            // СЕКЦИЯ 1: ЗАДАЧА ВВОДА - чтение векторов из файла
            // ============================================
            #pragma omp section
            {
                auto section_start = chrono::high_resolution_clock::now();
                
                ifstream file(filename);
                int np, vs;
                file >> np >> vs;
                
                for (int p = 0; p < np; ++p) {
                    VectorPair pair;
                    pair.id = p;
                    pair.vec1.resize(vs);
                    pair.vec2.resize(vs);
                    
                    // Чтение первого вектора
                    for (int i = 0; i < vs; ++i) {
                        file >> pair.vec1[i];
                    }
                    // Чтение второго вектора
                    for (int i = 0; i < vs; ++i) {
                        file >> pair.vec2[i];
                    }
                    
                    // Добавляем пару в очередь для обработки
                    work_queue.push(pair);
                }
                file.close();
                
                // Сигнализируем, что чтение завершено
                input_done.store(true);
                
                auto section_end = chrono::high_resolution_clock::now();
                chrono::duration<double, milli> duration = section_end - section_start;
                input_time = duration.count();
            }
            
            // ============================================
            // СЕКЦИЯ 2: ЗАДАЧА ВЫЧИСЛЕНИЯ - вычисление скалярных произведений
            // ============================================
            #pragma omp section
            {
                auto section_start = chrono::high_resolution_clock::now();
                
                while (true) {
                    VectorPair pair;
                    
                    // Пытаемся получить данные из очереди
                    if (work_queue.try_pop(pair)) {
                        // Вычисляем скалярное произведение
                        auto dot_start = chrono::high_resolution_clock::now();
                        double dot_product = compute_dot_product(pair.vec1, pair.vec2);
                        auto dot_end = chrono::high_resolution_clock::now();
                        
                        // Сохраняем результат
                        results[pair.id].pair_id = pair.id;
                        results[pair.id].result = dot_product;
                        chrono::duration<double, milli> dot_duration = dot_end - dot_start;
                        results[pair.id].computation_time_ms = dot_duration.count();
                        
                        processed_count.fetch_add(1);
                    } else {
                        // Очередь пуста
                        if (input_done.load() && work_queue.empty()) {
                            // Ввод завершён и очередь пуста - выходим
                            break;
                        }
                        // Иначе ждём новых данных (короткая пауза)
                        // Используем busy-wait с yield для снижения нагрузки
                        #pragma omp flush
                    }
                }
                
                auto section_end = chrono::high_resolution_clock::now();
                chrono::duration<double, milli> duration = section_end - section_start;
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

// Проверка корректности результатов
bool verify_correctness(const string& filename) {
    cout << "\n=== Correctness Verification ===" << endl;
    
    BenchmarkResult seq_result = sequential_method(filename, 1);
    BenchmarkResult par_result = sections_method(filename, 2, 1);
    
    cout << "Sequential results (first 5):" << endl;
    for (size_t i = 0; i < min(size_t(5), seq_result.results.size()); ++i) {
        cout << "  Pair " << i << ": " << fixed << setprecision(6) 
             << seq_result.results[i].result << endl;
    }
    
    cout << "\nParallel (sections) results (first 5):" << endl;
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

// Полный бенчмарк с сравнением методов
void full_benchmark(const string& filename, int runs) {
    cout << "\n" << string(60, '=') << endl;
    cout << "FULL BENCHMARK COMPARISON" << endl;
    cout << string(60, '=') << endl;
    
    // Последовательный метод
    cout << "\nRunning sequential method..." << endl;
    BenchmarkResult seq = sequential_method(filename, runs);
    
    // Параллельный метод с 2 потоками (оптимально для 2 секций)
    cout << "Running parallel sections method (2 threads)..." << endl;
    BenchmarkResult par = sections_method(filename, 2, runs);
    
    // Вывод результатов
    cout << "\n" << string(60, '-') << endl;
    cout << "RESULTS (averaged over " << runs << " runs)" << endl;
    cout << string(60, '-') << endl;
    
    cout << "\nDataset: " << seq.num_pairs << " pairs, vector size " << seq.vector_size << endl;
    
    cout << "\n" << left << setw(20) << "Method" 
         << setw(15) << "Total (ms)" 
         << setw(15) << "Input (ms)" 
         << setw(15) << "Compute (ms)" << endl;
    cout << string(60, '-') << endl;
    
    cout << left << setw(20) << "Sequential"
         << setw(15) << fixed << setprecision(2) << seq.total_time_ms
         << setw(15) << seq.input_time_ms
         << setw(15) << seq.computation_time_ms << endl;
    
    cout << left << setw(20) << "Sections (2 thr)"
         << setw(15) << fixed << setprecision(2) << par.total_time_ms
         << setw(15) << par.input_time_ms
         << setw(15) << par.computation_time_ms << endl;
    
    // Расчёт ускорения
    double speedup = seq.total_time_ms / par.total_time_ms;
    double efficiency = speedup / 2.0 * 100.0;
    
    cout << "\n" << string(60, '-') << endl;
    cout << "SPEEDUP ANALYSIS" << endl;
    cout << string(60, '-') << endl;
    cout << "Speedup:    " << fixed << setprecision(2) << speedup << "x" << endl;
    cout << "Efficiency: " << fixed << setprecision(1) << efficiency << "%" << endl;
    
    // Теоретическое ускорение
    double t_input = seq.input_time_ms;
    double t_compute = seq.computation_time_ms;
    double t_seq = t_input + t_compute;
    double t_par_theoretical = max(t_input, t_compute);
    double theoretical_speedup = t_seq / t_par_theoretical;
    
    cout << "\nTheoretical maximum speedup (pipeline): " 
         << fixed << setprecision(2) << theoretical_speedup << "x" << endl;
    cout << "(Based on overlapping I/O and computation)" << endl;
    
    // Проверка корректности
    cout << "\n" << string(60, '-') << endl;
    cout << "CORRECTNESS CHECK" << endl;
    cout << string(60, '-') << endl;
    
    bool correct = true;
    const double tolerance = 1e-6;
    for (size_t i = 0; i < seq.results.size() && correct; ++i) {
        double error = abs(seq.results[i].result - par.results[i].result);
        if (error > tolerance) {
            correct = false;
            cout << "✗ MISMATCH at pair " << i << endl;
        }
    }
    
    if (correct) {
        cout << "✓ All " << seq.results.size() << " results match!" << endl;
    }
}

void print_usage(const char* program_name) {
    cout << "Usage: " << program_name << " <command> [options]" << endl;
    cout << "\nCommands:" << endl;
    cout << "  generate <num_pairs> <vector_size> <output_file>" << endl;
    cout << "    Generate test data file with vector pairs" << endl;
    cout << "\n  benchmark <data_file> <num_threads> <method> <runs>" << endl;
    cout << "    Run benchmark on existing data file" << endl;
    cout << "    method: sequential, sections" << endl;
    cout << "\n  full <data_file> <runs>" << endl;
    cout << "    Run full benchmark comparing all methods" << endl;
    cout << "\n  verify <data_file>" << endl;
    cout << "    Verify correctness of parallel implementation" << endl;
    cout << "\nExamples:" << endl;
    cout << "  " << program_name << " generate 50 10000 vectors.txt" << endl;
    cout << "  " << program_name << " full vectors.txt 5" << endl;
    cout << "  " << program_name << " benchmark vectors.txt 2 sections 10" << endl;
    cout << "  " << program_name << " verify vectors.txt" << endl;
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
        
        cout << "=== Vector Dot Products Benchmark ===" << endl;
        cout << "Data file: " << data_file << endl;
        cout << "Threads:   " << num_threads << endl;
        cout << "Method:    " << method << endl;
        cout << "Runs:      " << runs << endl;
        
        BenchmarkResult result;
        if (method == "sequential") {
            result = sequential_method(data_file, runs);
        } else if (method == "sections") {
            result = sections_method(data_file, num_threads, runs);
        } else {
            cerr << "Error: Invalid method" << endl;
            return 1;
        }
        
        cout << "\nResults:" << endl;
        cout << "  Total time:   " << fixed << setprecision(2) << result.total_time_ms << " ms" << endl;
        cout << "  Input time:   " << result.input_time_ms << " ms" << endl;
        cout << "  Compute time: " << result.computation_time_ms << " ms" << endl;
        
    } else if (command == "full") {
        if (argc < 4) {
            cerr << "Error: Insufficient arguments for full benchmark" << endl;
            print_usage(argv[0]);
            return 1;
        }
        
        string data_file = argv[2];
        int runs = atoi(argv[3]);
        
        full_benchmark(data_file, runs);
        
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
