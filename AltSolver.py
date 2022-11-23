from EA import EA
import random
import numpy as np

class AltSolver:
    def __init__(self, evolutionary_algorithm: EA):
        self.ea = evolutionary_algorithm
        pass

    def build_ea_module(self):
        self.ea.load_image()

    def __get_deltas(self, method: str, threshold: int):
        if method == 'gaussian':
            gaussian_std = threshold
            deltas = [np.random.normal(0, gaussian_std)] #changes
        elif method == 'local_search':
            deltas = list(range(-threshold, threshold+1))
        else:
            raise Exception('Invalid method')
        return deltas

    def solve(self, method: str, max_iter: int, vertex_count: int, threshold = 500, verbose = True):
        ind_size = vertex_count * 2
        max_x, max_y = self.ea.image_processor.width-1, self.ea.image_processor.height-1
        edges = self.ea.image_processor.edges_coordinates
        min_individual = self.ea.init_coordinates(max_x, max_y, ind_size, edges)
        min_eval, = self.ea.evalDelaunay(min_individual)

        if verbose:
            initial_eval = min_eval

        i = 0
        while i < max_iter:
            ind_gene = random.randint(0, ind_size-1)
            best_delta = 0
            deltas = self.__get_deltas(method, threshold)
            for delta in deltas:
                if not (0 <= min_individual[ind_gene] + delta <= 255) or delta==0: 
                    continue
                min_individual[ind_gene] += delta
                eval_candidate, = self.ea.evalDelaunay(min_individual)
                if eval_candidate < min_eval:
                    min_eval = eval_candidate
                    best_delta = delta
                    if verbose:
                        print(f'New best individual found at iteration {i}/{max_iter} with fitness {min_eval}')
                min_individual[ind_gene] -= delta
            min_individual[ind_gene] += best_delta 
            if verbose:
                print(f'Iteration {i}/{max_iter} finished with fitness {min_eval}')
            i += 1
        if verbose:
            print(f'Initial fitness: {initial_eval} - Final fitness: {min_eval}')
        return min_individual, min_eval