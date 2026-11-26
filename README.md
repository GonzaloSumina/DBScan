# Laboratorio 5: DBSCAN + KDTree (EDA, UCSP)

Implementación en C++ de DBSCAN clásico y DBSCAN con KDTree, con scripts en Python para
los experimentos, las gráficas y el Silhouette Score.

## Contenido

| Archivo | Para qué sirve |
|---|---|
| `dbscan.cpp` | DBSCAN clásico y con KDTree (C++17). Imprime tiempos, clusters y outliers |
| `gen_datos.py` | Genera los datasets `datos/moons_2d.csv` (2D) y `datos/blobs_6d.csv` (6D) |
| `analisis.py` | Corre todos los experimentos y guarda gráficas y tablas en `resultados/` |
| `evaluar.py` | Script para un CSV nuevo: outliers, clusters, silueta, tiempos y gráfica |
| `informe.tex` | Informe en LaTeX (usa las imágenes de `resultados/`) |

## Requisitos

- Compilador C++ con soporte C++17 (g++ 9 o superior).
- Python 3.9 o superior, **versión normal** (no la variante "free-threaded" `python3.13t`).
- Librerías de Python: `numpy`, `pandas`, `scikit-learn`, `matplotlib`.
- Para compilar el informe: una distribución de LaTeX con el paquete de español (TeX Live completo o MiKTeX).

## Instalación

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install numpy pandas scikit-learn matplotlib
g++ -O2 -std=c++17 -o dbscan dbscan.cpp
```

### Windows
1. Instala g++ con [MSYS2](https://www.msys2.org) (terminal "MSYS2 UCRT64"):
   ```
   pacman -S mingw-w64-ucrt-x86_64-gcc
   ```
2. Compila desde esa misma terminal, dentro de la carpeta del proyecto:
   ```
   g++ -O2 -std=c++17 -o dbscan dbscan.cpp
   ```
   Esto crea `dbscan.exe`. Si prefieres Visual Studio, reemplaza `#include <bits/stdc++.h>` por los
   includes estándar (`iostream`, `fstream`, `sstream`, `vector`, `string`, `algorithm`, `numeric`, `chrono`).
3. En el CMD, dentro de la carpeta del proyecto:
   ```
   py -3.13 -m venv venv
   venv\Scripts\activate
   pip install numpy pandas scikit-learn matplotlib
   ```
   (usa la versión de Python que tengas instalada en lugar de `3.13`).

## Uso

### 1. DBSCAN desde C++
```
./dbscan datos/moons_2d.csv 0.1 5 salida.csv
```
En Windows (CMD): `dbscan.exe datos\moons_2d.csv 0.1 5 salida.csv`

Argumentos: `archivo.csv eps minPts archivo_de_salida.csv`. El CSV debe tener una fila de cabecera
y solo columnas numéricas.

Imprime: tamaño y dimensión de los datos, tiempo del clásico y del KDTree, número de clusters,
número de outliers y si ambas versiones dieron el mismo resultado. En el archivo de salida,
cada fila es la etiqueta de un punto (`-1` = outlier, `1..K` = cluster).

### 2. Experimentos completos
```
python gen_datos.py      # solo si no existen los CSV de datos/
python analisis.py
```
Tarda un par de minutos (incluye pruebas con hasta 40 000 puntos). Genera en `resultados/`:
`clusters_*.png`, `tiempo_vs_n.png`, `tiempo_vs_dim.png`, `kdistance.png` y las tablas `.csv`.
El script elige solo entre `./dbscan` y `dbscan.exe` según el sistema.

### 3. Evaluar un dataset nuevo
```
python evaluar.py archivo.csv              # eps sugerido automáticamente
python evaluar.py archivo.csv 0.5 10       # eps y minPts a mano
```
Acepta CSV con o sin cabecera, separador `,` o `;`, cualquier dimensión (>= 2) y columnas no
numéricas (se ignoran). Estandariza los datos, imprime outliers, clusters, Silhouette Score
(sin contar outliers) y tiempos, y guarda la gráfica en `clusterizacion.png` (con PCA si hay más
de 2 dimensiones). Necesita que `dbscan` / `dbscan.exe` esté compilado en la misma carpeta.

El `eps` sugerido es solo un punto de partida; si la gráfica no se ve bien, prueba valores
cercanos a mano.

### 4. Compilar el informe
```
pdflatex informe.tex
pdflatex informe.tex
```
(dos veces, para que las referencias se resuelvan). La carpeta `resultados/` debe estar junto al `.tex`.

## Usar otro dataset desde otro computador

`dbscan.exe` no está en GitHub (está en el `.gitignore`), así que en una máquina nueva hay que clonar el repositorio y compilar de nuevo.

1. Clona el repositorio:
   ```
   git clone https://github.com/GonzaloSumina/DBScan.git
   cd DBScan
   ```
2. Instala y compila siguiendo la sección **Instalación** de arriba (Python normal con entorno virtual, librerías con `pip` y `g++ -O2 -std=c++17 -o dbscan dbscan.cpp`).
3. Copia tu CSV a la carpeta `datos/` y ejecuta:
   ```
   python evaluar.py datos/nuevo.csv
   ```
   o con tus parámetros:
   ```
   python evaluar.py datos/nuevo.csv 0.5 10
   ```
   Sirve para cualquier CSV con 2 o más dimensiones. Imprime outliers, clusters, silueta y tiempos, y guarda `clusterizacion.png`.

### Repetir todos los experimentos con tu dataset

Edita `analisis.py` y cambia el diccionario `config`: el nombre, la ruta del CSV y la lista de pares `(eps, minPts)` que quieras probar.

```python
config = {
    "mi_dataset": ("datos/nuevo.csv", [(0.3, 10), (0.5, 10), (0.8, 10), (0.5, 30)]),
}
```

Para elegir esos valores, corre primero `evaluar.py` y usa el `eps` sugerido como referencia. Los experimentos de tiempo con datos sintéticos se generan solos y no dependen de tu dataset.

### Requisitos del CSV
- Con `evaluar.py`: cabecera opcional, separador `,` o `;`, y las columnas de texto se ignoran.
- Con `dbscan` / `dbscan.exe` directamente: una fila de cabecera y solo columnas numéricas.

### Subir los cambios desde esa máquina
```
git add .
git commit -m "Descripción del cambio"
git push
```
GitHub pedirá iniciar sesión la primera vez. Si sigues trabajando en otra máquina, ejecuta `git pull` antes de modificar archivos para evitar conflictos.

## Problemas frecuentes

- **`"." no se reconoce como comando`** (Windows): en el CMD no uses `./`; escribe `dbscan.exe`.
- **Error al importar numpy** con `python3.13t.exe`: tienes la variante free-threaded; instala la versión normal de Python.
- **`g++` no se reconoce**: usa la terminal "MSYS2 UCRT64" o agrega `C:\msys64\ucrt64\bin` al PATH.
- **Error de babel/spanish al compilar el informe**: instala el paquete de idioma español de tu distribución LaTeX.