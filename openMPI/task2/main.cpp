#include <mpi.h>
#include <iostream>
#include <vector>
#include <random>
#include <numeric>
#include <iomanip>

// Функция генерации данных
// Заполняем небольшими числами, чтобы результат оставался читаемым
void generate_data(std::vector<double>& data, long long size, int rank, int seed_offset) {
    std::mt19937 rng(42 + rank + seed_offset);
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

    long long global_n = 10000000;
    if (argc > 1) {
        global_n = std::atoll(argv[1]);
    }

    long long local_n = global_n / size;
    if (rank == size - 1) {
        local_n += global_n % size;
    }

    std::vector<double> vec_a;
    std::vector<double> vec_b;
    // гарантируем, что a и b будут заполнены разными данными
    generate_data(vec_a, local_n, rank, 0);
    generate_data(vec_b, local_n, rank, 1);

    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    double local_dot_prod = 0.0;
    const double* a_ptr = vec_a.data();
    const double* b_ptr = vec_b.data();

    for (long long i = 0; i < local_n; ++i) {
        local_dot_prod += a_ptr[i] * b_ptr[i];
    }

    double global_dot_prod = 0.0;
    MPI_Reduce(&local_dot_prod, &global_dot_prod, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD); // Суммируем результаты всех процессов

    double end_time = MPI_Wtime();
    double elapsed_time = end_time - start_time;

    if (rank == 0) {
        std::cout << size << ";"
                  << global_n << ";"
                  << std::fixed << std::setprecision(6) << elapsed_time << ";"
                  << std::scientific << std::setprecision(4) << global_dot_prod << std::endl;
    }

    MPI_Finalize();
    return 0;
}