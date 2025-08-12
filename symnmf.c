#include <stdlib.h>
#include <math.h>
#include "symnmf.h"

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
// NITS - the comments are for myself as i tend to forget shit in the speed of light - do not worry my dear the formal ones will be wayyyy beter XOXO
double sym_val(const double *point1, const double *point2, int d) // if points saved as dynamic array, else - below
{   
    int i;
    double e_exponent=0.0, sum=0.0;
    double temp;
    
    for(i=0; i<d; i++){
       temp =  point1[i] - point2[i];
       sum += pow(temp,2);
    }
    e_exponent = (-0.5)*sum;
    return (exp(e_exponent));
}


/* else (+add struct cord def): 
double sym_val(struct cord *point1, struct cord *point2) 
{   
    double e_exponent=0.0, sum=0.0;
    double temp;
    
    while(point1 != NULL&& point2 != NULL){
       temp =  point1->value - point2->value;
       sum += pow(temp,2);
       point1 = point1->next; 
       point2 = point2->next;

    }
    e_exponent = (-0.5)*sum;
    return (exp(e_exponent));
}
*/
//#define d after first point was read ?
double *build_a(const double *p_matrix, int n, int d) //p=flattened 1D arr of size n*d (n points, of dim d each)
{
    int i, j;
    double sym_v;
    double *a = malloc((size_t)n*n*sizeof(double));
    if(!a) return NULL;
    for(i=0; i<n;i++){
        for(j=0;j<i;j++){ //calc sym v only under the diag
            sym_v = sym_val(&p_matrix[i * d], &p_matrix[j * d], d); 
            a[i * n + j] = sym_v; 
            a[j * n + i] = sym_v; //a is  symmetric duh
        } 
        a[i * n + i] = 1.0;  //diag is all 1's (e**0)
    }  
    return a;      
    
}
double *build_d(const double *a_matrix, int n) //a_matrix= sym matrix as flattened 1D arr of size n*n 
{
    int i, j;
    double d_i;
    double *d = malloc((size_t)n*sizeof(double));
    if(!d) return NULL;
    for(i=0; i<n;i++){
        d_i = 0.0;
        for(j=0;j<n;j++){ 
            d_i+=a_matrix[(i*n) + j];
        } 
        d[i] = d_i;  
    }  
    return d;
}