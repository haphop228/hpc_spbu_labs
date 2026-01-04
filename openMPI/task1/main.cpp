#include <mpi.h>
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <limits>
#include <iomanip>

// Функция для заполнения части вектора случайными числами
void generate_data(std::vector<int>& data, int size, int rank) {
    std::mt19937 rng(42 + rank);
    std::uniform_int_distribution<int> dist(std::numeric_limits<int>::min(), std::numeric_limits<int>::max());

    data.resize(size);
    for (int i = 0; i < size; ++i) {
        data[i] = dist(rng);
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv); // Инициализация MPI

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank); // Получение номера текущего процесса
    MPI_Comm_size(MPI_COMM_WORLD, &size); // Получение количества процессов

    // Расчет local_n и генерация
    long long global_n = 10000000;
    if (argc > 1) {
        global_n = std::atoll(argv[1]);
    }

    long long local_n = global_n / size;
    if (rank == size - 1) {
        local_n += global_n % size;
    }

    std::vector<int> local_vec;
    generate_data(local_vec, local_n, rank);

    MPI_Barrier(MPI_COMM_WORLD); // Барьер для синхронизации процессов, чтобы все процессы начали работу одновременно
    double start_time = MPI_Wtime();

    int local_min = std::numeric_limits<int>::max();
    if (!local_vec.empty()) {
        local_min = *std::min_element(local_vec.begin(), local_vec.end());
    }

    int global_min = 0;
    MPI_Reduce(&local_min, &global_min, 1, MPI_INT, MPI_MIN, 0, MPI_COMM_WORLD); // Редукция для нахождения минимального значения

    double end_time = MPI_Wtime();
    double elapsed_time = end_time - start_time;

    if (rank == 0) {
        std::cout << size << ";"
                  << global_n << ";"
                  << std::fixed << std::setprecision(6) << elapsed_time << ";"
                  << global_min << std::endl;
    }

    MPI_Finalize();
    return 0;
}