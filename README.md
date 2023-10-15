# Image Approximation with Polygons using Delaunay Triangulation

# Features:

- Parametric configuration
- Comparison with other methods and result evaluation through statistical tests and visualization (due to the stochastic nature of the algorithm).
- Automated testing and graph generation with fixed seeds for result reproducibility.
- Multiprocessing
- Denoising and edge detection

# Libraries

Software built using the most popular libraries in the field of Data Science:

### Evolutionary Algorithms

- [DEAP] - Provides basic functionalities for instantiating evolutionary algorithm problems.
- [multiprocessing] - Parallelization in fitness calculation (master-slave architecture)

![DEAP](./readme/icons/DEAP.png)
![multiprocessing](./readme/icons/multiprocessing.png)
### Image Processing

- [OpenCV] - For denoising and edge detection algorithms.
- [PILLOW] - For dynamically generating and modifying images (genotype and phenotype of individuals).
- [NumPy] - Simplifies linear algebra operations using C code for increased efficiency.

![openCV](./readme/icons/openCV.png)
![PILLOW](./readme/icons/PILLOW.png)
![numpy](./readme/icons/numpy.png)

### Analysis of Results

- [SciPy] - Evaluation. Statistical tests with obtained results.
- [scikit_posthocs] - Results analysis with normal distribution using pairwise tests.
- [Pandas] - Data manipulation.
- [Matplotlib] - Data visualization.

![scipy](./readme/icons/scipy.png)
![scikit_posthocs](./readme/icons/scikit_posthocs.png)
![pandas](./readme/icons/pandas.png)
![matplotlib](./readme/icons/matplotlib.png)

# Results

![faces](./readme/results/extra_faces1.png)
![animals](./readme/results/extra_animals1.png)

# Data Source

All images where taken from https://www.pexels.com/es-es/

# Program Instructions

## Dependencies:
The libraries used in the project can be installed using the following command:

```
pip install -r ./requirements.txt
```

## Main modules:
Below are the execution scripts provided in this directory.

- main.py: This is the main program of the implemented algorithm. In it you can run the program with any desired configuration.

- alternative_solutions_main.py: This is the main program of the local-search and Gaussian mutation methods used as a baseline against the evolutionary algorithm.

- experiments_main.py: This is the main program used to execute the statistical tests reported in the article.

- analysis.ipynb: All the tests and evaluations shown in the report are performed here.

## Execution:

To run any of these three scripts, simply use the commands specified below.

- To obtain the complete description of the different flags, use:

```
python main.py -h
```

```
python alternative_solutions_main.py -h
```
In any case, when using a parameter in the wrong way, the main should report the error if it is in the input.

- An example of the execution of each algorithm is presented below:

```
python main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000
```

This will apply the algorithm to the image in the corresponding directory and name with a number of vertices equal to that included after --vertex_count.
Here the mandatory parameters are only the first two. The number of vertices is a parameter that is recommended to be used, although if not, a value is assigned according to the entropy of the image.

```
python alternative_solutions_main.py --input_name womhd.jpg --vertex_count 200 --method gaussian --threshold 100 --max_iter 1000 --max_evals 1000
```
This will apply the comparison algorithm in Gaussian mutation mode. It is possible to use the --method local_search or --method gaussian parameters to select the method to use. The --threshold parameter is the size of the local-search neighborhood and the standard deviation of the Gaussian mutation, while --max_iter is the maximum number of iterations to perform. --max_evals is the maximum number of fitness evaluations to perform.


It is recommended to use the --verbose 1 parameter to view the execution progress.

===========================================================================

To execute the statistical tests carried out, use the following command:

```
python experiments_main.py
```

Note: This could take hours or even days.

===========================================================================

Details that are not mentioned in the report:

There are parameters used for debugging which could be helpful:

```
python main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --show 1 --verbose 1
```

show and verbose allow you to view intermediately generated images and details about the execution.

```
python main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --manual_console 1
```

This flag creates a thread simultaneously with the algorithm that waits for an input and allows the execution to be canceled by writing "exit\n".

```
python main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --tri_outline black
```

This flag with the value of "black" or "white" gives an outline to the triangles used, allowing the distribution of triangles to be displayed more clearly. However, this directly affects the fitness calculation.

```
python main.py --input_path ./img --input_name imagen.jpg --vertex_count 5000 --width 500
```

Note: Specifying only the width or height size adjusts the other automatically.