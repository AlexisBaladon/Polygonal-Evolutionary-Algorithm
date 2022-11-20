from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import random
import pandas
import numpy as np
import os

import multiprocessing

class DeapConfig:
    def __init__(self, seed=64, ind_size=2000,
                 INDPB=0.1, cpu_count=os.cpu_count(),
                 NGEN=2, MU=50, LAMBDA=50, CXPB=0.8, MUTPB=0.2, **kwargs):

        self.toolbox = base.Toolbox()
        self.stats = tools.Statistics()
        self.seed = seed
        self.ind_size = ind_size
        self.cpu_count = cpu_count
        # number of generations to run
        self.NGEN = NGEN
        # population size
        self.MU = MU
        # number of children to produce at each generation
        self.LAMBDA = LAMBDA
        # probability of mating two individuals
        self.CXPB = CXPB
        # probability of mutating an individual
        self.MUTPB = MUTPB
        # probability of mutating a gene
        self.INDPB = INDPB
    
    #CUSTOM OPERATORS
    def __init_coordinates(self, init_coordinates, order_individual):
        coordinates = init_coordinates()
        coordinates = order_individual(coordinates)
        coordinates = creator.Individual(coordinates)
        return coordinates

    def register_fitness(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

    def register_population(self, init_coordinates, order_individual):
        init_coordinates_ = lambda: init_coordinates(self.ind_size)
        self.toolbox.register("individual", self.__init_coordinates, init_coordinates_, order_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

    def register_operators(self, fitness_custom_function, mutation_custom_function, max_x, max_y):
        self.toolbox.register("evaluate", fitness_custom_function)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", mutation_custom_function, mu_x=0, mu_y=0, sigma_x=max_x/50, sigma_y=max_y/50, indpb=self.INDPB)
        #self.toolbox.register("select", tools.selTournament, tournsize=self.MU//5)
        self.toolbox.register("select", tools.selBest)
    
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
    
    def save_logs(self, logbook):
        df_log = pandas.DataFrame(logbook)
        df_log.to_csv('./logs/last.csv', index=False) #TODO: PARAMETRIZAR
    
    def register_seed(self):
        random.seed(self.seed)

    def run_algorithm(self, parallel=True):
        if parallel:
            with self.process_pool:
                population, logbook = self.__run_algorithm()
        else:
            population, logbook = self.__run_algorithm()
        return population, logbook

    def __run_algorithm(self):
            pop = self.toolbox.population(n=self.MU)
            pop, logbook = self.__eaMuPlusLambda(pop, self.toolbox, self.MU, self.LAMBDA,
                             self.CXPB, self.MUTPB, self.NGEN, self.stats, verbose=True)
            return pop, logbook

        #SAME IMPLEMENTATION AS IN DEAP LIBRARY BUT WITH CHUNKSIZE DEFINED IN MAP FUNCTIONS
    def __eaMuPlusLambda(self, population, toolbox, mu, lambda_, cxpb, mutpb, ngen, stats=None,
                         halloffame=None, verbose=None):

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind, chunksize=len(population)//self.cpu_count)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)

        if verbose:
            print(logbook.stream)

        for gen in range(1, ngen + 1): #TODO: HACER WHILE
            offspring = algorithms.varOr(population, toolbox, lambda_, cxpb, mutpb)
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind, chunksize=len(population)//self.cpu_count)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            if halloffame is not None:
                halloffame.update(offspring)
            population[:] = toolbox.select(population + offspring, mu)
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)

            if verbose:
                print(logbook.stream)
                #img = image_processor.decode(population[0])
                #img.save(f'test/womhd/{self.ind_size >> 1}-IMAGEN_{gen}.png')

        return population, logbook