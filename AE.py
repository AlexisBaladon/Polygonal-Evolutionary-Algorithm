from ImageProcessor import ImageProcessor
from DeapConfig import DeapConfig

class AE:
    def __init__(self, img_p: ImageProcessor, deap_c: DeapConfig):
        self.image_processor = img_p
        self.deap_configurer = deap_c

    def buildImageModule(self):
        self.image_processor.read_image()

    def buildDeapModule(self):
        #self.deap_configurer.register_fitness() ONLY RUN OUTSIDE MAIN
        self.deap_configurer.register_population(self.image_processor.width - 1, self.image_processor.height - 1, 
                                                 self.image_processor.edges_coordinates)
        self.deap_configurer.register_operators(self.image_processor.evalDelaunay)
        self.deap_configurer.register_stats()
        self.deap_configurer.register_seed()
        self.deap_configurer.register_parallelism() #ONLY RUN INSIDE MAIN
        
    def run(self):
        self.deap_configurer.run_algorithm(logs=True, image_processor=self.image_processor)
        return