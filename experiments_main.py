import os

from src.evaluation.statistics import Statistics
from src.lib.deap_config import DeapConfig

DeapConfig.register_fitness() # Register fitness must be outside main

if __name__  == "__main__":        
    IMAGE_RESULT_PATH = os.path.join('data', 'inputs')
    SEED_NUMBER = 30
    stats = Statistics()

    # Parametric
    CONFIG_SEEDS = list(range(500, 500 + SEED_NUMBER))
    CONFIG_IMAGES = ["ultima_cena.jpg"]
    FORMAL_VERTEX_COUNT = 5000
    FORMAL_ATTRIBUTES = {"CXPB": [0.8, 0.9], "MUTPB": [0.01, 0.05, 0.1]}
    stats.parametric_evaluation(FORMAL_VERTEX_COUNT, FORMAL_ATTRIBUTES, 
                                IMAGE_RESULT_PATH, CONFIG_IMAGES, 
                                seeds=CONFIG_SEEDS)

    # Informal
    best_config = {"CXPB":0.9, "MUTPB":0.1}
    INFORMAL_ATTRIBUTES = {"tournament_size": [2,3]}
    INFORMAL_VERTEX_COUNT = 5000
    INFORMAL_IMAGE = CONFIG_IMAGES[0]
    stats.informal_evaluation(best_config, INFORMAL_VERTEX_COUNT, 
                              INFORMAL_ATTRIBUTES, IMAGE_RESULT_PATH, 
                              INFORMAL_IMAGE, seeds=CONFIG_SEEDS)
    
    # Comparison
    LAMBDA = 50
    NGEN = 100
    EVALS = LAMBDA * NGEN
    COMPARISON_CONFIG = {
        "local_search": {"max_iter": 100000, "threshold": 3, "max_evals": EVALS},
        "gaussian": {"max_iter": 100000, "threshold": 50, "max_evals": EVALS}
    }
    COMPARISON_SEEDS = list(range(1000, 1000 + SEED_NUMBER))
    IMAGES = {
        "fox.jpg": {
            "vertex_count": 1500,
            "width": 300,
        },
        "monalisa_sqr.jpg": {
            "vertex_count": 2000,
            "width": 400,
        },
        "old_man.jpeg": {
            "vertex_count": 3000,
            "width": 300,
        },
    }
    stats.comparison_evaluation(best_config, COMPARISON_CONFIG, 
                                IMAGE_RESULT_PATH, IMAGES, 
                                seeds=COMPARISON_SEEDS)

    # Efficiency
    stats.efficiency_evaluation(seed=0, images= IMAGES, 
                                image_path=IMAGE_RESULT_PATH)
