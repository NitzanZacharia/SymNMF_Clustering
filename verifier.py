import sys, math
import numpy as np

# ---- constants from C code ----
BETA = 0.5
EPSILON = 1e-4
SMALL_NUMBER = 1e-13
MAX_ITER = 300
np.random.seed(1234)  # same as Python wrapper

def read_points(path):
    X = np.loadtxt(path, delimiter=",", dtype=float)
    if X.ndim == 1:  # handle 1D case
        X = X.reshape(-1, 1)
    return X

def build_a(X):
    # symmetric affinity matrix
    sq_dists = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2)
    A = np.exp(-0.5 * sq_dists)
    np.fill_diagonal(A, 0.0)
    return A

def build_d(A):
    # degree vector (row sums)
    return A.sum(axis=1)

def build_d_matrix(D_vec):
    return np.diag(D_vec)

def build_w(D_vec, A):
    invsqrt = np.where(D_vec != 0.0, 1.0 / np.sqrt(D_vec), 0.0)
    return (invsqrt[:, None] * A) * invsqrt[None, :]

def init_H(W, n, k):
    m = W.mean()
    high = 2.0 * math.sqrt(m / k) if k > 0 else 0.0
    return np.random.uniform(low=0.0, high=high, size=(n, k))

def HHTH(H):
    return H @ (H.T @ H)

def converge_H(H, W):
    for _ in range(MAX_ITER):
        old = H
        numer = W @ old
        denom = HHTH(old) + SMALL_NUMBER
        H = old * ((1.0 - BETA) + BETA * (numer / denom))
        if np.sum((H - old) ** 2) < EPSILON:
            break
    return H

def fmt4_matrix(mat):
    return "\n".join(",".join(f"{x:.4f}" for x in row) for row in mat)

def main():
    if len(sys.argv) != 4:
        print("Usage: python verify_symnmf.py <k> <goal> <input-file>")
        print("goal ∈ {sym, ddg, norm, symnmf}")
        sys.exit(1)

    k = int(sys.argv[1])
    goal = sys.argv[2]
    path = sys.argv[3]

    X = read_points(path)
    n = X.shape[0]

    A = build_a(X)
    D_vec = build_d(A)
    D_mat = build_d_matrix(D_vec)
    W = build_w(D_vec, A)

    if goal == "sym":
        print(fmt4_matrix(A))
    elif goal == "ddg":
        print(fmt4_matrix(D_mat))
    elif goal == "norm":
        print(fmt4_matrix(W))
    elif goal == "symnmf":
        H0 = init_H(W, n, k)
        Hf = converge_H(H0, W)
        print(fmt4_matrix(Hf))
    else:
        print(f"Unknown goal: {goal}")
        sys.exit(1)

if __name__ == "__main__":
    main()
