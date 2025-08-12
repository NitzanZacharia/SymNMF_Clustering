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

def main():
    args = sys.argv
    k = args[1]
    goal = args[2]
    filename = args[3]