import numpy as np
import pandas as pd

from deap import tools
from time import time
from itertools import product
from scipy.stats import kstest
from os import cpu_count
import random

from AltSolver import AltSolver
from EAController import EAController
from ImageProcessor import ImageProcessor
from DeapConfig import DeapConfig
from EA import EA

class Statistics:
    
    def __init__(self, eac : EAController, altsol : AltSolver):
        self.eac = eac
        self.alt_solver = altsol
        return

    def informal_evaluation(self, best_config : dict, n_seed : int = 3, configuration_image_path : str = "img/ultima_cena.jpg"):
        # setear mejor configuracion hallada
        self.eac.deap_configurer.__setattr__("CXPB", best_config["CXPB"])
        self.eac.deap_configurer.__setattr__("MUTPB", best_config["MUTPB"])
        
        p = {
            "MU" : [50, 100],
            "select_operator" : [
               [tools.selTournament, 3], [tools.selBest],  [tools.selRoulette]
            ]
        }
        ortogonal_combinations = list(product(p["MU"], p["select_operator"]))

        # se setea la imagen que se va a utilizar para la configuracion
        self.eac.evolutionary_algorithm.image_processor.img_in_dir = configuration_image_path
        self.eac.evolutionary_algorithm.load_image()

        values = []

        # cada configuracion parametrica
        for mu, select_operator in ortogonal_combinations:

            if len(select_operator) == 2:
                self.eac.deap_configurer.__getattribute__("toolbox").register("select", select_operator[0], tournsize=select_operator[1])
            else:
                self.eac.deap_configurer.__getattribute__("toolbox").register("select", select_operator[0])
            self.eac.deap_configurer.__setattr__("MU", mu)

            best_execution_fitness = []

            # para cada seed
            for s in range(1, n_seed):
                # ejecutar el algoritmo
                self.eac.deap_configurer.__setattr__('seed', s)
                # si no salta error de pool not running
                self.eac.deap_configurer.register_parallelism()
                # devuelve lista de min fitness en cada generacion
                best_fitness_per_gen = self.eac.run(show_res=False)
                # se guarda el min fitness de una ejecucion. ejecucion = conf_alg + seed
                best_execution_fitness.append(min(best_fitness_per_gen))

            # se guardan los valores obtenidos para la configuracion
            values.append([
                mu, select_operator[0].__name__, min(best_execution_fitness), 
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                self.normality_test(best_execution_fitness)
            ])

        header = [
            "MU", "select_operator", "best_historical_fitness", 
            "avg_best_fitness", "std_fitness", "p-value"
        ]
        pd.DataFrame(values, columns=header).to_csv(f"results/informal.csv", index=False)
    
        return

    def greedy_evaluation(self, instance="img/ultima_cena.jpg", n_seed=3):
        """
        van a tener que ejecutarla entre 20 y 30 veces por instancia y van a tener que reportar valores promedio y desviación estándar del mejor valor hallado de la función objetivo que sería la función de fitness.
        """
        # se setea la imagen sobre la cual se va a evaluar
        self.alt_solver.ea.image_processor.img_in_dir = instance
        self.alt_solver.ea.load_image()

        values = []
        best_execution_fitness = []

        max_iter = 10 #1000
        vertex_count = 200
        threshold = 100
        
        for method in ["local_search", "gaussian"]:
            for s in range(1, n_seed):
                # setear la seed del pseudo greedy
                self.alt_solver.update_seed(s)

                best_individual, best_eval = self.alt_solver.solve(method, max_iter, vertex_count, threshold, verbose=True)

                best_execution_fitness.append(best_eval.min())

            # se guardan los valores obtenidos para la configuracion
            values.append([
                method,
                min(best_execution_fitness), 
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                kstest(best_execution_fitness, "norm", alternative='two-sided').pvalue
            ])

        header = [
            "method", "best_historical_fitness", "avg_best_fitness", "std_fitness", "p-value"
        ]
        pd.DataFrame(values, columns=header).to_csv(f"results/greedy.csv", index=False)

        return

    def parametric_evaluation(self, n_seed=30, configuration_image_path="img/ultima_cena.jpg"):    

        # se setea la imagen que se va a utilizar para la configuracion
        self.eac.evolutionary_algorithm.image_processor.img_in_dir = configuration_image_path
        self.eac.evolutionary_algorithm.load_image()

        p = {
            "CXPB" : [0.8, 0.9],
            "MUTPB" : [0.01, 0.05, 0.1],
        }
        ortogonal_combinations = list(product(p["CXPB"], p["MUTPB"]))
        values = []

        # cada configuracion parametrica
        for cxpb, mutpb in ortogonal_combinations:

            self.eac.deap_configurer.__setattr__("CXPB", cxpb)
            self.eac.deap_configurer.__setattr__("MUTPB", mutpb)


            best_execution_fitness = []

            # para cada seed
            for s in range(1, n_seed):
                # ejecutar el algoritmo
                self.eac.deap_configurer.__setattr__('seed', s)

                # si no salta error de pool not running
                self.eac.deap_configurer.register_parallelism()

                # devuelve lista de min fitness en cada generacion
                best_fitness_per_gen = self.eac.run(show_res=False)

                # se guarda el min fitness de una ejecucion. ejecucion = conf_alg + seed
                best_execution_fitness.append(min(best_fitness_per_gen))

            # se guardan los valores obtenidos para la configuracion
            values.append([
                cxpb, mutpb, min(best_execution_fitness), 
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                self.normality_test(best_execution_fitness)
            ])

        header = [
            "CXPB", "MUTPB", "best_historical_fitness", 
            "avg_best_fitness", "std_fitness", "p-value"
        ]
        pd.DataFrame(values, columns=header).to_csv(f"results/resultados.csv", index=False)
    
        return

    # Estadisticas Paralelismo
    def algorithmical_speedup(self):
        """
        Se define el speedup algorítmico como SN = T1 / TN, siendo:
            * T1 el tiempo de ejecución del algoritmo en forma serial
            * TN el tiempo del algoritmo paralelo ejecutado sobre N procesadores

        Se define la eficiencia computacional como EN = T1 / (N * TN )
            * N cantidad de procesadores
        """
        values = []

        for i in range(1,cpu_count()+1):
            self.eac.deap_configurer.__setattr__('cpu_count', i)
            start = time()
            self.eac.run(show_res=False)
            end = time()

            time_i = end - start
            time_1 = values[0][1] if i!=1 else time_i
            speedup = time_1 / time_i

            values.append([i, time_i, speedup, speedup * (1/i)])

        header = ["CPU", "time", "speedup", "efficiency"]
        pd.DataFrame(values, columns=header).to_csv(f"results/time.csv", index=False)

        return 

    def normality_test(self, sample): 
        """
        Suppose we wish to test the null hypothesis,
            N0: the sample is distributed according to the standard normal. 
        We choose a confidence level of 95%; 
        1) If the p-value is less than our threshold (0.05), we reject the null hypothesis.
        2) If the p-value is greater than our threshold (0.05), we fail to reject the null hypothesis.
        """
        return kstest(sample, "norm", alternative='two-sided').pvalue

#TODO 
# modularizar las evaluaciones: la estructura se repite
# hacer el stats_main.py para las llamadas al modulo Statistics
# hacer una run_all que ejecute todas las evaluaciones en el orden correcto
# graficos?

    def __update_config(self, eac: EAController, config: dict):
        eac.deap_configurer = DeapConfig(**config)
        eac.build_deap_module()
        return

    def __build_eac(self, input_name: str, input_dir: str, vertex_count: int):
        dc = DeapConfig()
        ip = ImageProcessor(input_name=input_name, input_dir=input_dir, vertex_count=vertex_count)
        ea = EA(ip)
        eac = EAController(ea, dc)
        eac.build_ea_module()
        eac.build_deap_module()
        return eac

    def __get_EA_results(self, eac: EAController, seeds: list, config: dict, attributes: list, results: list):
            self.__update_config(eac, config)
            best_execution_fitness = []
            for seed in seeds:
                random.seed(seed)
                eac.deap_configurer.register_parallelism() # si no salta error de pool not running
                best_fitnesses = eac.run(show_res=False, logs=False, seed=seed)
                best_execution_fitness.append(min(best_fitnesses))
                current_values = [eac.deap_configurer.__dict__[at] for at in attributes]
                results.append([
                    *current_values, seed, min(best_fitnesses),
                    np.mean(best_execution_fitness), np.std(best_execution_fitness),
                    self.normality_test(best_execution_fitness)
                ])

    def informal_evaluation_2(self, best_config : dict, vertex_count: int, attributes: dict, image_path: str, image_name: str,  seeds: list = [1,2]):
        eac = self.__build_eac(image_name, image_path, vertex_count)

        results = []
        for att, values in attributes.items():
            for val in values:
                current_config = {**best_config}
                current_config[att] = val
                self.__get_EA_results(eac, seeds, current_config, attributes, results)
        columns = [*(attributes.keys()), "seed", "best_historical_fitness", "avg_best_fitness", "std_fitness", "p-value"]
        pd.DataFrame(results, columns=columns).to_csv(f"results/informal.csv", index=False)

    def parametric_evaluation2(self, vertex_count: int, attributes: dict, image_path: str, image_name: str, seeds: list = [1,2]):
        eac = self.__build_eac(image_name, image_path, vertex_count)
        #TODO: PASAR LISTA DE IMAGENES POR PARAMETRO Y NO UNA SOLA
        results = []
        ortogonal_combinations = list(product(*(attributes.values())))
        for combination in ortogonal_combinations:
            current_config = {}
            for i, att in enumerate(attributes.keys()):
                current_config[att] = combination[i]
            self.__get_EA_results(eac, seeds, current_config, attributes, results)
        header = [*(attributes.keys()), "seed","best_historical_fitness", "avg_best_fitness", "std_fitness", "p-value"]
        pd.DataFrame(results, columns=header).to_csv(f"results/resultados.csv", index=False)
                
    def greedy_evaluation_2(self, best_config: dict, greedy_config: dict, vertex_count: int, image_path: str, image_name: str, seeds: list = [1,2]):
        eac = self.__build_eac(image_name, image_path, vertex_count)
        self.__update_config(eac, best_config)
        alt_solver = AltSolver(eac.evolutionary_algorithm)

        best_execution_fitness = []
        results = []
        EA_ID = "EA"

        for method in list(greedy_config.keys()) + [EA_ID]:
            for seed in seeds:
                if method == EA_ID:
                    random.seed(seed)
                    eac.deap_configurer.register_parallelism() # si no salta error de pool not running
                    best_fitnesses = eac.run(show_res=False, logs=False, seed=seed)
                    best_execution_fitness.append(min(best_fitnesses))
                else:
                    alt_solver.update_seed(seed)
                    _, best_eval = alt_solver.solve(**(greedy_config[method]), vertex_count=vertex_count, method=method, verbose=True)
                    best_execution_fitness.append(best_eval.min())

            results.append([
                method,
                min(best_execution_fitness), 
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                kstest(best_execution_fitness, "norm", alternative='two-sided').pvalue
            ])

        header = ["method", "best_historical_fitness", "avg_best_fitness", "std_fitness", "p-value"]
        pd.DataFrame(results, columns=header).to_csv(f"results/greedy.csv", index=False)