import sys, os, re, subprocess
import numpy as np, pandas as pd, matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ruta = sys.argv[1]
df = pd.read_csv(ruta, sep=None, engine="python")
if any(re.fullmatch(r"-?[\d.]+(e-?\d+)?", str(c)) for c in df.columns):   # no habia cabecera
    df = pd.read_csv(ruta, sep=None, engine="python", header=None)
X = df.select_dtypes(include=[np.number]).dropna().values
X = StandardScaler().fit_transform(X)                                      # misma escala en todas las columnas
n, d = X.shape
print(f"Datos: {n} puntos, {d} dimensiones")

minPts = int(sys.argv[3]) if len(sys.argv) > 3 else max(4, 2 * d)
if len(sys.argv) > 2:
    eps = float(sys.argv[2])
else:                                                                      # eps sugerido
    kd = np.sort(NearestNeighbors(n_neighbors=minPts).fit(X).kneighbors(X)[0][:, -1])
    x = np.arange(n); p1, p2 = np.array([0, kd[0]]), np.array([n - 1, kd[-1]])
    v = p2 - p1; w = np.c_[x, kd] - p1
    dist = np.abs(v[0] * w[:, 1] - v[1] * w[:, 0]) / np.linalg.norm(v)
    eps = float(kd[dist.argmax()])
    print(f"eps sugerido (codo k-distance): {eps:.4f}")
print(f"eps={eps:.4f} minPts={minPts}")

pd.DataFrame(X, columns=[f"x{i}" for i in range(d)]).to_csv("limpio_tmp.csv", index=False)
exe = "dbscan.exe" if os.name == "nt" else "./dbscan"
salida = subprocess.run([exe, "limpio_tmp.csv", str(eps), str(minPts), "etiquetas_tmp.csv"], capture_output=True, text=True).stdout
print(salida.strip())
et = pd.read_csv("etiquetas_tmp.csv")["etiqueta"].values
os.remove("limpio_tmp.csv"); os.remove("etiquetas_tmp.csv")

outliers = int((et == -1).sum()); clusters = len(set(et) - {-1})
print(f"OUTLIERS: {outliers}   CLUSTERS: {clusters}")
m = et != -1
if clusters >= 2: print(f"SILHOUETTE (sin outliers): {silhouette_score(X[m], et[m]):.4f}")
else: print("SILHOUETTE: no se puede calcular (menos de 2 clusters)")

X2 = X if d == 2 else PCA(2).fit_transform(X)
plt.figure(figsize=(6, 5))
plt.scatter(X2[m, 0], X2[m, 1], c=et[m], s=6, cmap="tab10")
plt.scatter(X2[~m, 0], X2[~m, 1], c="k", s=10, marker="x", label="outliers")
plt.title(f"DBSCAN eps={eps:.3f} minPts={minPts}: {clusters} clusters, {outliers} outliers" + (" (PCA 2D)" if d > 2 else ""), fontsize=9)
plt.legend(); plt.tight_layout(); plt.savefig("clusterizacion.png", dpi=120)
print("Grafica guardada en clusterizacion.png"); plt.show()
