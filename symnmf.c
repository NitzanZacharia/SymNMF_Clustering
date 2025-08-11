#include <stdlib.h>
#include <math.h>

#define BETA 0.5
#define EPSILON 1e-4
#define SMALL_NUMBER 1e-13
#define MAX_ITER 300

double *transpose_matrix(const double *mat, int n, int k){
    int i, j;
    double *mat_t = malloc((size_t)n*k*sizeof(double));
    if(!mat_t) return NULL;
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
    if(!prod) return NULL;
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

int check_convergence(const double *h_new, const double *h_old, int n, int k){
    int i, j;
    double sum = 0.0;
    for(i=0; i<n; i++){
        for(j=0; j<k; j++){
            sum += pow(h_new[(i*k) + j] - h_old[(i*k) + j], 2);
        }
    }
    return sum < EPSILON;
}

double *mult_transpose(const double *mat, int n, int k){
    double *transpose, *res, *temp;
    transpose = transpose_matrix(mat, n, k);
    if(!transpose) return NULL;
    temp = mat_mult(transpose, mat, k, n, k);
    if(!temp){
        free(transpose);
        return NULL;
    }
    res = mat_mult(mat, temp, n, k, k);
    free(transpose);
    free(temp);
    return res;
}

double *create_h_new(const double *old_h, const double *w_matrix, int n, int k){
    int i, j;
    double inside;
    double *h_matrix, *mone, *mehane;
    h_matrix = malloc((size_t)n*k*sizeof(double));
    if(!h_matrix) return NULL;
    mone = mat_mult(w_matrix, old_h, n, n, k);
    if(!mone){
        free(h_matrix);
        return NULL;
    }
    mehane = mult_transpose(old_h, n, k);
    if(!mehane){
        free(h_matrix);
        free(mone);
        return NULL;
    }
    for(i=0; i<n; i++){
        for(j=0; j<k; j++){
            inside = (mone[(i*k) + j])/(mehane[(i*k) + j] + SMALL_NUMBER);
            h_matrix[(i*k) + j] = old_h[(i*k) + j]*((1.0-BETA)+(BETA*inside));
        }
    }
    free(mone);
    free(mehane);
    return h_matrix;
}

double *converge_h(double *h_matrix, const double *w_matrix, int n, int k){
    int i, res;
    double *old_h;
    for(i=0; i<MAX_ITER; i++){
        old_h = h_matrix;
        h_matrix = create_h_new(old_h, w_matrix, n, k);
        if(!h_matrix){
            free(old_h);
            return NULL;
        }
        res = check_convergence(h_matrix, old_h, n, k);
        free(old_h);
        if(res) break;
    }
    return h_matrix;
}

double *build_w(const double *d_matrix, const double *a_matrix, int n){
    int i,j;
    double d_i, d_j;
    double *w = malloc((size_t)n*n*sizeof(double));
    if(!w) return NULL;
    for(i=0; i<n;i++){
        d_i = d_matrix[i] != 0.0 ? 1.0/sqrt(d_matrix[i]) : 0.0;
        for(j=0;j<n;j++){
            d_j = d_matrix[j] != 0.0 ? 1.0/sqrt(d_matrix[j]) : 0.0;
            w[(i*n)+j] = d_i*a_matrix[i*n+j]*d_j;
        }
    }
    return w;
}