#include <mpi.h>
#include <iostream>
#include <vector>
#include <random>
#include <numeric>
#include <iomanip>

void generate_data(std::vector<double>& data, long long size, int seed) {
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> dist(-100.0, 100.0);

    data.resize(size);
    for (long long i = 0; i < size; ++i) {
        data[i] = dist(rng);
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long long global_n = 100000000000;
    if (argc > 1) {
        global_n = std::atoll(argv[1]);
    }

    long long count_per_proc = global_n / size;

    std::vector<double> global_a;
    std::vector<double> global_b;

    std::vector<double> local_a(count_per_proc);
    std::vector<double> local_b(count_per_proc);

    if (rank == 0) {
        generate_data(global_a, count_per_proc * size, 42);
        generate_data(global_b, count_per_proc * size, 43);
    }

    MPI_Scatter(global_a.data(), count_per_proc, MPI_DOUBLE, 
                local_a.data(), count_per_proc, MPI_DOUBLE, 
                0, MPI_COMM_WORLD);
    
    MPI_Scatter(global_b.data(), count_per_proc, MPI_DOUBLE, 
                local_b.data(), count_per_proc, MPI_DOUBLE, 
                0, MPI_COMM_WORLD);

    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    double local_dot_prod = 0.0;
    const double* a_ptr = local_a.data();
    const double* b_ptr = local_b.data();

    for (long long i = 0; i < count_per_proc; ++i) {
        local_dot_prod += a_ptr[i] * b_ptr[i];
    }

    double global_dot_prod = 0.0;
    MPI_Reduce(&local_dot_prod, &global_dot_prod, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    double end_time = MPI_Wtime();
    double elapsed_time = end_time - start_time;

    if (rank == 0) {
        std::cout << size << ";"
                  << (count_per_proc * size)
                  << ";"
                  << std::fixed << std::setprecision(6) << elapsed_time << ";"
                  << std::scientific << std::setprecision(4) << global_dot_prod << std::endl;
    }

    MPI_Finalize();
    return 0;
}
