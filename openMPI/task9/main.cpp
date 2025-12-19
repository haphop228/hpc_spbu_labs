#include <mpi.h>
#include <iostream>
#include <vector>
#include <iomanip>
#include <cstring>
#include <algorithm>

void Custom_Bcast(void* buffer, int count, MPI_Datatype datatype, int root, MPI_Comm comm) {
    int rank, size;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &size);
    
    if (rank == root) {
        for (int i = 0; i < size; i++) {
            if (i != root) {
                MPI_Send(buffer, count, datatype, i, 0, comm);
            }
        }
    } else {
        MPI_Recv(buffer, count, datatype, root, 0, comm, MPI_STATUS_IGNORE);
    }
}

void Custom_Reduce(void* sendbuf, void* recvbuf, int count, MPI_Datatype datatype, 
                    MPI_Op op, int root, MPI_Comm comm) {
    int rank, size;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &size);
    
    if (datatype != MPI_INT || op != MPI_SUM) {
        if (rank == 0) {
            std::cerr << "Custom_Reduce: Only MPI_INT and MPI_SUM supported" << std::endl;
        }
        return;
    }
    
    int* send_data = (int*)sendbuf;
    int* recv_data = (int*)recvbuf;
    
    if (rank == root) {
        std::memcpy(recv_data, send_data, count * sizeof(int));
        
        std::vector<int> temp(count);
        for (int i = 0; i < size; i++) {
            if (i != root) {
                MPI_Recv(temp.data(), count, MPI_INT, i, 0, comm, MPI_STATUS_IGNORE);
                for (int j = 0; j < count; j++) {
                    recv_data[j] += temp[j];
                }
            }
        }
    } else {
        MPI_Send(send_data, count, MPI_INT, root, 0, comm);
    }
}

void Custom_Scatter(void* sendbuf, int sendcount, MPI_Datatype sendtype,
                    void* recvbuf, int recvcount, MPI_Datatype recvtype,
                    int root, MPI_Comm comm) {
    int rank, size;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &size);
    
    if (sendtype != MPI_INT || recvtype != MPI_INT) {
        if (rank == 0) {
            std::cerr << "Custom_Scatter: Only MPI_INT supported" << std::endl;
        }
        return;
    }
    
    int* send_data = (int*)sendbuf;
    int* recv_data = (int*)recvbuf;
    
    if (rank == root) {
        std::memcpy(recv_data, send_data, sendcount * sizeof(int));
        
        for (int i = 0; i < size; i++) {
            if (i != root) {
                MPI_Send(send_data + i * sendcount, sendcount, MPI_INT, i, 0, comm);
            }
        }
    } else {
        MPI_Recv(recv_data, recvcount, MPI_INT, root, 0, comm, MPI_STATUS_IGNORE);
    }
}

void Custom_Gather(void* sendbuf, int sendcount, MPI_Datatype sendtype,
                   void* recvbuf, int recvcount, MPI_Datatype recvtype,
                   int root, MPI_Comm comm) {
    int rank, size;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &size);
    
    if (sendtype != MPI_INT || recvtype != MPI_INT) {
        if (rank == 0) {
            std::cerr << "Custom_Gather: Only MPI_INT supported" << std::endl;
        }
        return;
    }
    
    int* send_data = (int*)sendbuf;
    int* recv_data = (int*)recvbuf;
    
    if (rank == root) {
        std::memcpy(recv_data, send_data, sendcount * sizeof(int));
        
        for (int i = 0; i < size; i++) {
            if (i != root) {
                MPI_Recv(recv_data + i * recvcount, recvcount, MPI_INT, i, 0, comm, MPI_STATUS_IGNORE);
            }
        }
    } else {
        MPI_Send(send_data, sendcount, MPI_INT, root, 0, comm);
    }
}

void Custom_Allgather(void* sendbuf, int sendcount, MPI_Datatype sendtype,
                      void* recvbuf, int recvcount, MPI_Datatype recvtype,
                      MPI_Comm comm) {
    int rank, size;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &size);
    
    if (sendtype != MPI_INT || recvtype != MPI_INT) {
        if (rank == 0) {
            std::cerr << "Custom_Allgather: Only MPI_INT supported" << std::endl;
        }
        return;
    }
    
    int* send_data = (int*)sendbuf;
    int* recv_data = (int*)recvbuf;
    
    std::memcpy(recv_data + rank * recvcount, send_data, sendcount * sizeof(int));
    
    for (int i = 0; i < size; i++) {
        if (i != rank) {
            MPI_Sendrecv(send_data, sendcount, MPI_INT, i, 0,
                        recv_data + i * recvcount, recvcount, MPI_INT, i, 0,
                        comm, MPI_STATUS_IGNORE);
        }
    }
}

void Custom_Alltoall(void* sendbuf, int sendcount, MPI_Datatype sendtype,
                     void* recvbuf, int recvcount, MPI_Datatype recvtype,
                     MPI_Comm comm) {
    int rank, size;
    MPI_Comm_rank(comm, &rank);
    MPI_Comm_size(comm, &size);
    
    if (sendtype != MPI_INT || recvtype != MPI_INT) {
        if (rank == 0) {
            std::cerr << "Custom_Alltoall: Only MPI_INT supported" << std::endl;
        }
        return;
    }
    
    int* send_data = (int*)sendbuf;
    int* recv_data = (int*)recvbuf;
    
    std::memcpy(recv_data + rank * recvcount, send_data + rank * sendcount, sendcount * sizeof(int));
    
    for (int i = 0; i < size; i++) {
        if (i != rank) {
            MPI_Sendrecv(send_data + i * sendcount, sendcount, MPI_INT, i, 0,
                        recv_data + i * recvcount, recvcount, MPI_INT, i, 0,
                        comm, MPI_STATUS_IGNORE);
        }
    }
}

void benchmark_operation(const std::string& op_name, int data_size, int iterations) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    std::vector<int> send_data(data_size * size);
    std::vector<int> recv_data(data_size * size);
    std::vector<int> local_data(data_size);
    
    for (int i = 0; i < data_size * size; i++) {
        send_data[i] = rank * 100 + i;
    }
    for (int i = 0; i < data_size; i++) {
        local_data[i] = rank * 100 + i;
    }
    
    double custom_time = 0.0, mpi_time = 0.0;
    
    MPI_Barrier(MPI_COMM_WORLD);
    double t_start = MPI_Wtime();
    
    for (int iter = 0; iter < iterations; iter++) {
        if (op_name == "Broadcast") {
            Custom_Bcast(local_data.data(), data_size, MPI_INT, 0, MPI_COMM_WORLD);
        } else if (op_name == "Reduce") {
            Custom_Reduce(local_data.data(), recv_data.data(), data_size, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);
        } else if (op_name == "Scatter") {
            Custom_Scatter(send_data.data(), data_size, MPI_INT, local_data.data(), data_size, MPI_INT, 0, MPI_COMM_WORLD);
        } else if (op_name == "Gather") {
            Custom_Gather(local_data.data(), data_size, MPI_INT, recv_data.data(), data_size, MPI_INT, 0, MPI_COMM_WORLD);
        } else if (op_name == "Allgather") {
            Custom_Allgather(local_data.data(), data_size, MPI_INT, recv_data.data(), data_size, MPI_INT, MPI_COMM_WORLD);
        } else if (op_name == "Alltoall") {
            Custom_Alltoall(send_data.data(), data_size, MPI_INT, recv_data.data(), data_size, MPI_INT, MPI_COMM_WORLD);
        }
    }
    
    custom_time = (MPI_Wtime() - t_start) / iterations;
    
    MPI_Barrier(MPI_COMM_WORLD);
    t_start = MPI_Wtime();
    
    for (int iter = 0; iter < iterations; iter++) {
        if (op_name == "Broadcast") {
            MPI_Bcast(local_data.data(), data_size, MPI_INT, 0, MPI_COMM_WORLD);
        } else if (op_name == "Reduce") {
            MPI_Reduce(local_data.data(), recv_data.data(), data_size, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);
        } else if (op_name == "Scatter") {
            MPI_Scatter(send_data.data(), data_size, MPI_INT, local_data.data(), data_size, MPI_INT, 0, MPI_COMM_WORLD);
        } else if (op_name == "Gather") {
            MPI_Gather(local_data.data(), data_size, MPI_INT, recv_data.data(), data_size, MPI_INT, 0, MPI_COMM_WORLD);
        } else if (op_name == "Allgather") {
            MPI_Allgather(local_data.data(), data_size, MPI_INT, recv_data.data(), data_size, MPI_INT, MPI_COMM_WORLD);
        } else if (op_name == "Alltoall") {
            MPI_Alltoall(send_data.data(), data_size, MPI_INT, recv_data.data(), data_size, MPI_INT, MPI_COMM_WORLD);
        }
    }
    
    mpi_time = (MPI_Wtime() - t_start) / iterations;
    
    if (rank == 0) {
        double speedup = custom_time / mpi_time;
        std::cout << op_name << ";" 
                  << size << ";"
                  << data_size << ";"
                  << std::scientific << std::setprecision(6) << custom_time << ";"
                  << mpi_time << ";"
                  << std::fixed << std::setprecision(4) << speedup << std::endl;
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (rank == 0) {
        std::cout << "Operation;Processes;DataSize;CustomTime;MPITime;Speedup" << std::endl;
    }
    
    std::vector<std::string> operations = {
        "Broadcast", "Reduce", "Scatter", "Gather", "Allgather", "Alltoall"
    };
    
    std::vector<int> data_sizes = {1, 10, 100, 1000, 10000, 100000};
    
    int iterations = 100;
    
    for (const auto& op : operations) {
        for (int data_size : data_sizes) {
            int iter = iterations;
            if (data_size >= 10000) iter = 20;
            if (data_size >= 100000) iter = 10;
            
            benchmark_operation(op, data_size, iter);
        }
    }
    
    MPI_Finalize();
    return 0;
}
