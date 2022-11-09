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
    def __init__(self, seed=64, ind_size=12,
                 INDPB=0.1, cpu_count=os.cpu_count(),
                 NGEN=100, MU=50, LAMBDA=50, CXPB=0.8, MUTPB=0.2, **kwargs):

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
    


    def register_fitness(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

    def __create_individual_representation(self):
        return (self.toolbox.attr_x_coord, self.toolbox.attr_y_coord)

    def __register_individual_type(self):
        # definicion de atributos y sus rangos de valores asociados
        self.toolbox.register("attr_x_coord", random.randint, 0, self.max_x)
        self.toolbox.register("attr_y_coord", random.randint, 0, self.max_y)
    
    #define initialization of deap individual for initCycle
    def __initCycle(self, individual, edges, n):
        edges_coords = [random.choice(edges) for _ in range(n >> 1)]
        genotype = [x for edge in edges_coords for x in edge]
        genotype = individual(genotype)
        return genotype

    def register_population(self, max_x, max_y, edges=None):
        self.max_x = max_x
        self.max_y = max_y
        self.__register_individual_type()
        individual_representation = self.__create_individual_representation()

        if edges:
            #initialize custom individual
            self.toolbox.register("individual", self.__initCycle, creator.Individual, edges, self.ind_size)
            self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        else:    
            self.toolbox.register("individual", tools.initCycle, creator.Individual, individual_representation, n=self.ind_size)
            self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

    def __mutGaussianCoordinate(self, individual, mu_x=0, mu_y=0, sigma_x=50, sigma_y=50, indpb=0.2):
        size = len(individual)
        for i in range(0,size,2):
            if random.random() < indpb:
                individual[i] += random.gauss(mu_x, sigma_x)
                individual[i+1] += random.gauss(mu_y, sigma_y)
        return individual,

    def __mutUniformCoordinate(self, individual, indpb=0.2):
        size = len(individual)
        for i in range(0,size,2):
            if random.random() < indpb:
                individual[i] = random.randint(0,self.max_x)
                individual[i+1] = random.randint(0,self.max_y)
        return individual,

    def register_operators(self, fitness_custom_function):
        self.toolbox.register("evaluate", fitness_custom_function)
        self.toolbox.register("mate", tools.cxTwoPoint)
        #self.toolbox.register("mate", tools.cxOnePoint)
        #self.toolbox.register("mutate", tools.mutUniformInt, low=0, up=255, indpb=self.INDPB)
        #self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=50, indpb=self.INDPB)
        #self.toolbox.register("mutate",self.__mutUniformCoordinate, indpb=self.INDPB)
        self.toolbox.register("mutate", self.__mutGaussianCoordinate, mu_x=0, mu_y=0, sigma_x=self.max_x/10, sigma_y=self.max_y/10, indpb=self.INDPB)
        self.toolbox.register("select", tools.selBest)

    
    # logs and stats related #

    def register_stats(self):
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

    def register_parallelism(self):
        pool = multiprocessing.Pool(self.cpu_count)
        self.toolbox.register("map", pool.map)
        return
    
    def save_logs(self, logbook):
        df_log = pandas.DataFrame(logbook)
        df_log.to_csv('./logs/last.csv', index=False)
    
    def register_seed(self):
        random.seed(self.seed)

    def run_algorithm(self, logs=False):
        pop = self.toolbox.population(n=self.MU)
        pop, logbook = algorithms.eaMuPlusLambda(pop, self.toolbox, self.MU, self.LAMBDA, self.CXPB, self.MUTPB, self.NGEN, self.stats, verbose=True)
        if logs:
            self.save_logs(logbook)