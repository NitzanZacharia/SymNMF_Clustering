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
def m_val(norm_matrix): #ok in PY? part of init H...
    norm_mat = np.array(norm_matrix)
    m = np.mean(norm_mat)
    return m


 #assuming str (user's input) is correct as stated on the assignment - double check   
def ex_funcs(str, p_matrix, n, d, k):
    a_mat = ex_sym(p_matrix, n, d)
    if str == "sym":
        return a_mat
    d_mat = ex_ddg(a_mat, n)     
    if str == "ddg":
        return d_mat
    norm_mat = ex_norm(d_mat, a_mat, n)    
    if str == "norm":
        return norm_mat
    m =  m_val(norm_mat)
    h_in = init_h(n, k, m)
    h_mat = ex_symnmf(h_in, norm_mat, n, k)  
    return h_mat 

#***
#NITS - slight chance all ex funcs but ex_ddg are redundant, keeping them for now to handle changes in array shape if needed -XOXO
#****

def ex_sym(p_matrix, n, d): # p_matrix is init_p (make sure to flatten), n is num points and d is dim 
    p_mat_flat = p_matrix.flatten()
    a_mat_flat = symnmf.sym(p_mat_flat, n, d) #asumming returned mat is 1D flattened np array - check with nits
    a_matrix = a_mat_flat.reshape(n,n)
    return a_matrix
    
def ex_ddg(a_matrix, n): # a_matrix is ret val of ex_sym, n is num points 
    a_mat_flat = a_matrix.flatten() 
    d_vec = symnmf.ddg(a_mat_flat, n)
    d_matrix = np.diag(d_vec) 
    return d_matrix

def ex_norm(d_matrix, a_matrix, n):
    a_mat_flat = a_matrix.flatten() 
    d_vec = np.diag(d_matrix)
    norm_matrix_flat = symnmf.norm(d_vec, a_mat_flat, n)
    norm_matrix = norm_matrix_flat.reshape(n, n)
    return norm_matrix

def ex_symnmf(h_matrix, norm_matrix, n, k):
    h_flat = h_matrix.flatten()
    norm_flat = norm_matrix.flatten()
    res_flat = symnmf.symnmf(h_flat, norm_flat, n, k)  
    res_mat = res_flat.reshape(n, n)
    return res_mat

def main():
    args = sys.argv
    k = int(args[1])
    goal = args[2]
    filename = args[3]

    file = pd.read_csv(filename, header=None)
    points = file.to_numpy()
    n = points.shape[0]
    d = points.shape[1]
    res_mat = ex_funcs(goal, points, n, d, k)