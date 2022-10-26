import random

import numpy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import prueba

IND_SIZE=100

# estas habra que setearlas segun la imagen que leamos
WIDTH_MIN, WIDTH_MAX = 0, 255
HEIGHT_MIN, HEIGHT_MAX = 0, 255

VERTEX_COUNT = 500

def create_individual_representation(toolbox, rgb = False):
    return (toolbox.attr_x_coord, toolbox.attr_y_coord)

def register_population(toolbox):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # definicion de atributos y sus rangos de valores asociados
    toolbox.register("attr_x_coord", random.randint, WIDTH_MIN, WIDTH_MAX)
    toolbox.register("attr_y_coord", random.randint, HEIGHT_MIN, HEIGHT_MAX)

    individual_representation = create_individual_representation(toolbox)
    toolbox.register("individual", 
                        tools.initCycle,
                        creator.Individual,
                        individual_representation, 
                        n=VERTEX_COUNT
                    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    return toolbox

def register_operators(toolbox: base.Toolbox):
    toolbox.register("evaluate", prueba.evalDelaunay)
    toolbox.register("mate", tools.cxOnePoint)#, alpha=0.5)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=255, indpb=0.1) #TODO: DESHARDCODEAR up y low
    toolbox.register("select", tools.selTournament, tournsize=3)
    return toolbox

def register_stats():
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    return stats

def main():
    random.seed(64)
    NGEN = 1000000
    MU = 50
    LAMBDA = 100
    CXPB = 0.8
    MUTPB = 0.2

    toolbox = base.Toolbox()
    register_population(toolbox)
    register_operators(toolbox)
    pop = toolbox.population(n=MU)
    stats = register_stats()

    pop, stats = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats, verbose=True)


    return pop, stats

if __name__ == "__main__":
    main()               