#include <stdio.h>
#include <stdlib.h>
#include <omp.h> // OpenMP
#include <float.h>
#include <time.h>
#include <string.h>

// объявляем функции
double find_min_with_reduction(double *arr, long long n, int num_threads);
double find_min_without_reduction(double *arr, long long n, int num_threads, double *thread_storage);
double find_max_with_reduction(double *arr, long long n, int num_threads);
double find_max_without_reduction(double *arr, long long n, int num_threads, double *thread_storage);
void generate_random_array(double *arr, long long n);
void print_json_result(const char *method, const char *operation, int threads,
                       long long size, double result, double time_ms, int run, int is_last);

int main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Usage: %s <size> <threads> <method> <runs>\n", argv[0]);
        fprintf(stderr, "  method: reduction | no-reduction\n");
        fprintf(stderr, "  Example: %s 1000000 4 reduction 10\n", argv[0]);
        return 1;
    }

    long long size = atoll(argv[1]);
    int num_threads = atoi(argv[2]);
    char *method = argv[3];
    int num_runs = atoi(argv[4]);

    if (size <= 0 || num_threads <= 0 || num_runs <= 0) {
        fprintf(stderr, "Error: Invalid parameters\n");
        return 1;
    }

    double *arr = (double *)malloc(size * sizeof(double));
    if (arr == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        return 1;
    }

    srand(time(NULL));
    generate_random_array(arr, size);

    omp_set_num_threads(num_threads);

    int use_reduction = (strcmp(method, "reduction") == 0);

    double *thread_storage = NULL;
    if (!use_reduction) {
        thread_storage = (double *)malloc(num_threads * sizeof(double));
        if (thread_storage == NULL) {
            fprintf(stderr, "Error: Thread storage allocation failed\n");
            free(arr);
            return 1;
        }
    }

    double warmup_result;
    if (use_reduction) {
        warmup_result = find_min_with_reduction(arr, size, num_threads);
    } else {
        warmup_result = find_min_without_reduction(arr, size, num_threads, thread_storage);
    }
    (void)warmup_result;

    for (int run = 0; run < num_runs; run++) {
        double start_time, end_time, elapsed_time;
        double result;

        start_time = omp_get_wtime();
        if (use_reduction) {
            result = find_min_with_reduction(arr, size, num_threads);
        } else {
            result = find_min_without_reduction(arr, size, num_threads, thread_storage);
        }
        end_time = omp_get_wtime();
        elapsed_time = (end_time - start_time) * 1000.0;
        
        print_json_result(method, "min", num_threads, size, result, elapsed_time, run, 0);

        start_time = omp_get_wtime();
        if (use_reduction) {
            result = find_max_with_reduction(arr, size, num_threads);
        } else {
            result = find_max_without_reduction(arr, size, num_threads, thread_storage);
        }
        end_time = omp_get_wtime();
        elapsed_time = (end_time - start_time) * 1000.0;
        
        int is_last = (run == num_runs - 1);
        print_json_result(method, "max", num_threads, size, result, elapsed_time, run, is_last);
    }

    if (thread_storage != NULL) {
        free(thread_storage);
    }
    free(arr);
    return 0;
}

double find_min_with_reduction(double *arr, long long n, int num_threads) {
    double min_val = DBL_MAX;
    
    #pragma omp parallel for reduction(min:min_val) num_threads(num_threads)
    for (long long i = 0; i < n; i++) {
        if (arr[i] < min_val) {
            min_val = arr[i];
        }
    }
    
    return min_val;
}

double find_min_without_reduction(double *arr, long long n, int num_threads, double *thread_storage) {
    for (int i = 0; i < num_threads; i++) {
        thread_storage[i] = DBL_MAX;
    }
    
    #pragma omp parallel num_threads(num_threads)
    {
        int tid = omp_get_thread_num();
        double local_min = DBL_MAX;
        
        #pragma omp for
        for (long long i = 0; i < n; i++) {
            if (arr[i] < local_min) {
                local_min = arr[i];
            }
        }
        
        thread_storage[tid] = local_min;
    }
    
    double global_min = DBL_MAX;
    for (int i = 0; i < num_threads; i++) {
        if (thread_storage[i] < global_min) {
            global_min = thread_storage[i];
        }
    }
    
    return global_min;
}

double find_max_with_reduction(double *arr, long long n, int num_threads) {
    double max_val = -DBL_MAX;
    
    #pragma omp parallel for reduction(max:max_val) num_threads(num_threads)
    for (long long i = 0; i < n; i++) {
        if (arr[i] > max_val) {
            max_val = arr[i];
        }
    }
    
    return max_val;
}

double find_max_without_reduction(double *arr, long long n, int num_threads, double *thread_storage) {
    for (int i = 0; i < num_threads; i++) {
        thread_storage[i] = -DBL_MAX;
    }
    
    #pragma omp parallel num_threads(num_threads)
    {
        int tid = omp_get_thread_num();
        double local_max = -DBL_MAX;
        
        #pragma omp for
        for (long long i = 0; i < n; i++) {
            if (arr[i] > local_max) {
                local_max = arr[i];
            }
        }
        
        thread_storage[tid] = local_max;
    }
    
    double global_max = -DBL_MAX;
    for (int i = 0; i < num_threads; i++) {
        if (thread_storage[i] > global_max) {
            global_max = thread_storage[i];
        }
    }
    
    return global_max;
}

void generate_random_array(double *arr, long long n) {
    for (long long i = 0; i < n; i++) {
        arr[i] = ((double)rand() / RAND_MAX) * 2000.0 - 1000.0;
    }
}

void print_json_result(const char *method, const char *operation, int threads,
                       long long size, double result, double time_ms, int run, int is_last) {
    printf("{\"method\":\"%s\",\"operation\":\"%s\",\"threads\":%d,\"size\":%lld,"
           "\"result\":%.6f,\"time_ms\":%.6f,\"run\":%d}",
           method, operation, threads, size, result, time_ms, run);
    
    if (!is_last) {
        printf(",");
    }
    printf("\n");
    fflush(stdout);
}
