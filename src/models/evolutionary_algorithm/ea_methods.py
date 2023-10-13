import random

import numpy as np

from src.utils.image_processor import ImageProcessor

class EA():
    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor

    def load_image(self, verbose=False, show=False):
        self.image_processor.read_image(verbose=verbose, show=show)
    
    def init_coordinates(self, max_x, max_y, n, edges, edge_rate=0.5):
        genotype = []
        for _ in range(0, n, 2):
            if edges and random.random() < edge_rate:
                edge = random.choice(edges)
                genotype.extend(edge)
            else:
                genotype.append(random.randint(0, max_x))
                genotype.append(random.randint(0, max_y))
        return genotype

    def order_individual(self, individual):
        individual = list(zip(individual[0::2], individual[1::2]))
        individual.sort(key=lambda x: (x[0], x[1]))
        individual = [item for sublist in individual for item in sublist]
        return individual

    def get_vertices(self, individual):
        width, height = self.image_processor.width, self.image_processor.height
        individual[::2] = np.clip(individual[::2], 0, width)
        individual[1::2] = np.clip(individual[1::2], 0, height)
        individual = list(map(int, individual))
        vertices = list(zip(individual[::2], individual[1::2]))
        vertices.extend([(0,0), (0,height), (width,0), (width,height)]) #Always include the corners
        vertices = np.array(vertices)
        return vertices

    def decode(self, individual):
        vertices = self.get_vertices(individual)
        polygonal_image = self.image_processor.create_polygonal_image(vertices)
        return polygonal_image

    def get_fitness(self, decoded_individual):
        individual_image_matrix = np.asarray(decoded_individual, dtype=np.uint64)
        original_image_matrix = self.image_processor.original_image_matrix
        diff = individual_image_matrix - original_image_matrix
        squared_diff = np.sum(diff**2, dtype=np.uint64)
        w, h = self.image_processor.width, self.image_processor.height
        return squared_diff / (w * h)

    def eval_individual(self, individual):
        decoded_individual = self.decode(individual)
        fit = self.get_fitness(decoded_individual)
        return fit, # Fitness should be inside a tuple

    def mut_gaussian_coordinate(self, individual, sigma_x, sigma_y, indpb=0.2):
        size = len(individual)
        for i in range(0,size,2):
            if random.random() < indpb:
                individual[i] += random.gauss(0, sigma_x)
                individual[i+1] += random.gauss(0, sigma_y)
        return individual,