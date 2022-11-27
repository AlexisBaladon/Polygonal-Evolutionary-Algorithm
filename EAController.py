from EA import EA
from DeapConfig import DeapConfig

class EAController:
    def __init__(self, ea: EA, deap_c: DeapConfig):
        self.evolutionary_algorithm = ea
        self.deap_configurer = deap_c

    def build_ea_module(self, verbose=True, show_img=False):
        self.evolutionary_algorithm.load_image(verbose=verbose, show=show_img)

    #FITNESS MUST BE REGISTERED OUTSIDE OF MAIN WHEN USING PARALLELISM
    def build_deap_module(self):
        width, height = self.evolutionary_algorithm.image_processor.width, self.evolutionary_algorithm.image_processor.height
        edges_coordinates = self.evolutionary_algorithm.image_processor.edges_coordinates
        ind_size = self.evolutionary_algorithm.image_processor.vertex_count * 2
        fitness_function, mutation_function = self.evolutionary_algorithm.evalDelaunay, self.evolutionary_algorithm.mutGaussianCoordinate
        init_coordinates = lambda edge_rate: self.evolutionary_algorithm.init_coordinates(width-1, height-1, ind_size, edges_coordinates, edge_rate=edge_rate)
        self.deap_configurer.register_population(init_coordinates, self.evolutionary_algorithm.order_individual)
        self.deap_configurer.register_operators(fitness_function, mutation_function, width-1, height-1)
        self.deap_configurer.register_stats()
        if self.deap_configurer.cpu_count > 1:
            self.deap_configurer.register_parallelism() 
        
    def run(self, show_res=True, logs=True, seed=0):
        is_parallel = bool(self.deap_configurer.cpu_count > 1)
        population, log_info, hall_of_fame, best_fitnesses = self.deap_configurer.run_algorithm(parallel=is_parallel)

        # Save files
        img = self.evolutionary_algorithm.decode(population[0])
        img.save(self.evolutionary_algorithm.image_processor.img_out_dir)
        if verbose:
            img.show()
        if logs:
            self.deap_configurer.save_logs(
                log_info, 
                seed=seed,
                file_name=self.evolutionary_algorithm.image_processor.input_name,
                hall_of_fame=hall_of_fame)
        return best_fitnesses

