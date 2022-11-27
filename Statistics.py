import numpy as np
import pandas as pd
import time
import os
from deap import tools
from itertools import product
from scipy.stats import kstest

from EAController import EAController

class Statistics:
    
    def __init__(self, eac : EAController, configuration_image_path="img/ultima_cena.jpg"):
        self.eac = eac
        self.conf_img_path = configuration_image_path
        return

    def parametric_evaluation(self, n_seed=3):    
        results = {}

        # se setea la imagen que se va a utilizar para la configuracion
        self.eac.evolutionary_algorithm.image_processor.img_in_dir = self.conf_img_path
        self.eac.evolutionary_algorithm.load_image()

        p = {
            # le saque el 1 a CXPB me daba problema assert CXPB+MUTPB<=1
            "CXPB" : [0.8, 0.9],
            "MUTPB" : [0.01, 0.05, 0.1],
            "select_operator" : [
               [tools.selTournament, 3], [tools.selBest],  [tools.selStochasticUniversalSampling]
            ]
            # "CXPB" : [0.8, 0.9],
            # "MUTPB" : [0.1],
            # "select_operator" : [
            #     [tools.selBest]
            # ]
        }
        ortogonal_combinations = list(product(p["CXPB"], p["MUTPB"], p["select_operator"]))

        # cada configuracion parametrica
        for config in ortogonal_combinations:

                cxpb, mutpb, select_operator = config

                if len(select_operator) == 2:
                    self.eac.deap_configurer.__getattribute__("toolbox").register("select", select_operator[0], tournsize=select_operator[1])
                else:
                    self.eac.deap_configurer.__getattribute__("toolbox").register("select", select_operator[0])

                self.eac.deap_configurer.__setattr__("CXPB", cxpb)
                self.eac.deap_configurer.__setattr__("MUTPB", mutpb)

                comb_name = f"{cxpb}_{mutpb}_{select_operator[0].__name__}"
                results[comb_name] = {}

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
                results[comb_name]["best_historical_fitness"] = min(best_execution_fitness)
                results[comb_name]["avg_best_fitness"] = np.mean(best_execution_fitness)
                results[comb_name]["std_fitness"] = np.std(best_execution_fitness)

                pd.DataFrame(results).to_csv(f"results/resultados.csv")

        return

    # otras cosas posibles a agregar:
        # - el promedio del número de generaciones necesarias para alcanzar
        # el mejor resultado obtenido (eventualmente, debe presentarse la
        # desviación estándar del número de generaciones)?

    # Estadisticas Paralelismo
    def algorithmical_speedup(self):
        """
        Se define el speedup algorítmico como SN = T1 / TN, siendo:
            * T1 el tiempo de ejecución del algoritmo en forma serial
            * TN el tiempo del algoritmo paralelo ejecutado sobre N procesadores

        Se define la eficiencia computacional como EN = T1 / (N * TN )
            * N cantidad de procesadores
        

        """
        timestamps = {}

        for i in range(1,os.cpu_count()+1):
            self.eac.deap_configurer.__setattr__('cpu_count', i)
            start = time.time()
            self.eac.run()
            end = time.time()

            timestamps[i] = {}
            timestamps[i]["time"] = end - start
            timestamps[i]["speedup"] = timestamps[1]["time"] / timestamps[i]["time"]
            timestamps[i]["efficiency"] = timestamps[i]["speedup"] * (1/i)

        pd.DataFrame(timestamps).to_csv(f"results/time.csv")

        return 

    def normality_test(self, sample): 

        bnp = np.array(sample)
        bnp = bnp - bnp.mean()
        bnp = bnp / bnp.std()

        kstats = kstest(bnp, "norm", alternative='two-sided')