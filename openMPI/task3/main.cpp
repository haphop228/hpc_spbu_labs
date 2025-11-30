#include <mpi.h>
#include <iostream>
#include <vector>
#include <iomanip>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Для этой задачи нужно ровно 2 процесса
    if (size != 2) {
        if (rank == 0) {
            std::cerr << "Error: This program requires exactly 2 processes." << std::endl;
        }
        MPI_Finalize();
        return 1;
    }

    // Размеры сообщений: от 0 байт до 16 МБ
    std::vector<long long> msg_sizes;
    msg_sizes.push_back(0); // Латентность
    for (long long s = 1; s <= 16 * 1024 * 1024; s *= 2) {
        msg_sizes.push_back(s);
    }

    // Буферы
    long long max_size = 16 * 1024 * 1024;
    std::vector<char> send_buf(max_size, 'A');
    std::vector<char> recv_buf(max_size);

    // Печатаем заголовок CSV только один раз
    if (rank == 0) {
        std::cout << "Bytes;Iterations;Time;Bandwidth" << std::endl;
    }

    for (long long n : msg_sizes) {
        // Адаптивное число итераций: много для малых, мало для больших
        int iterations = 1000;
        if (n > 64 * 1024) iterations = 100;
        if (n > 1024 * 1024) iterations = 20;

        MPI_Barrier(MPI_COMM_WORLD);
        double t_start = MPI_Wtime();

        for (int i = 0; i < iterations; ++i) {
            if (rank == 0) {
                // Ping
                MPI_Send(send_buf.data(), n, MPI_BYTE, 1, 0, MPI_COMM_WORLD);
                // Pong
                MPI_Recv(recv_buf.data(), n, MPI_BYTE, 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            } else if (rank == 1) {
                MPI_Recv(recv_buf.data(), n, MPI_BYTE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                MPI_Send(send_buf.data(), n, MPI_BYTE, 0, 0, MPI_COMM_WORLD);
            }
        }

        double total_time = MPI_Wtime() - t_start;
        // Время в одну сторону
        double one_way_time = total_time / (iterations * 2);

        // Пропускная способность (MB/s)
        double bandwidth_mbs = 0.0;
        if (n > 0 && one_way_time > 1e-9) {
            bandwidth_mbs = (double)n / one_way_time / (1024.0 * 1024.0);
        }

        if (rank == 0) {
            // Формат: Bytes;Iterations;Time;Bandwidth
            std::cout << n << ";"
                      << iterations << ";"
                      << std::scientific << std::setprecision(6) << one_way_time << ";"
                      << std::fixed << std::setprecision(4) << bandwidth_mbs << std::endl;
        }
    }

    MPI_Finalize();
    return 0;
}