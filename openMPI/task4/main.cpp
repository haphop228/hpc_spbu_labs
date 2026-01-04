#include <mpi.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <cstdlib>

void solve_striped(int n, int rank, int size) {
    if (n % size != 0) {
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    int local_rows = n / size;
    std::vector<double> A_local(local_rows * n, 1.0);
    std::vector<double> B(n * n, 1.0);
    std::vector<double> C_local(local_rows * n, 0.0);

    MPI_Bcast(B.data(), n * n, MPI_DOUBLE, 0, MPI_COMM_WORLD); // рассылаем матрицу B всем процессам

    MPI_Barrier(MPI_COMM_WORLD);
    double start = MPI_Wtime();

    for (int i = 0; i < local_rows; ++i) {
        for (int k = 0; k < n; ++k) {
            double temp = A_local[i * n + k];
            for (int j = 0; j < n; ++j) {
                C_local[i * n + j] += temp * B[k * n + j];
            }
        }
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "Striped;" << size << ";" << n << ";" << (end - start) << std::endl;
    }
}

void solve_cannon(int n, int rank, int size) {
    int dims[2] = {0, 0};
    int periods[2] = {1, 1};
    int coords[2];
    
    int sqrt_p = (int)sqrt(size);
    if (sqrt_p * sqrt_p != size) {
        if (rank == 0) std::cout << "Skipped;" << size << ";" << n << ";0.0" << std::endl; 
        return;
    }

    if (n % sqrt_p != 0) {
         MPI_Abort(MPI_COMM_WORLD, 1);
    }

    dims[0] = dims[1] = sqrt_p;
    
    MPI_Comm cart_comm; // создаем коммуникатор для решетки
    MPI_Cart_create(MPI_COMM_WORLD, 2, dims, periods, 1, &cart_comm); // создаем 2D решетку
    MPI_Cart_coords(cart_comm, rank, 2, coords); // получаем координаты процесса в решетке
    
    int my_row = coords[0];
    int my_col = coords[1];
    
    int left, right, up, down;
    MPI_Cart_shift(cart_comm, 1, 1, &left, &right); // получаем индексы соседей в решетке
    MPI_Cart_shift(cart_comm, 0, 1, &up, &down);

    int block_size = n / sqrt_p;
    std::vector<double> A_block(block_size * block_size, 1.0);
    std::vector<double> B_block(block_size * block_size, 1.0);
    std::vector<double> C_block(block_size * block_size, 0.0);

    MPI_Status status;
    int shift_src, shift_dst;

    // Вычисляем, насколько сдвигать и КУДА отправлять
    // Для матрицы A сдвигаем строку влево на величину 'my_row'
    MPI_Cart_shift(cart_comm, 1, -my_row, &shift_src, &shift_dst);
    // Физически меняемся данными
    // Функция MPI_Sendrecv_replace это обмен данными между процессами
    MPI_Sendrecv_replace(A_block.data(), block_size * block_size, MPI_DOUBLE, shift_dst, 1, shift_src, 1, cart_comm, &status);

    // То же самое для B, только сдвигаем столбцы вверх на 'my_col'
    MPI_Cart_shift(cart_comm, 0, -my_col, &shift_src, &shift_dst);
    MPI_Sendrecv_replace(B_block.data(), block_size * block_size, MPI_DOUBLE, shift_dst, 1, shift_src, 1, cart_comm, &status);

    MPI_Barrier(MPI_COMM_WORLD);
    double start = MPI_Wtime();

    for (int k = 0; k < sqrt_p; ++k) {
        for (int i = 0; i < block_size; ++i) {
            for (int l = 0; l < block_size; ++l) {
                double temp = A_block[i * block_size + l];
                for (int j = 0; j < block_size; ++j) {
                    C_block[i * block_size + j] += temp * B_block[l * block_size + j];
                }
            }
        }
        // Блок A всегда едет на 1 шаг ВЛЕВО, а B - ВВЕРХ
        MPI_Sendrecv_replace(A_block.data(), block_size * block_size, MPI_DOUBLE, left, 1, right, 1, cart_comm, &status);
        MPI_Sendrecv_replace(B_block.data(), block_size * block_size, MPI_DOUBLE, up, 1, down, 1, cart_comm, &status);
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double end = MPI_Wtime();

    if (rank == 0) {
        std::cout << "Cannon;" << size << ";" << n << ";" << (end - start) << std::endl;
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::string mode = "striped";
    int n = 576;

    if (argc > 1) mode = argv[1];
    if (argc > 2) n = std::atoi(argv[2]);

    if (rank == 0 && mode == "header") {
        std::cout << "Algorithm;Processes;MatrixSize;Time" << std::endl;
        MPI_Finalize();
        return 0;
    }

    if (mode == "striped") {
        solve_striped(n, rank, size);
    } else if (mode == "cannon") {
        solve_cannon(n, rank, size);
    }

    MPI_Finalize();
    return 0;
}
