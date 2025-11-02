/*
 * OpenMP Task 1: Finding Minimum/Maximum Value in Vector
 * Implements both reduction and non-reduction approaches
 */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <float.h>
#include <time.h>
#include <string.h>

// Function prototypes
double find_min_with_reduction(double *arr, long long n, int num_threads);
double find_min_without_reduction(double *arr, long long n, int num_threads);
double find_max_with_reduction(double *arr, long long n, int num_threads);
double find_max_without_reduction(double *arr, long long n, int num_threads);
void generate_random_array(double *arr, long long n);
void print_json_result(const char *method, const char *operation, int threads, 
                       long long size, double result, double time_ms, int run);

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

    // Validate inputs
    if (size <= 0 || num_threads <= 0 || num_runs <= 0) {
        fprintf(stderr, "Error: Invalid parameters\n");
        return 1;
    }

    // Allocate array
    double *arr = (double *)malloc(size * sizeof(double));
    if (arr == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        return 1;
    }

    // Generate random data (not timed)
    srand(time(NULL));
    generate_random_array(arr, size);

    // Set number of threads
    omp_set_num_threads(num_threads);

    // Determine which method to use
    int use_reduction = (strcmp(method, "reduction") == 0);

    // Run benchmarks
    for (int run = 0; run < num_runs; run++) {
        double start_time, end_time, elapsed_time;
        double result;

        // Find minimum
        start_time = omp_get_wtime();
        if (use_reduction) {
            result = find_min_with_reduction(arr, size, num_threads);
        } else {
            result = find_min_without_reduction(arr, size, num_threads);
        }
        end_time = omp_get_wtime();
        elapsed_time = (end_time - start_time) * 1000.0; // Convert to ms
        
        print_json_result(method, "min", num_threads, size, result, elapsed_time, run);

        // Find maximum
        start_time = omp_get_wtime();
        if (use_reduction) {
            result = find_max_with_reduction(arr, size, num_threads);
        } else {
            result = find_max_without_reduction(arr, size, num_threads);
        }
        end_time = omp_get_wtime();
        elapsed_time = (end_time - start_time) * 1000.0; // Convert to ms
        
        print_json_result(method, "max", num_threads, size, result, elapsed_time, run);
    }

    free(arr);
    return 0;
}

// Find minimum using OpenMP reduction
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

// Find minimum without using reduction (manual approach)
double find_min_without_reduction(double *arr, long long n, int num_threads) {
    double *thread_mins = (double *)malloc(num_threads * sizeof(double));
    
    // Initialize thread-local minimums
    for (int i = 0; i < num_threads; i++) {
        thread_mins[i] = DBL_MAX;
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
        
        thread_mins[tid] = local_min;
    }
    
    // Find global minimum from thread minimums
    double global_min = DBL_MAX;
    for (int i = 0; i < num_threads; i++) {
        if (thread_mins[i] < global_min) {
            global_min = thread_mins[i];
        }
    }
    
    free(thread_mins);
    return global_min;
}

// Find maximum using OpenMP reduction
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

// Find maximum without using reduction (manual approach)
double find_max_without_reduction(double *arr, long long n, int num_threads) {
    double *thread_maxs = (double *)malloc(num_threads * sizeof(double));
    
    // Initialize thread-local maximums
    for (int i = 0; i < num_threads; i++) {
        thread_maxs[i] = -DBL_MAX;
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
        
        thread_maxs[tid] = local_max;
    }
    
    // Find global maximum from thread maximums
    double global_max = -DBL_MAX;
    for (int i = 0; i < num_threads; i++) {
        if (thread_maxs[i] > global_max) {
            global_max = thread_maxs[i];
        }
    }
    
    free(thread_maxs);
    return global_max;
}

// Generate random array
void generate_random_array(double *arr, long long n) {
    for (long long i = 0; i < n; i++) {
        arr[i] = ((double)rand() / RAND_MAX) * 2000.0 - 1000.0; // Range: -1000 to 1000
    }
}

// Print result in JSON format for easy parsing
void print_json_result(const char *method, const char *operation, int threads, 
                       long long size, double result, double time_ms, int run) {
    printf("{\"method\":\"%s\",\"operation\":\"%s\",\"threads\":%d,\"size\":%lld,"
           "\"result\":%.6f,\"time_ms\":%.6f,\"run\":%d}\n",
           method, operation, threads, size, result, time_ms, run);
    fflush(stdout);
}