import numpy as np
import pandas as pd
import sys
import symnmf
from kmeanshw1 import final_clusters
from sklearn.metrics import silhouette_score


def get_points(f_name): #gets file name, returns a tuple of (X, n, d) when X=2D numpy array of data points, n = num of points, d = dim of points
    dfp = pd.read_csv(f_name, header=None)
    points= dfp.to_numpy()
    num_p = points.shape[0]
    dim_p = points.shape[1]
    return points, num_p, dim_p
'''
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
    '''
def get_sym_culsters(goal, points_arr, n, k): #(basically manual fit_predict() ) gets goal="symnmf", n=num points, k=num clusts, points_arr=2D numpy array of the points, returns 1D vector so that cluster_ind[i] = cluster num (in range(0,k)) point i was assigned to 
    points = points_arr.tolist()
    res = symnmf.ex_funcs(goal, points, n, k) #gets final H as nested list
    res_arr = np.array(res)
    cluster_ind = np.argsmax(res_arr, axis=1) #since point that is row i match cluster in col j (in H) where H_ij is maximal
    return cluster_ind

def get_kmeans_clusters(points, k):
    cents, clusts, cluster_inds = final_clusters(points, k)



def main():
    try:
        args = sys.argv
        goal = "symnmf"
        k = int(args[1])
        filename = args[2]
        X, n, d = get_points(filename)
        Y_sym = get_sym_culsters(goal, X, n, k)
        sym_s_score = silhouette_score(X, Y_sym) #silhouette score of the sym clustering
        cents, clusts, Y_kmeans = final_clusters(X, k)
        kmeans_s_score = silhouette_score(X, Y_kmeans)
        print(f"nmf: {sym_s_score:.4f}")
        print(f"kmeans: {kmeans_s_score:.4f}")
    except:
        print("An Error Has Occured")
if __name__ == "__main__":
    main()    