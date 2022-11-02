import ImageProcessor
import DeapConfig

class AE:
    def __init__(self, img_p, deap_c):
        self.image_processor = img_p
        self.deap_configurer = deap_c

    def buildImageModule(self):
        self.image_processor.read_image()


    def buildDeapModule(self):
        self.deap_configurer.register_individual_type()
        self.deap_configurer.register_fitness()
        self.deap_configurer.register_population()
        self.deap_configurer.register_operators(self.image_processor.evalDelaunay)
        self.deap_configurer.register_stats()
        self.deap_configurer.register_parallelism()
        
    def run(self):
        self.buildImageModule()
        self.buildDeapModule()

        #algo
        self.deap_configurer.run_algorithm()

        return


if __name__ == "__main__":
    img_p = ImageProcessor.ImageProcessor()
    deap_c = DeapConfig.DeapConfig()
    ae = AE(img_p, deap_c)
    ae.run()