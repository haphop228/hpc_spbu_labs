#include <mpi.h>
#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <cstdlib>
#include <cstring>

void solve_cannon_modes(int n, int rank, int size, std::string mode_str) {
    int dims[2] = {0, 0};
    int periods[2] = {1, 1};
    int coords[2];

    int sqrt_p = (int)sqrt(size);
    if (sqrt_p * sqrt_p != size) return;
    if (n % sqrt_p != 0) MPI_Abort(MPI_COMM_WORLD, 1);

    dims[0] = dims[1] = sqrt_p;

    MPI_Comm cart_comm;
    MPI_Cart_create(MPI_COMM_WORLD, 2, dims, periods, 1, &cart_comm);
    MPI_Cart_coords(cart_comm, rank, 2, coords);

    int my_row = coords[0];
    int my_col = coords[1];

    int left, right, up, down;
    MPI_Cart_shift(cart_comm, 1, 1, &left, &right);
    MPI_Cart_shift(cart_comm, 0, 1, &up, &down);

    int block_size = n / sqrt_p;
    int count = block_size * block_size;

    std::vector<double> A(count, 1.0);
    std::vector<double> B(count, 1.0);
    std::vector<double> C(count, 0.0);
    std::vector<double> A_recv(count);
    std::vector<double> B_recv(count);

    int buffer_size = 0;
    char* buffer = nullptr;
    // Подготовка буфера
    if (mode_str == "Buffered") {
        buffer_size = 128 * 1024 * 1024;
        buffer = new char[buffer_size];
        MPI_Buffer_attach(buffer, buffer_size); // но MPI не выделяет этот буфер сам, поэтому это сделаем мы
    }

    MPI_Status stats[2];
    MPI_Request reqs[2];

    int shift_src, shift_dst;

    MPI_Cart_shift(cart_comm, 1, -my_row, &shift_src, &shift_dst);
    MPI_Sendrecv_replace(A.data(), count, MPI_DOUBLE, shift_dst, 1, shift_src, 1, cart_comm, &stats[0]);

    MPI_Cart_shift(cart_comm, 0, -my_col, &shift_src, &shift_dst);
    MPI_Sendrecv_replace(B.data(), count, MPI_DOUBLE, shift_dst, 1, shift_src, 1, cart_comm, &stats[0]);

    MPI_Barrier(MPI_COMM_WORLD);
    double start = MPI_Wtime();

    for (int k = 0; k < sqrt_p; ++k) {
        for (int i = 0; i < block_size; ++i) {
            for (int l = 0; l < block_size; ++l) {
                double temp = A[i * block_size + l];
                for (int j = 0; j < block_size; ++j) {
                    C[i * block_size + j] += temp * B[l * block_size + j];
                }
            }
        }
        // запускаем прием данных до того, как начинаем отправку
        MPI_Irecv(A_recv.data(), count, MPI_DOUBLE, right, 1, cart_comm, &reqs[0]);
        MPI_Irecv(B_recv.data(), count, MPI_DOUBLE, down, 1, cart_comm, &reqs[1]);

        if (mode_str == "Ready") {
            MPI_Barrier(cart_comm);
        }

        if (mode_str == "Standard") {
            MPI_Send(A.data(), count, MPI_DOUBLE, left, 1, cart_comm);
            MPI_Send(B.data(), count, MPI_DOUBLE, up, 1, cart_comm);
        } else if (mode_str == "Synchronous") {
            MPI_Ssend(A.data(), count, MPI_DOUBLE, left, 1, cart_comm); // ждем, когда получатель готов
            MPI_Ssend(B.data(), count, MPI_DOUBLE, up, 1, cart_comm);
        } else if (mode_str == "Buffered") {
            MPI_Bsend(A.data(), count, MPI_DOUBLE, left, 1, cart_comm); // все кладем в буфер
            MPI_Bsend(B.data(), count, MPI_DOUBLE, up, 1, cart_comm);
        } else if (mode_str == "Ready") {
            MPI_Rsend(A.data(), count, MPI_DOUBLE, left, 1, cart_comm); // отправка без проверки
            MPI_Rsend(B.data(), count, MPI_DOUBLE, up, 1, cart_comm);
        }

        MPI_Waitall(2, reqs, stats);

        std::swap(A, A_recv);
        std::swap(B, B_recv);
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double end = MPI_Wtime();

    if (mode_str == "Buffered") {
        MPI_Buffer_detach(&buffer, &buffer_size);
        delete[] buffer;
    }

    if (rank == 0) {
        std::cout << mode_str << ";" << size << ";" << n << ";" << (end - start) << std::endl;
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::string mode = "Standard";
    int n = 576;

    if (argc > 1) mode = argv[1];
    if (argc > 2) n = std::atoi(argv[2]);

    if (rank == 0 && mode == "header") {
        std::cout << "Mode;Processes;MatrixSize;Time" << std::endl;
        MPI_Finalize();
        return 0;
    }

    solve_cannon_modes(n, rank, size, mode);

    MPI_Finalize();
    return 0;
}