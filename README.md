Integrantes:
 *      Guido Dinello
 *      Alexis Baladón

===========================================================================

### Programas principales:
A continuación se presentan los scripts de ejecución proveídos en este directorio.

- main.py: Este es el programa principal del algoritmo implementado. En él se podrá ejecutar el programa con cualquier configuración deseada.

- alt_main.py, Es el programa principal de los métodos local-search y de mutación gaussiana utilizados como línea base contra el algoritmo evolutivo.

- stats_main.py, Es el programa principal utilizado para ejecutar los tests estadísticos reportados en el informe final.

### Ejecución:

Para ejecutar cualquiera de estos tres scripts basta con utilizar los comandos especificados a continuación utilizando el comando py o python3 dependiendo del sistema operativo en uso.

- Para obtener la descripción completa de las distintas flags utilizar:

```
py main.py -h
```

```
py alt_main.py -h
```

De todas formas, al utilizar un parámetro de forma equivocada el main debería informar el error en caso de ser en la entrada.

- Un ejemplo de ejecución de cada algoritmo es presentado a continuación:

```
py main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000
```

Esto aplicará el algoritmo a la imagen en el directorio y nombre correspondientes con una cantidad de vértices igual a la incluida luego de --vertex_count.
Aquí los parámetros obligatorios son solo los primeros dos. El número de vértices es un parámetro que se recomienda usar, aunque en caso de no hacerlo se asigna un valor según la entropía de la imagen.

```
py alt_main.py --input_name womhd.jpg --vertex_count 200 --method gaussian --threshold 100 --max_iter 1000 --max_evals 1000
```

Esto aplicará el algoritmo de comparación en modalidad de mutación gaussiana. Es posible utilizar los parámetros --method local_search o --method gaussian para seleccionar el método a utilizar. El parámetro --threshold es el tamaño de la vecindad del local-search y la desviación estándar de la mutación gaussiana, mientras que --max_iter es la cantidad máxima de iteraciones a realizar. --max_evals es la cantidad máxima de evaluaciones de fitness a realizar.


Se recomienda utilizar el parámetro --verbose 1 para ver el progreso de la ejecución.

===========================================================================

Para ejecutar los tests estadísticos realizados debe realizarse:

```
py stats_main.py -h
```

Esto podría tardar horas o incluso días.

===========================================================================

Detalles que no son mencionados en informe:

Existen parámetros utilizados para depuración los cuales podrían ser de ayuda:

```
py main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --show 1 --verbose 1
```

show y verbose permiten visualizar imagenes generadas de forma intermédia y detalles sobre la ejecución.

```
py main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --manual_console 1
```

Esta flag crea un hilo en simultáneo al algoritmo que espera por una entrada y permite cancelar la ejecución escribiendo "exit\n".

```
py main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --tri_outline black
```

Esta flag con el valor de "black" o "white" le da contorno a los triángulos utilizados, permitiendo visualizar la distribución de triángulos con mayor claridad. Sin embargo, esto afecta directamente al cálculo del fitness.

```
py main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --width 500
```

Especificar solo el tamaño del ancho o alto ajusta la otra automáticamente.

### Detalles de implementación:

Para el algoritmo evolutivo son utilizados los siguientes archivos:

- main.py: Es el programa principal del algoritmo evolutivo. En él se podrá ejecutar el programa con cualquier configuración deseada.
- EAController.py: Contiene la clase EAController, la cual es la encargada de controlar el algoritmo evolutivo.
- DeapConfig.py: Encapsula todo operador o clase utilizada de la librería DEAP.
- EA.py: Contiene toda la lógica específica al algoritmo evolutivo y al problema en cuestión.
- ImageProcessor.py: Contiene toda la lógica de procesamiento de imágenes, incluyendo la creación de imágenes polinómicas, la detección de bordes y el denoising.

Para los métodos de resolución alternativos son utilizados los siguientes archivos:

- alt_main.py: Es el programa principal de los métodos local-search y de mutación gaussiana utilizados como línea base contra el algoritmo evolutivo.
- AltSolver.py: Contiene la clase AltSolver, la cual es la encargada de controlar los métodos de resolución alternativos.

Para los tests estadísticos son utilizados los siguientes archivos:
- stats_main.py: Es el programa principal de los tests estadísticos.
- Statistics.py: Contiene la clase Statistics, en la cual son implementados los tests estadísticos (configuración formal e informal, comparación y medición de eficiencia computacional).