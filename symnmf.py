import numpy as np
import pandas as pd
import sys
import symnmf_c as symnmf

np.random.seed(1234)

def init_h(n, k, m):
    return np.random.uniform(
        low=0.0,
        high=2 * np.sqrt(m/k),
        size=(n, k)
    )

def m_val(norm_matrix):
    m = np.mean(norm_matrix)
    return m
 
def ex_funcs(str, p_matrix, n, k):
    match str:
        case "sym":
            a_mat = symnmf.sym(p_matrix)
            return a_mat
        case "ddg":
            d_mat = symnmf.ddg(p_matrix)
            return d_mat
        case "norm":
            norm_mat = symnmf.norm(p_matrix)
            return norm_mat
        case _:
            norm = symnmf.norm(p_matrix)
            norm_mat = np.array(norm)       
            m =  m_val(norm_mat)
            h_in = init_h(n, k, m)
            h_mat = symnmf.symnmf(h_in.tolist(), norm, n, k) 
            return h_mat 

def print_d(mat, n):
    for i in range(n):
        for j in range(n):
            if i == j:
                print(f"{mat[i]:.4f}", end="")
            else:
                print("0.0000", end="")
            if j < n - 1:
                print(",", end="")
        print()  

def main():
    try:
        args = sys.argv
        k = int(args[1])
        goal = args[2]
        filename = args[3]
        file = pd.read_csv(filename, header=None)
        points_arr = file.to_numpy()
        n = points_arr.shape[0]
        points = points_arr.tolist()
        res = ex_funcs(goal, points, n, k)
        res_mat = np.array(res)
        if(goal == "ddg"):
            print_d(res_mat, n)
        else:
            for row in res_mat:
                print(','.join(f"{val:.4f}" for val in row))
    except Exception as e:
        print("An Error Has Occurred")

if __name__ == "__main__":
    main()