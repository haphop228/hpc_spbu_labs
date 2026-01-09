#include <mpi.h>
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <limits>
#include <iomanip>

void generate_data(std::vector<int>& data, int size) {
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> dist(std::numeric_limits<int>::min(), std::numeric_limits<int>::max());

    data.resize(size);
    for (int i = 0; i < size; ++i) {
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

    int count_per_proc = global_n / size;

    std::vector<int> global_vec;
    std::vector<int> local_vec(count_per_proc);

    if (rank == 0) {
        generate_data(global_vec, count_per_proc * size);
    }

    MPI_Scatter(global_vec.data(), count_per_proc, MPI_INT, 
                local_vec.data(), count_per_proc, MPI_INT, 
                0, MPI_COMM_WORLD);

    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    int local_min = std::numeric_limits<int>::max();
    if (!local_vec.empty()) {
        local_min = *std::min_element(local_vec.begin(), local_vec.end());
    }

    int global_min = 0;
    MPI_Reduce(&local_min, &global_min, 1, MPI_INT, MPI_MIN, 0, MPI_COMM_WORLD);

    double end_time = MPI_Wtime();
    double elapsed_time = end_time - start_time;

    if (rank == 0) {
        std::cout << size << ";"
                  << (count_per_proc * size)
                  << ";"
                  << std::fixed << std::setprecision(6) << elapsed_time << ";"
                  << global_min << std::endl;
    }

    MPI_Finalize();
    return 0;
}
