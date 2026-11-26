# Genera los dos datasets y los guarda como csv con cabecera
import numpy as np, pandas as pd
from sklearn.datasets import make_moons, make_blobs
from sklearn.preprocessing import StandardScaler

X, _ = make_moons(n_samples=10000, noise=0.07, random_state=0)
pd.DataFrame(StandardScaler().fit_transform(X), columns=["x1", "x2"]).to_csv("datos/moons_2d.csv", index=False)

X, _ = make_blobs(n_samples=5000, n_features=6, centers=4, cluster_std=1.0, random_state=0)
cols = [f"x{i+1}" for i in range(6)]
pd.DataFrame(StandardScaler().fit_transform(X), columns=cols).to_csv("datos/blobs_6d.csv", index=False)
