import numpy as np
import pandas as pd
import sys
import symnmf
#import kmeansapp?

def main():
    args = sys.argv
    goal = "symnmf"
    k = int(args[1])
    filename = args[2]
    file = pd.read_csv(filename, header=None)
    points_arr = file.to_numpy()
    n = points_arr.shape[0]
    points = points_arr.tolist()
    #d = points.shape[1]
    res = symnmf.ex_funcs(goal, points, n, k)
    res_mat = np.array(res)
    