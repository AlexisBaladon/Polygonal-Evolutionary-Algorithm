from EA import EA
from DeapConfig import DeapConfig

class EAController:
    def __init__(self, ea: EA, deap_c: DeapConfig):
        self.evolutionary_algorithm = ea
        self.deap_configurer = deap_c

    def build_ea_module(self):
        self.evolutionary_algorithm.load_image()

    def build_deap_module(self):
        #self.deap_configurer.register_fitness() ONLY RUN OUTSIDE MAIN
        width, height = self.evolutionary_algorithm.image_processor.width, self.evolutionary_algorithm.image_processor.height
        edges_coordinates = self.evolutionary_algorithm.image_processor.edges_coordinates
        ind_size = self.evolutionary_algorithm.image_processor.vertex_count * 2
        fitness_function, mutation_function = self.evolutionary_algorithm.evalDelaunay, self.evolutionary_algorithm.mutGaussianCoordinate
        init_coordinates = lambda: self.evolutionary_algorithm.init_coordinates(width-1, height-1, ind_size, edges_coordinates)
        self.deap_configurer.register_population(init_coordinates, self.evolutionary_algorithm.order_individual)
        self.deap_configurer.register_operators(fitness_function, mutation_function, width-1, height-1)
        self.deap_configurer.register_stats()
        self.deap_configurer.register_seed()
        if self.deap_configurer.cpu_count > 0:
            self.deap_configurer.register_parallelism() #ONLY RUN INSIDE MAIN
        
    def run(self, logs=True):
        is_parallel = bool(self.deap_configurer.cpu_count > 1)
        population, log_info = self.deap_configurer.run_algorithm(parallel=is_parallel)

        # Save files
        img = self.evolutionary_algorithm.decode(population[0])
        img.save(self.evolutionary_algorithm.image_processor.img_out_dir)
        img.show()
        if logs:
            self.deap_configurer.save_logs(log_info)
        return

    def exit(self):
        self.deap_configurer.force_stop()
        return