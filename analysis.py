import numpy as np
import pandas as pd
import sys
import symnmf
#import kmeansapp?
def aDist(points, clust_ind, p_ind, d)
{
    c_id = clust_ind[p_ind] #ind of the cluster p is in
    c_all = np.where((clust_ind == c_id))[0] #vector of row inds of all other points in same cluster
    c_all = c_all[c_all != p_ind] #exclude p
    if len(c_all) == 0: #if p is the only one in its cluster
        return 0 #or other way to handle!!! dont forget
    dists = [getDistance(points[p_ind], points[j],d) for j in c_all]
    return np.mean(dists)

}

def getDistance(point1, point2,d):
    dist = 0
    for i in range(d):
        diff = float(point1[i])-float(point2[i])
        dist += diff*diff
    return math.sqrt(dist) #sqrt???

def main():
    args = sys.argv
    goal = "symnmf"
    k = int(args[1])
    filename = args[2]
    file = pd.read_csv(filename, header=None)
    points_arr = file.to_numpy()
    n = points_arr.shape[0]
    d = points.shape[1]
    points = points_arr.tolist()
    
    res = symnmf.ex_funcs(goal, points, n, k)
    res_mat = np.array(res)
    cluster_ind = np.argsmax(res_mat, axis=1) #1D vector so that cluster_ind[i] = cluster num (in range(0,k)) point i was assigned to 
    
    