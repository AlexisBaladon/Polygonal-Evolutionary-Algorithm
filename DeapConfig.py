from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from deap.tools import HallOfFame

import random
import pandas
import numpy as np
import os

import multiprocessing

class DeapConfig:
    def __init__(self, ind_size=2000,
                 INDPB=0.1, cpu_count=os.cpu_count(), selection="best", tournament_size=3,
                 gaussian_rate=0.5, NGEN=2, MU=50, LAMBDA=50, CXPB=0.8, MUTPB=0.2, edge_rate=0.5, **kwargs):

        self.toolbox = base.Toolbox()
        self.stats = tools.Statistics()
        self.ind_size = ind_size
        self.cpu_count = cpu_count
        
        self.NGEN = NGEN
        # population size
        self.MU = MU
        # number of children to produce at each generation
        self.LAMBDA = LAMBDA
        self.CXPB = CXPB
        self.MUTPB = MUTPB
        # probability of mutating a gene
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

    @staticmethod
    def register_fitness():
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

    def register_population(self, init_coordinates, order_individual):
        self.toolbox.register("individual", self.__init_coordinates, init_coordinates, order_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

    def register_operators(self, fitness_custom_function, mutation_custom_function, max_x, max_y):
        selections = {
            "best"      : {"function": tools.selBest},
            "stochastic": {"function": tools.selStochasticUniversalSampling},
            "tournament": {"function": tools.selTournament, "tournsize": self.tournament_size},
        }

        self.toolbox.register("evaluate", fitness_custom_function)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", mutation_custom_function, sigma_x=max_x*self.gaussian_rate, sigma_y=max_y*self.gaussian_rate, indpb=self.INDPB)
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
    
    def save_logs(self, logbook, seed : int, file_name="default", hall_of_fame=None):
        df_log = pandas.DataFrame(logbook)
        df_log.to_csv(f'./logs/{file_name}_{seed}.csv', index=False) #TODO: PARAMETRIZAR
        if hall_of_fame:
            df_hall_of_fame = pandas.DataFrame(hall_of_fame)
            df_hall_of_fame.to_csv(f'./logs/best_individual_{file_name}_{seed}.csv', index=False)
    
    def run_algorithm(self, parallel=True):
        if parallel:
            with self.process_pool:
                population, logbook, hof, best_fitnesses = self.__run_algorithm()
        else:
            population, logbook, hof, best_fitnesses = self.__run_algorithm()
        return population, logbook, hof, best_fitnesses

    def __run_algorithm(self):
            pop = self.toolbox.population(n=self.MU)
            pop, logbook, hof, best_fitnesses = self.__eaMuPlusLambda(pop, self.toolbox, self.MU, self.LAMBDA, self.CXPB, self.MUTPB, self.NGEN, self.stats, verbose=True)
            return pop, logbook, hof, best_fitnesses

    def force_stop(self):
        self.forced_stop = True

    def __stop_condition(self, gen: int, ngen: int, fitnesses: "list[int]"):
        #last generation, or fitness not changing for 0.2*NGEN generations, or forced stop from main thread
        INVARIANCE_THRESHOLD = 0.2
        GEN_INV_THRESHOLD = int(INVARIANCE_THRESHOLD * ngen)

        conditions = [
            gen >= ngen,
            GEN_INV_THRESHOLD > 1 and (gen >= GEN_INV_THRESHOLD) and len(set(fitnesses[-GEN_INV_THRESHOLD:])) == 1,
            self.forced_stop
        ]

        return any(conditions)

    def __eaMuPlusLambda(self, population: list, toolbox: base.Toolbox, 
                         mu: int, lambda_: int, cxpb: float, mutpb: float, ngen: int,
                         stats: tools.Statistics = None, halloffame: tools.HallOfFame = HallOfFame(1), verbose=True):

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])
        parallelism_params = {} if self.cpu_count < 2 else {"chunksize": len(population)//self.cpu_count}

        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind, **parallelism_params)
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
        while not self.__stop_condition(gen, ngen, best_fitnesses):
            offspring = algorithms.varOr(population, toolbox, lambda_, cxpb, mutpb)
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind, **parallelism_params)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            if halloffame is not None:
                halloffame.update(offspring)
            population[:] = toolbox.select(population + offspring, mu)
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:
                print(logbook.stream)
            best_fitnesses.append(record['min'])
            gen += 1

        return population, logbook, halloffame, best_fitnesses