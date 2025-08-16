import math
import sys
import numpy as np

e = 0.001

#calculates the distance between two points
def getDistance(point1, point2):
    """
    Compute Euclidean distance between two points.

    Args:
        point1 (list[float]): First point.
        point2 (list[float]): Second point.

    Returns:
        float: Euclidean distance.
    """
    d = len(point1)
    dist = 0
    for i in range(d):
        diff = float(point1[i])-float(point2[i])
        dist += diff*diff
    return math.sqrt(dist)

#updates the centroids after we insert all points       
def update_center(clusters):
    """
    Compute new centroids after we insert all points.

    Args:
        clusters (list[list[list[float]]]): List of clusters, each has a list of points.

    Returns:
        list[list[float]]: Updated centroids.
    """
    d = len(clusters[0][0])
    centers = []
    for cluster in clusters:
        up_center= []
        for i in range(d): 
            s = 0
            for point in cluster:
                s+=point[i]
            up_center.append(s/len(cluster))
        centers.append(up_center)
    return centers    

#returns a tupple of clusters, cluts_id= list of indexes of the clusters each point was assigned to
#given the current centroids and the points, sorts the points
#to their closest centroid 
def sort_points(points, centroids):
    """
    Sorts points to nearest centroid.

    Args:
        points (list[list[float]]): Input points.
        centroids (list[list[float]]): Current centroids.

    Returns:
            clusters (list[list[list[float]]]): Points grouped by nearest centroid.
            clusts_ind (list[int]): List of indexes of the clusters each point was assigned to.
    """
    clusters = [[] for i in range(len(centroids))]
    clusts_ind = [] 
    for p_ind in range(len(points)): 
        point = points[p_ind] 
        minDist = math.inf
        centIdx = len(centroids)
        for i in range(len(centroids)):
            centroid = centroids[i]
            dist = getDistance(centroid, point)
            if dist<minDist:
                minDist = dist
                centIdx = i
        clusters[centIdx].append(point)
        clusts_ind.append(centIdx) 
    return clusters, clusts_ind 

#checks if the centroids converged enough
def e_convergence(prev_ctr, up_ctr):
     """
    Check if centroids converged.

    Args:
        prev_ctr (list[list[float]]): Previous centroids.
        up_ctr (list[list[float]]): Updated centroids.

    Returns:
        bool: True if converged, False otherwise.
    """
    for i in range(len(prev_ctr)):
        if(getDistance(prev_ctr[i],up_ctr[i]))>=e:
            return False
    return True

#when the sorting is done, print to the screen
def print_centroids(centroids):
    """
    Print centroids in formatted output.

    Args:
        centroids (list[list[float]]): Centroids to print.
    """
    for centroid in centroids:
        print(",".join(f"{x:.4f}" for x in centroid))  

#create points from stdin
def create_points(input_data):
    """
    Parse input data into points.

    Args:
        input_data (list[str]): Input lines, each a comma-separated point.

    Returns:
        list[list[float]]: List of the data points.
    """
    points = []
    for line in input_data:
        numbers = [float(x) for x in line.strip().split(',')]
        points.append(numbers)
    return points

#validates input
def check_validation(k, n ,iter):
    """
    Validate input.

    Args:
        k (str): Number of clusters.
        n (int): Number of points.
        iter (str): Number of iterations.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        knum = float(k)
        if ((not knum.is_integer()) or knum>=n or knum<2):
            print("Incorrect number of clusters!")
            return False
    except:
        print("Incorrect number of clusters!")
        return False
    try:
        iternum = float(iter)
        if ((not iternum.is_integer()) or iternum>=1000 or iternum<2):
            print("Incorrect number of iteration!")
            return False
    except:
        print("Incorrect number of iteration!")
        return False
    return True

def final_clusters(points_arr, k):
    """
    Cluster the data points into k clusters until convergence.

    Args:
        points_arr (numpy.ndarray): Input points as NumPy array.
        k (int): Number of clusters.

    Returns:
        numpy.ndarray: Cluster indices each point was assigned to.
    """
    points = points_arr.tolist()
    centroids = [points[i] for i in range(k)]
    for i in range(300): #default iter is 300
            clusters, clusters_indexs = sort_points(points, centroids)
            new_cents = update_center(clusters)
            if e_convergence(centroids, new_cents):
                break
            centroids = new_cents
    final_clusters_indexs = np.array(clusters_indexs)
    return final_clusters_indexs            

def main():
    try:
        args = sys.argv
        input_data = sys.stdin.readlines()
        n = len(input_data)
        if len(args) == 2:
            args.append("400")
        
        #if input is not valid, print an error message and end the run
        valid_input = check_validation(args[1],n, args[2])
        if not valid_input:
            return
        k = int(float(args[1]))
        iter = int(float(args[2]))

        #parse the input from the file to create the datapoints
        points = create_points(input_data)
        centroids = [points[i] for i in range(k)]

        #re-devide the datapoints into the clusters iff
        #the centroids convergence is not 0.001 or we didnt 
        #reach 400 iterations
        for i in range(iter):
            clusters = sort_points(points, centroids)
            new_cents = update_center(clusters)
            if e_convergence(centroids, new_cents):
                break
            centroids = new_cents
        print_centroids(centroids)

    except:
        print("An Error Has Occured")

    
if __name__ == "__main__":
    main()