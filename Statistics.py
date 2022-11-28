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

    def informal_evaluation(self, best_config, n_seed=30):
        p = {
            "MU" : [50, 100],
            "select_operator" : [
               [tools.selTournament, 3], [tools.selBest],  [tools.selRoulette]
            ]
        }
        return

    def greedy_evaluation(self, n_seed=30):
        return

    def parametric_evaluation(self, n_seed=30):    

        # se setea la imagen que se va a utilizar para la configuracion
        self.eac.evolutionary_algorithm.image_processor.img_in_dir = self.conf_img_path
        self.eac.evolutionary_algorithm.load_image()

        p = {
            "CXPB" : [0.8, 0.9],
            "MUTPB" : [0.01, 0.05, 0.1],
        }
        ortogonal_combinations = list(product(p["CXPB"], p["MUTPB"], p["select_operator"]))
        values = []

        # cada configuracion parametrica
        for cxpb, mutpb, select_operator in ortogonal_combinations:

            if len(select_operator) == 2:
                self.eac.deap_configurer.__getattribute__("toolbox").register("select", select_operator[0], tournsize=select_operator[1])
            else:
                self.eac.deap_configurer.__getattribute__("toolbox").register("select", select_operator[0])

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
                cxpb, mutpb, select_operator[0].__name__, min(best_execution_fitness), 
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                kstest(best_execution_fitness, "norm", alternative='two-sided').pvalue
            ])

        header = [
            "CXPB", "MUTPB", "select_operator", "best_historical_fitness", 
            "avg_best_fitness", "std_fitness", "p-value"
        ]
        pd.DataFrame(values, columns=header).to_csv(f"results/resultados.csv", index=False)
    
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
        values = []

        for i in range(1,os.cpu_count()+1):
            self.eac.deap_configurer.__setattr__('cpu_count', i)
            start = time.time()
            self.eac.run(show_res=False)
            end = time.time()

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

        bnp = np.array(sample)
        bnp = bnp - bnp.mean()
        bnp = bnp / bnp.std()

        kstats = kstest(bnp, "norm", alternative='two-sided')