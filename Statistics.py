import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

from itertools import product
from time import time
from scipy.stats import kstest
from scipy.stats import f_oneway
from os import cpu_count

from AltSolver import AltSolver
from EAController import EAController
from ImageProcessor import ImageProcessor
from DeapConfig import DeapConfig
from EA import EA

class Statistics:
    
    def __init__(self):
        return

    def efficiency_evaluation(self, images: dict, image_path: str, seed = 0):
        """
        Se define el speedup algorítmico como SN = T1 / TN, siendo:
            * T1 el tiempo de ejecución del algoritmo en forma serial
            * TN el tiempo del algoritmo paralelo ejecutado sobre N procesadores

        Se define la eficiencia computacional como EN = T1 / (N * TN )
            * N cantidad de procesadores
        """
        values = []
        random.seed(seed)
        for img in images:
            vertex_count = images[img].get("vertex_count", 100)
            eac = self.__build_eac(img, image_path, vertex_count, width=images[img].get("width", 500))
            for i in range(1,cpu_count()+1):
                print(f"Testing {img} with {i} CPUs")
                config = {"cpu_count": i}
                self.__update_config(eac, config)
                eac.deap_configurer.register_parallelism()
                start = time()
                eac.run(show_res=False)
                end = time()
                time_i = end - start
                time_1 = values[0][1] if i!=1 else time_i
                speedup = time_1 / time_i
                values.append([i, time_i, speedup, speedup * (1/i)])

        header = ["CPU", "time", "speedup", "efficiency"]
        df = pd.DataFrame(values, columns=header)
        df.to_csv(f"results/reports/test_time.csv", index=False)

        return 

    def normality_test(self, sample): 
        """
        Suppose we wish to test the null hypothesis,
            N0: the sample is distributed according to the standard normal. 
        We choose a confidence level of 95%; 
        1) If the p-value is less than our threshold (0.05), we reject the null hypothesis.
        2) If the p-value is greater than our threshold (0.05), we fail to reject the null hypothesis.
        """
        standarized_sample = (sample - np.mean(sample)) / np.std(sample, ddof=1)
        return kstest(standarized_sample, "norm", alternative='two-sided').pvalue

    def ANOVA_test(self, samples : list):
        """
        Null hypothesis: Groups means are equal (no variation in means of groups)
        H0: μ1 = μ2 = ... = μp
        Alternative hypothesis: At least, one group mean is different from other groups
        H1: All μ are not equal

        samples : should be a list of lists, where each list is a sample
        """
        return f_oneway(*samples).pvalue

    def __update_config(self, eac: EAController, config: dict):
        eac.deap_configurer = DeapConfig(**config)
        eac.build_deap_module()
        return

    def __build_eac(self, input_name: str, input_dir: str, vertex_count: int, width=500):
        dc = DeapConfig()
        ip = ImageProcessor(input_name=input_name, input_dir=input_dir, vertex_count=vertex_count, width=width)
        ea = EA(ip)
        eac = EAController(ea, dc)
        eac.build_ea_module()
        eac.build_deap_module()
        return eac

    def __get_EA_results(self, eac: EAController, seeds: list, config: dict, attributes: list, results: list, header_fitness: list, best_fitness_config: list):
            self.__update_config(eac, config)

            best_execution_fitness = []
            time_execution = []
            
            for seed in seeds:
                print(f"Evaluating seed {seed+1}/{len(seeds)} of config {config}")
                random.seed(seed)
                eac.deap_configurer.register_parallelism() # si no salta error de pool not running

                start = time()
                best_fitnesses = eac.run(show_res=False, logs=False, seed=seed)
                end = time()

                time_execution.append(end - start)
                best_execution_fitness.append(min(best_fitnesses))

            current_values = [eac.deap_configurer.__dict__[at] for at in attributes]

            results.append([
                *current_values, min(best_execution_fitness),
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                np.mean(time_execution),
                self.normality_test(best_execution_fitness)
            ])
        
            header_fitness.append(str(current_values))
            best_fitness_config.append(best_execution_fitness)

    def informal_evaluation(self, best_config : dict, vertex_count: int, attributes: dict, image_path: str, image_name: str,  seeds: list = [1,2,3,4]):
        eac = self.__build_eac(image_name, image_path, vertex_count)

        results = []
        header_fitness = []
        best_fitness_config = []

        for att, values in attributes.items():
            for val in values:
                current_config = {**best_config}
                current_config[att] = val
                self.__get_EA_results(eac, seeds, current_config, attributes, results, header_fitness, best_fitness_config)

        columns = [*(attributes.keys()), "best_historical_fitness", "avg_best_fitness", "std_fitness", "avg_time", "p-value"]
        pd.DataFrame(results, columns=columns).to_csv(f"results/informal.csv", index=False)
        pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/best_fit_per_config_informal.csv", index=False)

    def parametric_evaluation(self, vertex_count: int, attributes: dict, image_path: str, images: list=["ultima_cena.jpg"], seeds: list = [1,2,3,4]):
        eac = self.__build_eac(images[0], image_path, vertex_count)
        results = []
        header_fitness = []
        best_fitness_config = []
        
        ortogonal_combinations = list(product(*(attributes.values())))
        for combination in ortogonal_combinations:
            current_config = {}
            for i, att in enumerate(attributes.keys()):
                current_config[att] = combination[i]
            self.__get_EA_results(eac, seeds, current_config, attributes, results, 
                                  header_fitness, best_fitness_config)
        
        header = [*(attributes.keys()),"best_historical_fitness", "avg_best_fitness", "std_fitness", "avg_time", "p-value"]
        pd.DataFrame(results, columns=header).to_csv(f"results/resultados.csv", index=False)

        pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/best_fit_per_config_parametric.csv", index=False)
                
    def comparison_evaluation(self, best_config: dict, greedy_config: dict, image_path: str, images: dict, seeds: list = [1,2]):
        best_execution_fitness = []
        results = []
        header_fitness = []
        best_fitness_config = []
        EA_ID = "EA"

        for img in images:
            print(f"Evaluating image {img}")
            vertex_count = images[img].get("vertex_count", 100)
            eac = self.__build_eac(img, image_path, vertex_count, width=images[img].get("width", 500))
            self.__update_config(eac, best_config)
            alt_solver = AltSolver(eac.evolutionary_algorithm)

            for method in [EA_ID] + list(greedy_config.keys()):
                best_execution_fitness = []
                time_execution = []
                start = 0
                end = 0

                for seed in seeds:
                    print(f"Evaluating seed {seed+1}/{len(seeds)} of method {method}")
                    random.seed(seed)
                    if method == EA_ID:
                        eac.deap_configurer.register_parallelism() # si no salta error de pool not running
                        start = time()
                        best_fitnesses = eac.run(show_res=False, logs=False, seed=seed)
                        end = time()
                        best_execution_fitness.append(min(best_fitnesses))
                    else:
                        alt_solver.update_seed(seed)
                        start = time()
                        _, best_eval = alt_solver.solve(**(greedy_config[method]), method=method, verbose=False)
                        end = time()
                        best_execution_fitness.append(best_eval)
                        print(f"Best fitness: {best_eval}")
                    time_execution.append(end - start)
                
                results.append([
                    img,
                    method,
                    min(best_execution_fitness), 
                    np.mean(best_execution_fitness), np.std(best_execution_fitness),
                    np.mean(time_execution),
                    self.normality_test(best_execution_fitness)
                ])

                header_fitness.append(f"{method}-{img}")
                best_fitness_config.append(best_execution_fitness)

                header = ["image", "method", "best_historical_fitness", "avg_best_fitness", "std_fitness", "avg_time", "p-value"]
                pd.DataFrame(results, columns=header).to_csv(f"results/comparison.csv", index=False)
                pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/best_fit_per_config_greedy.csv", index=False)

    def plot_best_historical_fitness(self):
        df = pd.read_csv("results/comparison.csv")
        df_pivot = df.pivot(index='image', columns='method', values='best_historical_fitness')
        df_pivot = df_pivot.apply(lambda x: x/x.max(), axis=1)
        df_pivot.plot.bar(rot=0)
        plt.savefig("results/plots/best_historical_fitness.png", format="png")
        plt.show()

    def plot_time(self):
        df = pd.read_csv("results/reports/test_time.csv")
        df_with_images = pd.DataFrame(columns=["CPU", "time", "image"])
        for idx, image in enumerate(["fox.jpg", "monalisa_sqr.jpg", "old_man.jpeg"]):
            row = df.iloc[4*idx:4*idx+4]
            df2 = pd.DataFrame({"CPU": row["CPU"], "time": row["time"], "image": image})
            df_with_images = pd.concat([df_with_images, df2], axis=0)

        df_pivot = df_with_images.pivot(index='CPU', columns='image', values='time')

        df_pivot.plot.bar()
        plt.savefig("results/plots/time.png", format="png")
        plt.show()