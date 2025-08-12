import numpy as np
import pandas as pd
import sys
import symnmf

np.random.seed(1234)

def init_h(n, k, m):
    return np.random.uniform(
        low=0.0,
        high=2 * np.sqrt(m/k),
        size=(n, k)
    )
 #assuming str (user's input) is correct as stated on the assignment - double check   
def ex_funcs(str, p_matrix, n, d, k, m):
   # all_funcs = [symnmf.sym, symnmf.ddg, symnmf.norm, symnmf.symnmf]
    #res_mat = []
    a_mat = ex_sym(p_matrix, n, d)
    if str == "sym":
        return a_mat
    d_mat =  ex_ddg(a_mat, n)     
    if str == "ddg":
        return d_mat
    norm_mat = ex_norm(d_mat, a_mat, n)    
    if str == "norm":
        return norm_mat
    h_in = init_h(n, k, m)
    h_mat = ex_symnmf(h_in, norm_mat, n, k)  
    return h_mat 

def ex_sym(p_matrix, n, d): # p_matrix is ret val of init_p (make sure to flatten), n is num points and d is dim 
    a_matrix = symnmf.sym(p_matrix, n, d)
    return a_matrix
    
def ex_ddg(a_matrix, n): # a_matrix is ret val of ex_sym, n is num points 
    d_vec = symnmf.ddg(a_matrix, n)
    d_mat =  np.diag(d_vec) #np.diagflat??
    d_matrix = d_mat.flatten() #2 lines cause not sure on the prev line
    return d_matrix

    
def main():
    args = sys.argv
    k = args[1]
    goal = args[2]
    filename = args[3]

    file = pd.read_csv(filename, header=None)
    points = file.to_numpy()
    n = points.shape[0]
    d = points.shape[1]