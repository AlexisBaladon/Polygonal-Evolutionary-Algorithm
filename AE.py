from ImageProcessor import ImageProcessor
from DeapConfig import DeapConfig

class AE:
    def __init__(self, img_p: ImageProcessor, deap_c: DeapConfig):
        self.image_processor = img_p
        self.deap_configurer = deap_c

    def buildImageModule(self):
        self.image_processor.read_image()


    def buildDeapModule(self):
        self.deap_configurer.register_fitness()
        self.deap_configurer.register_population(self.image_processor.width - 1, self.image_processor.height - 1)
        self.deap_configurer.register_operators(self.image_processor.evalDelaunay)
        self.deap_configurer.register_stats()
        self.deap_configurer.register_seed()
        #self.deap_configurer.register_parallelism()
        
    def run(self):
        self.buildImageModule()
        self.buildDeapModule()

        #algo
        self.deap_configurer.run_algorithm(logs=True)

        return


if __name__ == "__main__":
    img_p = ImageProcessor()
    deap_c = DeapConfig()
    ae = AE(img_p, deap_c)
    ae.run()