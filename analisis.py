# Ejecuta el C++, grafica, calcula Silhouette y arma las tablas del informe
import subprocess, re, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.datasets import make_blobs, make_moons
from sklearn.preprocessing import StandardScaler

def correr(csv, eps, mp, salida="resultados/tmp.csv"):
    txt = subprocess.run(["dbscan.exe", csv, str(eps), str(mp), salida], capture_output=True, text=True).stdout
    tc, tk = map(float, re.findall(r"clasico_s=([\d.e-]+) kdtree_s=([\d.e-]+)", txt)[0])
    cl, out = map(int, re.findall(r"clusters=(\d+) outliers=(\d+)", txt)[0])
    ok = "resultados_iguales=si" in txt
    return tc, tk, cl, out, ok, pd.read_csv(salida)["etiqueta"].values

def silueta(X, et):
    m = et != -1   # se evalua sin el ruido
    if len(set(et[m])) < 2: return float("nan")
    return silhouette_score(X[m], et[m])

res = {}
# 1: hiperparametros en cada dataset
config = {
    "moons_2d": ("datos/moons_2d.csv", [(0.05, 5), (0.1, 5), (0.2, 5), (0.1, 30)]),
    "blobs_6d": ("datos/blobs_6d.csv", [(0.3, 10), (0.6, 10), (1.0, 10), (0.6, 40)]),
}
filas = []
for nombre, (csv, params) in config.items():
    X = pd.read_csv(csv).values
    X2 = X if X.shape[1] == 2 else PCA(2).fit_transform(X)
    fig, ax = plt.subplots(1, len(params), figsize=(4 * len(params), 3.8))
    for a, (eps, mp) in zip(ax, params):
        tc, tk, cl, out, ok, et = correr(csv, eps, mp)
        s = silueta(X, et)
        filas.append([nombre, eps, mp, cl, out, round(s, 3), round(tc, 4), round(tk, 4), round(tc / tk, 1), "si" if ok else "no"])
        m = et == -1
        a.scatter(X2[~m, 0], X2[~m, 1], c=et[~m], s=4, cmap="tab10")
        a.scatter(X2[m, 0], X2[m, 1], c="k", s=6, marker="x")
        a.set_title(f"eps={eps}, minPts={mp}\n{cl} clusters, {out} outliers", fontsize=9)
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle(nombre + (" (PCA a 2D)" if X.shape[1] > 2 else ""))
    plt.tight_layout(); plt.savefig(f"resultados/clusters_{nombre}.png", dpi=110); plt.close()
tabla1 = pd.DataFrame(filas, columns=["dataset", "eps", "minPts", "clusters", "outliers", "silhouette", "t_clasico(s)", "t_kdtree(s)", "speedup", "iguales"])
tabla1.to_csv("resultados/tabla_hiperparametros.csv", index=False)

# 2: tiempo vs tamano n (2D)
Xf, _ = make_moons(n_samples=40000, noise=0.07, random_state=1)
Xf = StandardScaler().fit_transform(Xf)
filas = []
for n in [2000, 5000, 10000, 20000, 40000]:
    pd.DataFrame(Xf[:n], columns=["x1", "x2"]).to_csv("datos/tmp.csv", index=False)
    tc, tk, *_ = correr("datos/tmp.csv", 0.1, 5)
    filas.append([n, tc, tk])
t2 = pd.DataFrame(filas, columns=["n", "clasico", "kdtree"])
plt.figure(figsize=(5, 3.6))
plt.plot(t2.n, t2.clasico, "o-", label="Clasico O(n^2)"); plt.plot(t2.n, t2.kdtree, "s-", label="KDTree")
plt.xlabel("n puntos"); plt.ylabel("tiempo (s)"); plt.legend(); plt.title("Tiempo vs n (2D)"); plt.tight_layout()
plt.savefig("resultados/tiempo_vs_n.png", dpi=110); plt.close()
t2.round(4).to_csv("resultados/tabla_tiempo_n.csv", index=False)

# 3: tiempo vs dimension (n=4000)
filas = []
for d in [2, 4, 8, 16, 32]:
    X, _ = make_blobs(n_samples=4000, n_features=d, centers=4, random_state=0)
    X = StandardScaler().fit_transform(X)
    pd.DataFrame(X, columns=[f"x{i}" for i in range(d)]).to_csv("datos/tmp.csv", index=False)
    eps = 0.3 * np.sqrt(d)
    tc, tk, *_ = correr("datos/tmp.csv", round(eps, 3), 10)
    filas.append([d, tc, tk])
t3 = pd.DataFrame(filas, columns=["d", "clasico", "kdtree"])
plt.figure(figsize=(5, 3.6))
plt.plot(t3.d, t3.clasico, "o-", label="Clasico"); plt.plot(t3.d, t3.kdtree, "s-", label="KDTree")
plt.xlabel("dimension"); plt.ylabel("tiempo (s)"); plt.legend(); plt.title("Tiempo vs dimension (n=4000)"); plt.tight_layout()
plt.savefig("resultados/tiempo_vs_dim.png", dpi=110); plt.close()
t3.round(4).to_csv("resultados/tabla_tiempo_dim.csv", index=False)

# Grafico k-distance (para elegir eps)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
for a, (nombre, k) in zip(ax, [("moons_2d", 5), ("blobs_6d", 10)]):
    X = pd.read_csv(config[nombre][0]).values
    d, _ = NearestNeighbors(n_neighbors=k).fit(X).kneighbors(X)
    a.plot(np.sort(d[:, -1])); a.set_title(f"{nombre}: distancia al vecino {k}"); a.set_xlabel("puntos ordenados"); a.set_ylabel("distancia")
plt.tight_layout(); plt.savefig("resultados/kdistance.png", dpi=110); plt.close()
print(tabla1.to_string()); print(t2.round(4)); print(t3.round(4))
