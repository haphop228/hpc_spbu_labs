#include <mpi.h>
#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>

void emulate_computation(double work_us) {
    if (work_us <= 0) return;
    double start = MPI_Wtime();
    double seconds = work_us / 1000000.0;
    while (MPI_Wtime() - start < seconds) {
        __asm__ volatile("" ::: "memory");
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::string label = "Default";
    double compute_us = 1000.0;
    long long comm_bytes = 1024;
    int iterations = 100;

    if (argc > 1) label = argv[1];
    if (argc > 2) compute_us = std::atof(argv[2]);
    if (argc > 3) comm_bytes = std::atoll(argv[3]);

    std::vector<char> send_buf(comm_bytes, 'A');
    std::vector<char> recv_buf(comm_bytes);

    int left = (rank - 1 + size) % size;
    int right = (rank + 1) % size;

    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    for (int i = 0; i < iterations; ++i) {
        emulate_computation(compute_us);
        if (comm_bytes > 0) {
            MPI_Sendrecv(send_buf.data(), comm_bytes, MPI_BYTE, right, 0,
                         recv_buf.data(), comm_bytes, MPI_BYTE, left, 0,
                         MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }
    }

    double end_time = MPI_Wtime();
    double total_time = end_time - start_time;

    double max_time = 0.0;
    MPI_Reduce(&total_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        std::cout << label << ";"
                  << size << ";"
                  << compute_us << ";"
                  << comm_bytes << ";"
                  << max_time << std::endl;
    }

    MPI_Finalize();
    return 0;
}
