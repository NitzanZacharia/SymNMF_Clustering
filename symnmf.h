#ifndef SYMNMF_H  
#define SYMNMF_H

double *converge_h(double *h_matrix, const double *w_matrix, int n, int k);
double *build_w(const double *d_matrix, const double *a_matrix, int n);
double *build_a(const double *p_matrix, int n, int d);
double *build_d(const double *a_matrix, int n);

#endif 