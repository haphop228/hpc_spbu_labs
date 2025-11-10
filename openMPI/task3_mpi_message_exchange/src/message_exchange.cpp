#include <mpi.h>
#include <iostream>
#include <vector>
#include <chrono>
#include <iomanip>
#include <cstring>
#include <fstream>
#include <algorithm>
#include <cmath>

struct BenchmarkResult {
    size_t message_size;
    int iterations;
    double avg_time_ms;
    double min_time_ms;
    double max_time_ms;
    double median_time_ms;
    double std_dev_ms;
    double bandwidth_mbps;
};

// Функция для выполнения обмена сообщениями между двумя процессами
std::vector<double> perform_message_exchange(int rank, size_t message_size, int iterations) {
    std::vector<char> send_buffer(message_size);
    std::vector<char> recv_buffer(message_size);
    std::vector<double> times;
    
    // Инициализация буфера отправки
    for (size_t i = 0; i < message_size; ++i) {
        send_buffer[i] = static_cast<char>(i % 256);
    }
    
    // Warm-up: один обмен для прогрева
    if (rank == 0) {
        MPI_Send(send_buffer.data(), message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
        MPI_Recv(recv_buffer.data(), message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    } else if (rank == 1) {
        MPI_Recv(recv_buffer.data(), message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Send(send_buffer.data(), message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
    }
    
    MPI_Barrier(MPI_COMM_WORLD);
    
    // Основные измерения
    for (int iter = 0; iter < iterations; ++iter) {
        double start_time = MPI_Wtime();
        
        if (rank == 0) {
            // Процесс 0: отправляет, затем получает
            MPI_Send(send_buffer.data(), message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
            MPI_Recv(recv_buffer.data(), message_size, MPI_CHAR, 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        } else if (rank == 1) {
            // Процесс 1: получает, затем отправляет
            MPI_Recv(recv_buffer.data(), message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            MPI_Send(send_buffer.data(), message_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
        }
        
        double end_time = MPI_Wtime();
        double elapsed_time = (end_time - start_time) * 1000.0; // в миллисекундах
        
        times.push_back(elapsed_time);
        
        MPI_Barrier(MPI_COMM_WORLD);
    }
    
    return times;
}

// Вычисление статистики
BenchmarkResult calculate_statistics(const std::vector<double>& times, size_t message_size, int iterations) {
    BenchmarkResult result;
    result.message_size = message_size;
    result.iterations = iterations;
    
    // Среднее время
    double sum = 0.0;
    for (double t : times) {
        sum += t;
    }
    result.avg_time_ms = sum / times.size();
    
    // Минимум и максимум
    result.min_time_ms = *std::min_element(times.begin(), times.end());
    result.max_time_ms = *std::max_element(times.begin(), times.end());
    
    // Медиана
    std::vector<double> sorted_times = times;
    std::sort(sorted_times.begin(), sorted_times.end());
    size_t mid = sorted_times.size() / 2;
    if (sorted_times.size() % 2 == 0) {
        result.median_time_ms = (sorted_times[mid - 1] + sorted_times[mid]) / 2.0;
    } else {
        result.median_time_ms = sorted_times[mid];
    }
    
    // Стандартное отклонение
    double variance = 0.0;
    for (double t : times) {
        variance += (t - result.avg_time_ms) * (t - result.avg_time_ms);
    }
    result.std_dev_ms = std::sqrt(variance / times.size());
    
    // Пропускная способность (bandwidth) в MB/s
    // Учитываем, что данные передаются дважды (туда и обратно)
    double total_data_mb = (2.0 * message_size) / (1024.0 * 1024.0);
    double time_seconds = result.avg_time_ms / 1000.0;
    result.bandwidth_mbps = total_data_mb / time_seconds;
    
    return result;
}

void print_result(const BenchmarkResult& result, int rank) {
    if (rank == 0) {
        std::cout << "\n=== Benchmark Results ===" << std::endl;
        std::cout << "Message size:     " << result.message_size << " bytes";
        
        // Форматирование размера сообщения
        if (result.message_size >= 1024 * 1024) {
            std::cout << " (" << std::fixed << std::setprecision(2) 
                      << result.message_size / (1024.0 * 1024.0) << " MB)";
        } else if (result.message_size >= 1024) {
            std::cout << " (" << std::fixed << std::setprecision(2) 
                      << result.message_size / 1024.0 << " KB)";
        }
        std::cout << std::endl;
        
        std::cout << "Iterations:       " << result.iterations << std::endl;
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "Average time:     " << result.avg_time_ms << " ms" << std::endl;
        std::cout << "Median time:      " << result.median_time_ms << " ms" << std::endl;
        std::cout << "Min time:         " << result.min_time_ms << " ms" << std::endl;
        std::cout << "Max time:         " << result.max_time_ms << " ms" << std::endl;
        std::cout << "Std deviation:    " << result.std_dev_ms << " ms" << std::endl;
        std::cout << "Bandwidth:        " << std::fixed << std::setprecision(2) 
                  << result.bandwidth_mbps << " MB/s" << std::endl;
    }
}

void save_to_csv(const BenchmarkResult& result, const std::string& filename, int rank) {
    if (rank == 0) {
        std::ofstream out(filename, std::ios::app);
        if (out.is_open()) {
            // Проверяем, пустой ли файл
            out.seekp(0, std::ios::end);
            if (out.tellp() == 0) {
                // Записываем заголовок
                out << "message_size_bytes,iterations,avg_time_ms,median_time_ms,"
                    << "min_time_ms,max_time_ms,std_dev_ms,bandwidth_mbps" << std::endl;
            }
            
            // Записываем данные
            out << result.message_size << ","
                << result.iterations << ","
                << std::fixed << std::setprecision(6)
                << result.avg_time_ms << ","
                << result.median_time_ms << ","
                << result.min_time_ms << ","
                << result.max_time_ms << ","
                << result.std_dev_ms << ","
                << std::setprecision(2)
                << result.bandwidth_mbps << std::endl;
            
            out.close();
        } else {
            std::cerr << "Error: Could not open output file: " << filename << std::endl;
        }
    }
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Проверка количества процессов
    if (size != 2) {
        if (rank == 0) {
            std::cerr << "Error: This program requires exactly 2 MPI processes" << std::endl;
            std::cerr << "Usage: mpirun -np 2 " << argv[0] << " <message_size> <iterations> [output_file]" << std::endl;
        }
        MPI_Finalize();
        return 1;
    }
    
    // Парсинг аргументов командной строки
    if (argc < 3) {
        if (rank == 0) {
            std::cerr << "Usage: " << argv[0] << " <message_size> <iterations> [output_file]" << std::endl;
            std::cerr << "Example: mpirun -np 2 " << argv[0] << " 1024 100" << std::endl;
            std::cerr << "         mpirun -np 2 " << argv[0] << " 1048576 50 results/benchmark.csv" << std::endl;
        }
        MPI_Finalize();
        return 1;
    }
    
    size_t message_size = std::stoull(argv[1]);
    int iterations = std::stoi(argv[2]);
    std::string output_file = (argc > 3) ? argv[3] : "";
    
    if (rank == 0) {
        std::cout << "=== MPI Message Exchange Benchmark ===" << std::endl;
        std::cout << "Number of processes: " << size << std::endl;
        std::cout << "Message size: " << message_size << " bytes" << std::endl;
        std::cout << "Iterations: " << iterations << std::endl;
        if (!output_file.empty()) {
            std::cout << "Output file: " << output_file << std::endl;
        }
        std::cout << "\nStarting benchmark..." << std::endl;
    }
    
    // Выполнение обмена сообщениями
    std::vector<double> times = perform_message_exchange(rank, message_size, iterations);
    
    // Вычисление статистики (только процесс 0)
    BenchmarkResult result;
    if (rank == 0) {
        result = calculate_statistics(times, message_size, iterations);
        print_result(result, rank);
        
        if (!output_file.empty()) {
            save_to_csv(result, output_file, rank);
            std::cout << "\nResults saved to: " << output_file << std::endl;
        }
    }
    
    MPI_Finalize();
    return 0;
}