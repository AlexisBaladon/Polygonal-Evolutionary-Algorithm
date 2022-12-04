import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

from deap import tools
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
    
    def __init__(self, eac : EAController, altsol : AltSolver):
        self.eac = eac
        self.alt_solver = altsol
        return

    def greedy_evaluation(self, 
        greedy_config={
            "max_iter": 10,#100,
            "vertex_count": 10,#1000,
            "threshold": 100
        }, 
        instances=["img/ultima_cena.jpg", "img/Bart.jpg", "img/monalisa.jpg"], 
        seeds: "list[int]"=[i for i in range(30)]):
        """
        van a tener que ejecutarla entre 20 y 30 veces por instancia y van a tener que reportar valores promedio y desviación estándar del mejor valor hallado de la función objetivo que sería la función de fitness.
        """


        for instance in instances: 

            # se setea la imagen sobre la cual se va a evaluar
            self.alt_solver.ea.image_processor.img_in_dir = instance
            self.alt_solver.ea.load_image()

            values = []

            header_fitness = []
            best_fitness_config = []

            for method in ["local_search", "gaussian"]:

                best_execution_fitness = []
                time_execution = []

                for s in seeds:
                    # setear la seed del pseudo greedy
                    self.alt_solver.update_seed(s)

                    start = time()
                    best_individual, best_eval = self.alt_solver.solve(method, **greedy_config, verbose=True)
                    end = time()

                    best_execution_fitness.append(best_eval.min())
                    time_execution.append(end - start)

                # se guardan los valores obtenidos para la configuracion
                values.append([
                    instance,
                    method,
                    min(best_execution_fitness), 
                    np.mean(best_execution_fitness), np.std(best_execution_fitness),
                    np.mean(time_execution),
                    self.normality_test(best_execution_fitness)
                ])

                header_fitness.append(method)
                best_fitness_config.append(best_execution_fitness)

        header = [
            "instance", "method", "best_historical_fitness", "avg_best_fitness", "std_fitness", "avg_time", "p-value"
        ]
        pd.DataFrame(values, columns=header).to_csv(f"results/reports/test_greedy.csv", index=False)
        
        pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/greedy.csv", index=False)

        return

    def informal_evaluation(self):
        self.evaluate_ae(
            self.eac.run,
            {
                "MU" : [50, 100],
                "select_operator" : [
                    [tools.selTournament, {"tournsize":3}], [tools.selBest, {}],  [tools.selRoulette, {}]
                ]
            },
            out_name="test_informal"
        )

    def parametric_evaluation(self):
        self.evaluate_ae(
            self.eac.run,
            {   
                "CXPB" : [0.8, 0.9],
                "MUTPB" : [0.01, 0.05, 0.1]
            },
            out_name="test_parametrico",
            seeds=[1,2,3]
        )

    def evaluate_ae(self, 
        func_to_eval,
        parameters: dict,
        out_name: str,
        initial_config: dict=None, 
        image_path: str="img/ultima_cena.jpg", 
        seeds: "list[int]"=[i for i in range(30)]
        ):

        # configuracion inicial, si existe
        if initial_config is not None:
            for k, v in initial_config:
                print(f"seteando config inicial {k} to ", *v)
                self.eac.deap_configurer.__setattr__(k, *v)

        # se setea la imagen que se va a utilizar para la configuracion
        self.eac.evolutionary_algorithm.image_processor.img_in_dir = image_path
        self.eac.evolutionary_algorithm.load_image()

        ortogonal_combinations = list(product(*parameters.values()))
        values = []

        header_fitness = []
        best_fitness_config = []

        # para cada configuracion parametrica
        for config in ortogonal_combinations:


            # se setean los parametros de la configuracion
            for k, v in zip(parameters.keys(), config):
                print(f"seteando config {k} ", v)
                if type(v) is list:
                    # formato esperado : [function, {"keyword_arg1": value, ...}]
                    self.eac.deap_configurer.__getattribute__("toolbox").register(k, v[0], **v[1])
                else: 
                    self.eac.deap_configurer.__setattr__(k, v)

            best_execution_fitness = []
            time_execution = []

            # para cada seed
            for s in seeds:
                print(f"Evaluating seed {s+1}/{len(seeds)} of config {config}")

                self.eac.deap_configurer.__setattr__('seed', s)
                # si no salta error de pool not running
                self.eac.deap_configurer.register_parallelism()

                start = time()
                # devuelve lista de min fitness en cada generacion
                best_fitness_per_gen = func_to_eval(show_res=False)
                end = time()

                # se guarda el min fitness de una ejecucion. ejecucion = conf_alg + seed
                best_execution_fitness.append(np.min(best_fitness_per_gen))
                
                time_execution.append(end - start)

            # se guardan los valores obtenidos para la configuracion
            config_values = []
            for val in config:
                if type(val) is list:
                    config_values.append(val[0].__name__)
                else:
                    config_values.append(val)

            values.append([
                *config_values, min(best_execution_fitness), 
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                np.mean(time_execution),
                self.normality_test(best_execution_fitness),
            ])

            header_fitness.append(str(config_values))
            best_fitness_config.append(best_execution_fitness)

        header = [
            *parameters.keys(), "best_historical_fitness", 
            "avg_best_fitness", "std_fitness", "avg_time", "p-value"
        ]
        pd.DataFrame(values, columns=header).to_csv(f"results/reports/{out_name}.csv", index=False)

        # cada columna es una configuracion y tiene n filas, donde n es la cantidad de ejecuciones (seeds)
        pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/{out_name}.csv", index=False)

        return


    def efficiency_evaluation(self, seed=0, instance="img/ultima_cena.jpg"):
        """
        Se define el speedup algorítmico como SN = T1 / TN, siendo:
            * T1 el tiempo de ejecución del algoritmo en forma serial
            * TN el tiempo del algoritmo paralelo ejecutado sobre N procesadores

        Se define la eficiencia computacional como EN = T1 / (N * TN )
            * N cantidad de procesadores
        """
        values = []
        
        random.seed(seed)
        self.eac.deap_configurer.__setattr__('seed', seed)
        self.eac.evolutionary_algorithm.image_processor.img_in_dir = instance
        self.eac.evolutionary_algorithm.load_image()

        for i in range(1,cpu_count()+1):
            self.eac.deap_configurer.__setattr__('cpu_count', i)
            self.eac.deap_configurer.register_parallelism()
            
            start = time()
            self.eac.run(show_res=False)
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
                *current_values, min(best_fitnesses),
                np.mean(best_execution_fitness), np.std(best_execution_fitness),
                np.mean(time_execution),
                self.normality_test(best_execution_fitness)
            ])
        
            header_fitness.append(str(current_values))
            best_fitness_config.append(best_execution_fitness)

    def informal_evaluation_2(self, best_config : dict, vertex_count: int, attributes: dict, image_path: str, image_name: str,  seeds: list = [1,2,3,4]):
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

    def parametric_evaluation2(self, vertex_count: int, attributes: dict, image_path: str, images: list=["ultima_cena.jpg"], seeds: list = [1,2,3,4]):
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
                
    def greedy_evaluation_2(self, best_config: dict, greedy_config: dict, image_path: str, images: dict, seeds: list = [1,2]):
        best_execution_fitness = []
        results = []
        header_fitness = []
        best_fitness_config = []
        EA_ID = "EA"

        for img in images:
            print(f"Evaluating image {img}")
            vertex_count = images.get("vertex_count", 100)
            eac = self.__build_eac(img, image_path, vertex_count, width=images.get("width", 500))
            self.__update_config(eac, best_config)
            alt_solver = AltSolver(eac.evolutionary_algorithm)

            for method in list(greedy_config.keys()) + [EA_ID]:

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
                        start = time()
                        _, best_eval = alt_solver.solve(**(greedy_config[method]), vertex_count=vertex_count, method=method, verbose=False)
                        end = time()
                        best_execution_fitness.append(best_eval.min())
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
        pd.DataFrame(results, columns=header).to_csv(f"results/greedy.csv", index=False)
        pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/best_fit_per_config_greedy.csv", index=False)

    def plot_performance(self):
        df = pd.read_csv("results/greedy.csv")
        df_pivot = df.pivot(index='seed', columns='method', values='best_historical_fitness')
        df_pivot.plot.box()
        plt.show()

    def plot_time(self):
        df = pd.read_csv("results/time.csv")
        #CPU,time,speedup,efficiency
        columns = ["time", "speedup", "efficiency"]
        df_pivot = df.pivot(index='CPU', columns=columns[0], values='time')
        #df_pivot.plot.bar()
        df_pivot = df.pivot(index='CPU', columns="time", values="time")
        df_pivot.plot.bar()
        plt.show()

    def to_latex(self):
        df = pd.read_csv("results/greedy.csv")
        df_pivot = df.pivot(index='seed', columns='method', values='best_historical_fitness')
        #convert to latex with style
        print(df_pivot.style.to_latex())

    def pairwise_matrix(self, data):
        import scikit_posthocs as sp
        rank = data.argsort().argsort(axis=1)
        pvalues = sp.posthoc_dunn(rank, p_adjust = 'holm')
        plt.matshow(pvalues)

        for (x, y), value in np.ndenumerate(pvalues):
            plt.text(x, y, f"{value:.2f}", va="center", ha="center")
            
        plt.colorbar()
        #plt.show()
        print(pvalues)

    def friedman_ranking(self, data):
        from scipy.stats import friedmanchisquare
        from scikit_posthocs import posthoc_nemenyi_friedman
        rank = data.argsort().argsort(axis=1)
        #perform friedman test
        _, p_value = friedmanchisquare(*rank)
        print(f"p-value: {p_value}")
        #perform post-hoc test
        pvalues = posthoc_nemenyi_friedman(rank)
        print(pvalues)
        #self.pairwise_matrix(data)

        


        



        #pd.DataFrame(np.transpose(np.array(best_fitness_config)), columns=header_fitness).to_csv(f"results/best_fitness_execution/greedy2.csv", index=False)
