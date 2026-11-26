// Laboratorio 5: DBSCAN clasico y DBSCAN con KDTree
// Uso: g++ -O2 -std=c++17 -o dbscan dbscan.cpp
// dbscan.exe datos\moons_2d.csv 0.1 5 salida.csv
// El csv debe tener una fila de cabecera y solo columnas numericas.
#include <bits/stdc++.h>
using namespace std;
typedef vector<double> Punto;

// ---------- Utilidades ----------
double dist2(const Punto& a, const Punto& b) {
    double s = 0;
    for (size_t i = 0; i < a.size(); i++) { double d = a[i] - b[i]; s += d * d; }
    return s;
}

vector<Punto> leerCSV(const string& archivo) {
    ifstream f(archivo);
    string linea;
    vector<Punto> pts;
    getline(f, linea); // cabecera
    while (getline(f, linea)) {
        if (linea.empty()) continue;
        stringstream ss(linea);
        string celda;
        Punto p;
        while (getline(ss, celda, ',')) p.push_back(stod(celda));
        pts.push_back(p);
    }
    return pts;
}

// ---------- KDTree ----------
struct KDTree {
    struct Nodo { int idx; int izq = -1, der = -1; };
    const vector<Punto>& P;
    vector<Nodo> nodos;
    int raiz, k;

    KDTree(const vector<Punto>& pts) : P(pts) {
        k = pts[0].size();
        vector<int> ids(pts.size());
        iota(ids.begin(), ids.end(), 0);
        nodos.reserve(pts.size());
        raiz = construir(ids, 0, ids.size(), 0);
    }
    // Construye con la mediana en cada nivel: O(n log n)
    int construir(vector<int>& ids, int ini, int fin, int prof) {
        if (ini >= fin) return -1;
        int eje = prof % k, med = (ini + fin) / 2;
        nth_element(ids.begin() + ini, ids.begin() + med, ids.begin() + fin,
                    [&](int a, int b) { return P[a][eje] < P[b][eje]; });
        int id = nodos.size();
        nodos.push_back({ids[med]});
        int i = construir(ids, ini, med, prof + 1);
        int d = construir(ids, med + 1, fin, prof + 1);
        nodos[id].izq = i; nodos[id].der = d;
        return id;
    }
    // Consulta por rango: todos los puntos a distancia <= eps de q
    void rango(int n, const Punto& q, double eps, double eps2, int prof, vector<int>& res) const {
        if (n < 0) return;
        const Nodo& nd = nodos[n];
        if (dist2(P[nd.idx], q) <= eps2) res.push_back(nd.idx);
        int eje = prof % k;
        double diff = q[eje] - P[nd.idx][eje];
        if (diff - eps <= 0) rango(nd.izq, q, eps, eps2, prof + 1, res);
        if (diff + eps >= 0) rango(nd.der, q, eps, eps2, prof + 1, res);
    }
    vector<int> vecinos(int q, double eps) const {
        vector<int> res;
        rango(raiz, P[q], eps, eps * eps, 0, res);
        return res;
    }
};

// ---------- DBSCAN ----------
// Etiquetas: 0 = sin procesar, -1 = ruido, 1..K = cluster
// 'vecinosFn' devuelve los vecinos (incluido el propio punto) de un punto.
template <class F>
vector<int> dbscan(int n, int minPts, F vecinosFn) {
    vector<int> etiqueta(n, 0);
    int cluster = 0;
    for (int p = 0; p < n; p++) {
        if (etiqueta[p] != 0) continue;
        etiqueta[p] = -1;          // por defecto ruido
        cluster++;
        vector<int> porProcesar = {p};
        for (size_t i = 0; i < porProcesar.size(); i++) {
            int q = porProcesar[i];
            vector<int> vec = vecinosFn(q);
            if ((int)vec.size() < minPts) continue; // q no es punto core
            etiqueta[q] = cluster;
            for (int w : vec)
                if (etiqueta[w] <= 0) {            // no procesado o ruido
                    if (etiqueta[w] == 0) porProcesar.push_back(w);
                    etiqueta[w] = cluster;         // punto borde o core
                }
        }
        if (etiqueta[p] == -1) cluster--;          // p era ruido: no se gasta el indice
    }
    return etiqueta;
}

// Version clasica: busqueda lineal O(n) por consulta -> O(n^2)
vector<int> dbscanClasico(const vector<Punto>& P, double eps, int minPts) {
    double eps2 = eps * eps;
    return dbscan((int)P.size(), minPts, [&](int q) {
        vector<int> r;
        for (int i = 0; i < (int)P.size(); i++)
            if (dist2(P[q], P[i]) <= eps2) r.push_back(i);
        return r;
    });
}

// Version con KDTree: consulta O(log n) en promedio (baja dimension)
vector<int> dbscanKD(const vector<Punto>& P, double eps, int minPts, double& tConstruccion) {
    auto t0 = chrono::high_resolution_clock::now();
    KDTree kd(P);
    tConstruccion = chrono::duration<double>(chrono::high_resolution_clock::now() - t0).count();
    return dbscan((int)P.size(), minPts, [&](int q) { return kd.vecinos(q, eps); });
}

// ---------- Funcion pedida en la evaluacion ----------
int contarOutliers(const vector<int>& et) { return count(et.begin(), et.end(), -1); }
int contarClusters(const vector<int>& et) { return et.empty() ? 0 : max(0, *max_element(et.begin(), et.end())); }

int main(int argc, char** argv) {
    if (argc < 5) { cout << "Uso: g++ -O2 -std=c++17 -o dbscan dbscan.cpp"; cout<<" dbscan.exe datos\moons_2d.csv 0.1 5 salida.csv\n"; return 1; }
    vector<Punto> P = leerCSV(argv[1]);
    double eps = stod(argv[2]);
    int minPts = stoi(argv[3]);

    auto t0 = chrono::high_resolution_clock::now();
    vector<int> e1 = dbscanClasico(P, eps, minPts);
    double tClasico = chrono::duration<double>(chrono::high_resolution_clock::now() - t0).count();

    double tCons;
    t0 = chrono::high_resolution_clock::now();
    vector<int> e2 = dbscanKD(P, eps, minPts, tCons);
    double tKD = chrono::duration<double>(chrono::high_resolution_clock::now() - t0).count();

    bool iguales = (e1 == e2);
    cout << "n=" << P.size() << " dim=" << P[0].size() << " eps=" << eps << " minPts=" << minPts << "\n";
    cout << "clasico_s=" << tClasico << " kdtree_s=" << tKD << " (construccion=" << tCons << ")\n";
    cout << "clusters=" << contarClusters(e2) << " outliers=" << contarOutliers(e2)
         << " resultados_iguales=" << (iguales ? "si" : "no") << "\n";

    ofstream out(argv[4]);
    out << "etiqueta\n";
    for (int e : e2) out << e << "\n";
    return 0;
}
