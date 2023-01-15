# Aproximación de imágenes con polígonos mediante triangulación de Delaunay


![gif](./readme/results/girl.gif)

# Librerías

Son utilizadas las librerías más populares dentro de la ciencia de datos:

### Algoritmos evolutivos

- [DEAP] - Provee funcionalidades base para instanciar problemas de algoritmos evolutivos.
- [multiprocessing] - Paralelización en cálculo de fitness (Arquitectura master-slave)

![DEAP](./readme/icons/DEAP.png)
![multiprocessing](./readme/icons/multiprocessing.png)
### Manipulación de imágenes

- [openCV] - Para algoritmos de denoising y detección de bordes.
- [PILLOW] - Para generar y modificar imágenes de forma dinámica (genotipo y fenotipo de individuos).
- [numpy] - Simplifica operaciones de álgebra lineal utilizando código de C para aumentar su eficiencia.

![openCV](./readme/icons/openCV.png)
![PILLOW](./readme/icons/PILLOW.png)
![numpy](./readme/icons/numpy.png)

### Análisis de resultados
- [scipy] - Evaluación. Pruebas estadísticas con resultados obtenidas.
- [scikit_posthocs] - Análisis de resultados con distribución normal mediante pruebas de pares.
- [pandas] - Manipulación de datos.
- [matplotlib] - Visualización de datos.
- [jupyter] - Generación de gráficas y análisis de resultados.

![scipy](./readme/icons/scipy.png)
![scikit_posthocs](./readme/icons/scikit_posthocs.png)
![pandas](./readme/icons/pandas.png)
![matplotlib](./readme/icons/matplotlib.png)

# Resultados

![faces](./readme/results/extra_faces1.png)
![animals](./readme/results/extra_animals1.png)

# Características:
- Configuración paramétrica
- Comparación con otros métodos y evaluación de resultados mediante pruebas estadísticas y visualización (dado que el algoritmo estocástico).
- Pruebas y generación de gráficas automatizadas con semillas fijadas para reproducir resultados.
- Multiprocesamiento
- Denoising y detección de bordes