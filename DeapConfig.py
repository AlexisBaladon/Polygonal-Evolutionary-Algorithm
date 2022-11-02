from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import random
import numpy as np
import os

from multiprocessing import Pool

class DeapConfig:
    def __init__(self, seed=64, vertex_count=1000, toolbox=base.Toolbox(), stats=tools.Statistics(),  gene_mutation_probability=0.1, pool_size=os.cpu_count(), NGEN=1000000, MU=50, LAMBDA=50, CXPB=0.8, MUTPB=0.2, mutation_probability=0.1, width_max=255, height_max=255):
        self.seed = seed
        self.vertex_count = vertex_count

        
        self.toolbox = toolbox
        self.stats = stats

        self.pool_size = pool_size

        self.width_max = width_max
        self.height_max = height_max

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
        self.mutation_probability = mutation_probability

        self.gene_mutation_probability = gene_mutation_probability
    
    def register_individual_type(self):
        # definicion de atributos y sus rangos de valores asociados
        self.toolbox.register("attr_x_coord", random.randint, 0, self.width_max)
        self.toolbox.register("attr_y_coord", random.randint, 0, self.height_max)

    def create_individual_representation(self):
        return (self.toolbox.attr_x_coord, self.toolbox.attr_y_coord)

    def register_fitness(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
    
    def register_population(self):
        self.register_individual_type()
        individual_representation = self.create_individual_representation()

        self.toolbox.register("individual", tools.initCycle, creator.Individual, individual_representation, n=self.vertex_count)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

    def register_operators(self, fitness_custom_function):
        self.toolbox.register("evaluate", fitness_custom_function)
        self.toolbox.register("mate", tools.cxOnePoint)
        min = self.height_max if self.height_max < self.width_max else self.width_max
        self.toolbox.register("mutate", tools.mutUniformInt, low=0, up=min, indpb=self.gene_mutation_probability)
        self.toolbox.register("select", tools.selBest)

    
    # logs and stats related #

    def register_stats(self):
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("std", np.std)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

    def register_parallelism(self):
        # with Pool(self.pool_size) as pool:
        #     results = pool.imap_unordered(self.toolbox.evaluate, )
        # self.toolbox.register("map", pool.map)
        # return results
        return
    
    def run_algorithm(self):
        pop = self.toolbox.population(n=self.MU)
        algorithms.eaMuPlusLambda(pop, self.toolbox, self.MU, self.LAMBDA, self.CXPB, self.MUTPB, self.NGEN, self.stats, verbose=True)