#include <mpi.h>
#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

void emulate_computation(double work_us) {
    if (work_us <= 0) return;
    double start = MPI_Wtime();
    double seconds = work_us / 1000000.0;
    while (MPI_Wtime() - start < seconds) {
        __asm__ volatile("" ::: "memory");
    }
}

void benchmark_nonblocking(int rank, int size, int data_size, double compute_us, int iterations, double& result_time) {
    std::vector<char> send_buf(data_size, 'A');
    std::vector<char> recv_buf(data_size);
    
    int left = (rank - 1 + size) % size;
    int right = (rank + 1) % size;
    
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();
    
    for (int i = 0; i < iterations; ++i) {
        MPI_Request reqs[2];
        MPI_Status stats[2];
        
        MPI_Irecv(recv_buf.data(), data_size, MPI_BYTE, left, 0, MPI_COMM_WORLD, &reqs[0]);
        MPI_Isend(send_buf.data(), data_size, MPI_BYTE, right, 0, MPI_COMM_WORLD, &reqs[1]);
        
        emulate_computation(compute_us);
        
        MPI_Waitall(2, reqs, stats);
    }
    
    double end_time = MPI_Wtime();
    double total_time = end_time - start_time;
    
    double max_time = 0.0;
    MPI_Reduce(&total_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    
    result_time = max_time;
}

void run_benchmark(const std::string& label, int data_size, double compute_us, int iterations) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    double blocking_time = 0.0;
    double nonblocking_time = 0.0;
    
    std::vector<char> send_buf(data_size, 'A');
    std::vector<char> recv_buf(data_size);
    int left = (rank - 1 + size) % size;
    int right = (rank + 1) % size;
    
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();
    for (int i = 0; i < iterations; ++i) {
        emulate_computation(compute_us);
        MPI_Sendrecv(send_buf.data(), data_size, MPI_BYTE, right, 0,
                     recv_buf.data(), data_size, MPI_BYTE, left, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }
    double end_time = MPI_Wtime();
    double total_time = end_time - start_time;
    MPI_Reduce(&total_time, &blocking_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    
    benchmark_nonblocking(rank, size, data_size, compute_us, iterations, nonblocking_time);
    
    if (rank == 0) {
        double speedup = blocking_time / nonblocking_time;
        std::cout << label << ";"
                  << size << ";"
                  << data_size << ";"
                  << compute_us << ";"
                  << std::scientific << std::setprecision(6) << blocking_time << ";"
                  << nonblocking_time << ";"
                  << std::fixed << std::setprecision(4) << speedup << std::endl;
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    std::vector<int> data_sizes = {1024, 10240, 102400, 1048576};
    std::vector<double> compute_values = {10, 100, 1000, 10000};
    
    int iterations = 100;
    
    for (int data_size : data_sizes) {
        for (double compute_us : compute_values) {
            std::string label = "D" + std::to_string(data_size) + "_C" + std::to_string((int)compute_us);
            
            int iter = iterations;
            if (data_size >= 1048576) iter = 20;
            
            run_benchmark(label, data_size, compute_us, iter);
        }
    }
    
    MPI_Finalize();
    return 0;
}
