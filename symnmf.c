#include <stdlib.h>
#include <math.h>

#define BETA 0.5
#define EPSILON 1e-4
#define SMALL_NUMBER 1e-13
#define MAX_ITER 300

double *transpose_matrix(const double *mat, int n, int k){
    int i, j;
    double *mat_t = malloc(n*k*sizeof(double));
    if(mat_t == NULL) return NULL;
    for(i=0; i<n; i++){
        for(j=0; j<k; j++){
            mat_t[(j*n)+i] = mat[(i*k)+j];
        }
    }
    return mat_t;
}

double *mat_mult(const double *matA, const double *matB, int rowsA, int cols_rows, int colsB){
    int i, j, k;
    double sum;
    double *prod = malloc(rowsA * colsB * sizeof(double));
    if(prod == NULL) return NULL;
    for(i=0; i<rowsA; i++){
        for(j=0; j<colsB; j++){
            sum=0.0;
            for(k=0; k<cols_rows; k++){
                sum += matA[(i*cols_rows) + k]*matB[(k*colsB) + j];
            }
            prod[(i*colsB) + j] = sum;
        }
    }
    return prod;
}

int check_convergence(double *h_new, double *h_old, int n, int k){
    int i, j;
    double sum = 0.0;
    for(i=0; i<n; i++){
        for(j=0; j<k; j++){
            sum += pow(h_new[(i*k) + j] - h_old[(i*k) + j], 2);
        }
    }
    return sum < EPSILON;
}

double *create_h_new(double *old_h, double *w_matrix, int n, int k){
    int i, j;
    double inside;
    double *h_matrix, *old_transpose, *mone, *mehane, *temp;
    h_matrix = malloc(n*k*sizeof(double));
    if(h_matrix == NULL){
        free(old_h);
        return NULL;
    }
    old_transpose = transpose_matrix(old_h, n, k);
    mone = mat_mult(w_matrix, old_h, n, n, k);
    temp = mat_mult(old_h, old_transpose, n, k, n);
    mehane = mat_mult(temp, old_h, n, n, k);
    for(j=0, j<n; j++){
        for(p=0; p<k; p++){
            inside = (mone[(j*k) + p])/(mehane[(j*k) + p] + SMALL_NUMBER);
            h_matrix[(j*k) + p] = old_h[(j*k) + p]*(BETA+(BETA*inside));
        }
        //continue!!!!!!!!!!!!
    }
}

double *converge_h(double *h_matrix, const double *w_matrix, int n, int k){
    int i;
    double *old_h;
    for(i=0; i<MAX_ITER; i++){
        old_h = h_matrix;
        //continue!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!    
    }
}

double *build_w(const double *d_matrix, const double *a_matrix, int n){
    int i,j;
    double d_i, d_j;
    double *w = malloc(n*n*sizeof(double));
    if(w == NULL) return NULL;
    for(i=0; i<n;i++){
        d_i = d_matrix[i] != 0.0 ? 1.0/sqrt(d_matrix[i]) : 0.0;
        for(j=0;j<n;j++){
            d_j = d_matrix[j] != 0.0 ? 1.0/sqrt(d_matrix[j]) : 0.0;
            w[(i*n)+j] = d_i*a_matrix[i*n+j]*d_j;
        }
    }
    return w;
}