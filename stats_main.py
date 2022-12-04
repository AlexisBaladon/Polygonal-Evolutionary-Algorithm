from Statistics import Statistics
from DeapConfig import DeapConfig
from AltSolver import AltSolver
from EAController import EAController
from ImageProcessor import ImageProcessor
from EA import EA

"""
     dc = DeapConfig(NGEN=NGEN)
     ip = ImageProcessor(IMAGE_NAME, vertex_count=VERTEX_COUNT)
     ea = EA(ip)
     eac = EAController(ea, dc)
     eac.build_ea_module()
     eac.build_deap_module()
     alts = AltSolver(eac.evolutionary_algorithm)

     stats = Statistics(eac, alts)
     stats.parametric_evaluation()
     stats.parametric_evaluation()
     stats.greedy_evaluation()

     #una vez se tenga la configuracion optima
     stats.informal_evaluation()
     stats.efficiency_evaluation()   
"""

DeapConfig.register_fitness() # register fitness outside main

if __name__  == "__main__":        
    IMAGE_RESULT_PATH = "img/"
    SEED_NUMBER = 2
    stateless_stats = Statistics(None, None)

    #PARAMETRIC
    CONFIG_SEEDS = list(range(500, 500 + SEED_NUMBER))
    CONFIG_IMAGES = ["ultima_cena.jpg"]
    FORMAL_VERTEX_COUNT = 5000
    FORMAL_ATTRIBUTES = {"CXPB": [0.8, 0.9], "MUTPB": [0.01, 0.05, 0.1]}
    #stateless_stats.parametric_evaluation2(FORMAL_VERTEX_COUNT, FORMAL_ATTRIBUTES, IMAGE_RESULT_PATH, CONFIG_IMAGES, seeds=CONFIG_SEEDS)

    #INFORMAL
    best_config = {"CXPB":0.9, "MUTPB":0.1}
    INFORMAL_ATTRIBUTES = {"tournament_size": [2,3]} #TODO: TOURNAMENT HARDCODEADO
    INFORMAL_VERTEX_COUNT = 5000
    INFORMAL_IMAGE = CONFIG_IMAGES[0]
    #stateless_stats.informal_evaluation_2(best_config, INFORMAL_VERTEX_COUNT, INFORMAL_ATTRIBUTES, IMAGE_RESULT_PATH, INFORMAL_IMAGE, seeds=CONFIG_SEEDS)
    
    #GREEDY
    GREEDY_CONFIG = {
        "local_search": {"max_iter": 100000, "threshold": 3, "max_time": 1},
        "gaussian": {"max_iter": 100000, "threshold": 50, "max_time": 1}
    }
    GREEDY_SEEDS = list(range(1000, 1000 + SEED_NUMBER))
    IMAGES = {
        "fox.jpg": {
            "vertex_count": 2500,
        },
        "monalisa.jpg": {
            "vertex_count": 5000,
        },
        "old_man.jpeg": {
            "vertex_count": 6000,
        },
    }
    stateless_stats.greedy_evaluation_2(best_config, GREEDY_CONFIG, IMAGE_RESULT_PATH, IMAGES, seeds=GREEDY_SEEDS)
