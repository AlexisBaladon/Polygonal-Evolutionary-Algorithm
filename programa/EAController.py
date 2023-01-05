from EA import EA
from DeapConfig import DeapConfig

class EAController:
    def __init__(self, ea: EA, deap_c: DeapConfig):
        self.evolutionary_algorithm = ea
        self.deap_configurer = deap_c

    def build_ea_module(self, verbose=True, show=False, **kwargs):
        self.evolutionary_algorithm.load_image(verbose=verbose, show=show)

    #FITNESS MUST BE REGISTERED OUTSIDE OF MAIN WHEN USING PARALLELISM
    def build_deap_module(self):
        ea, ip, dc = self.evolutionary_algorithm, self.evolutionary_algorithm.image_processor, self.deap_configurer
        width, height = ip.width, ip.height
        edges_coordinates = ip.edges_coordinates
        ind_size = ip.vertex_count * 2
        fitness_function, mutation_function = ea.evalDelaunay, ea.mutGaussianCoordinate
        init_coordinates = lambda edge_rate: ea.init_coordinates(width-1, height-1, ind_size, edges_coordinates, edge_rate=edge_rate)
        dc.register_population(init_coordinates, ea.order_individual)
        dc.register_operators(fitness_function, mutation_function, width-1, height-1)
        dc.register_stats()
        if dc.cpu_count > 1:
            dc.register_parallelism() 
        
    def run(self, show_res=True, logs=True, seed=0):
        is_parallel = bool(self.deap_configurer.cpu_count > 1)
        population, log_info, hall_of_fame, best_fitnesses = self.deap_configurer.run_algorithm(parallel=is_parallel)

        # Save files
        img = self.evolutionary_algorithm.decode(population[0])
        img.save(self.evolutionary_algorithm.image_processor.img_out_dir)

        if show_res:
            img.show("Result")
        if logs:
            self.deap_configurer.save_logs(
                log_info, 
                seed=seed,
                file_name=self.evolutionary_algorithm.image_processor.input_name,
                hall_of_fame=hall_of_fame)
        return best_fitnesses

    def exit(self):
        self.deap_configurer.force_stop()
        return
