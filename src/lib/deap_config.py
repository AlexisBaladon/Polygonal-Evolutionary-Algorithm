import os
import multiprocessing

from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap.tools import HallOfFame
import pandas
import numpy as np

BEST_SELECTION = 'best'
TOURNAMENT_SELECTION = 'torunament'
CPU_COUNT = os.cpu_count()

class DeapConfig:
    def __init__(self, INDPB=0.1, cpu_count=CPU_COUNT, selection=BEST_SELECTION, 
                 tournament_size=3, gaussian_rate=0.05, NGEN=2, 
                 MU=50, LAMBDA=50, CXPB=0.9, MUTPB=0.1, edge_rate=0.5, 
                 log_dir=os.path.join('data', 'outputs', 'executions', 'logs'), 
                 **kwargs):

        self.toolbox = base.Toolbox()
        self.stats = tools.Statistics()
        self.cpu_count = cpu_count
        self.log_dir = log_dir
        
        self.NGEN = NGEN
        self.MU = MU
        self.LAMBDA = LAMBDA
        self.CXPB = CXPB
        self.MUTPB = MUTPB
        self.INDPB = INDPB
        self.gaussian_rate = gaussian_rate
        self.selection = selection
        self.tournament_size = tournament_size

        #rate of edges in initialization
        self.edge_rate = edge_rate

        #force stop from main thread
        self.forced_stop = False
    
    def __init_coordinates(self, init_coordinates, order_individual):
        coordinates = init_coordinates(self.edge_rate)
        coordinates = order_individual(coordinates)
        coordinates = creator.Individual(coordinates)
        return coordinates

    # Needs to be used before creating the class (DEAP parallelism bug)
    @staticmethod
    def register_fitness():
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

    def register_population(self, init_coordinates, order_individual):
        self.toolbox.register("individual",
                              self.__init_coordinates, 
                              init_coordinates, 
                              order_individual)
        self.toolbox.register("population", 
                              tools.initRepeat, 
                              list, self.toolbox.individual)

    def register_operators(self, 
                           fitness_custom_function, 
                           mutation_custom_function, 
                           max_x, max_y):
        
        selections = {BEST_SELECTION: {"function": tools.selBest},
                     TOURNAMENT_SELECTION: {"function": tools.selTournament, 
                                            "tournsize": self.tournament_size}}

        self.toolbox.register("evaluate", fitness_custom_function)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", mutation_custom_function, 
                                        sigma_x=max_x*self.gaussian_rate, 
                                        sigma_y=max_y*self.gaussian_rate, 
                                        indpb=self.INDPB)
        self.toolbox.register("select", **selections[self.selection])
    
    def register_stats(self):
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

    def register_parallelism(self):
        self.process_pool = multiprocessing.Pool(self.cpu_count)
        self.toolbox.register("map", self.process_pool.map)
        return
    
    def save_logs(self, logbook, seed : str, 
                  file_name="default", hall_of_fame=None):
        df_log = pandas.DataFrame(logbook)

        log_dir = os.path.join(self.log_dir, f'{file_name}_{seed}.csv')
        df_log.to_csv(log_dir, index=False)

        if hall_of_fame:
            df_hall_of_fame = pandas.DataFrame(hall_of_fame)
            hall_of_fame_dir = os.path.join(self.log_dir, f'{file_name}_{seed}.csv')
            df_hall_of_fame.to_csv(hall_of_fame_dir, index=False)
    
    def run_algorithm(self, 
                      image_added_callback=lambda *_: None, 
                      stop_condition_callback=lambda: False, 
                      parallel=True):
        if parallel:
            with self.process_pool:
                population, logbook, hof, best_fitnesses = self.__run_algorithm(image_added_callback=image_added_callback,
                                                                                stop_condition_callback=stop_condition_callback)
        else:
            population, logbook, hof, best_fitnesses = self.__run_algorithm(image_added_callback=image_added_callback,
                                                                            stop_condition_callback=stop_condition_callback)

        return population, logbook, hof, best_fitnesses

    def __run_algorithm(self, 
                        image_added_callback=lambda *_: None,
                        stop_condition_callback=lambda: False):
            pop = self.toolbox.population(n=self.MU)
            pop, logbook, hof, best_fitnesses = self.__eaMuPlusLambda(pop, 
                                                                      self.toolbox, 
                                                                      self.MU, 
                                                                      self.LAMBDA, 
                                                                      self.CXPB, 
                                                                      self.MUTPB, 
                                                                      self.NGEN, 
                                                                      stats=self.stats, 
                                                                      image_added_callback=image_added_callback,
                                                                      stop_condition_callback=stop_condition_callback,
                                                                      verbose=True)
            return pop, logbook, hof, best_fitnesses

    def force_stop(self):
        self.forced_stop = True

    def __stop_condition(self, 
                         gen: int, 
                         ngen: int, 
                         stop_condition_callback=lambda: False):
        self.forced_stop = self.forced_stop or stop_condition_callback()
        
        conditions = [
            gen >= ngen,
            self.forced_stop, # User is allowed to stop the algorithm from the main thread,
        ]

        return any(conditions)

    # Modified version of original DEAP function: eaMuPlusLambda 
    # https://deap.readthedocs.io/en/master/_modules/deap/algorithms.html#eaMuPlusLambda
    def __eaMuPlusLambda(self, population: list, toolbox: base.Toolbox, 
                         mu: int, lambda_: int, cxpb: float, 
                         mutpb: float, ngen: int, 
                         stats: tools.Statistics = None, 
                         halloffame: tools.HallOfFame = HallOfFame(1),
                         image_added_callback= lambda *_: None,
                         stop_condition_callback=lambda: False,
                         verbose=True):

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        parallelism_params = {} if self.cpu_count < 2 else \
                             {"chunksize": len(population)//self.cpu_count}

        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = list(toolbox.map(toolbox.evaluate, invalid_ind, **parallelism_params))

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)

        if verbose:
            print(logbook.stream)

        gen = 1
        best_fitnesses = [record['min']]
        image_added_callback({"population": population[:],
                              "fitness": fitnesses[:]},
                              gen)

        while not self.__stop_condition(gen, ngen, stop_condition_callback):
            offspring = algorithms.varOr(population, toolbox, 
                                         lambda_, cxpb, mutpb)
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = list(toolbox.map(toolbox.evaluate, 
                                         invalid_ind, 
                                         **parallelism_params))

            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            if halloffame is not None:
                halloffame.update(offspring)

            population[:] = toolbox.select(population + offspring, mu)
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)

            if verbose:
                print(logbook.stream)

            gen += 1
            min_loss = record['min']
            best_fitnesses.append(min_loss)
            image_added_callback({"population": population[:],
                                  "fitness": fitnesses[:]},
                                  gen)

        return population, logbook, halloffame, best_fitnesses