import random

import numpy as np

from src.models.evolutionary_algorithm.ea_methods import EA

GAUSSIAN_METHOD = 'gaussian'
LOCAL_SEARCH_METHOD = 'local_search'

class LocalSearchSolver:
    def __init__(self, evolutionary_algorithm: EA, seed: str = 0):
        self.ea = evolutionary_algorithm
        random.seed(seed)
        pass

    def update_seed(self, seed):
        random.seed(seed)

    def build_ea_module(self):
        self.ea.load_image()

    def __get_deltas(self, method: str, threshold: int):
        if method == GAUSSIAN_METHOD:
            gaussian_std = threshold
            deltas = [np.random.normal(0, gaussian_std)]
        elif method == LOCAL_SEARCH_METHOD:
            deltas = list(range(-threshold, threshold+1))
        else:
            raise Exception(f'Invalid method: {method}')
        return deltas

    def solve(self, method: str, max_iter: int, threshold = 500, 
              max_evals = 60, verbose = True):
        ip = self.ea.image_processor
        max_x, max_y = ip.width-1, ip.height-1
        ind_size = ip.vertex_count * 2
        edges = ip.edges_coordinates
        min_individual = self.ea.init_coordinates(max_x, max_y, ind_size, edges)
        min_eval, = self.ea.eval_individual(min_individual)

        if verbose:
            initial_eval = min_eval

        i = 0
        eval_count = 1
        while i < max_iter and eval_count < max_evals:
            ind_gene = random.randint(0, ind_size-1)
            best_delta = 0
            deltas = self.__get_deltas(method, threshold)
            for delta in deltas:
                limit = max_x if ind_gene % 2 == 0 else max_y

                shifted_individual = min_individual[ind_gene] + delta
                if not (0 <= shifted_individual <= limit) or delta==0: 
                    continue

                min_individual[ind_gene] += delta
                eval_candidate, = self.ea.eval_individual(min_individual)
                eval_count += 1
                
                if eval_candidate < min_eval:
                    min_eval = eval_candidate
                    best_delta = delta

                    if verbose:
                        print("*"*75)
                        print(f'New best individual found at iteration {i}/{max_iter} with fitness {min_eval}')
                        print("*"*75, end='\n\n')

                min_individual[ind_gene] -= delta
            min_individual[ind_gene] += best_delta 

            if verbose:
                print(f'Iteration {i}/{max_iter} finished with fitness {min_eval}')
                print(f'Current eval count: {eval_count}')
                print()

            i += 1

        if verbose:
            print("#"*60)
            print(f'Initial fitness: {initial_eval} - Final fitness: {min_eval}')
            print("#"*60, end='\n\n')

        return min_individual, min_eval