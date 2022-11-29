from Statistics import Statistics
from DeapConfig import DeapConfig

DeapConfig.register_fitness() # register fitness outside main

if __name__  == "__main__":        
    IMAGE_RESULT_PATH = "img/"
    SEED_NUMBER = 2

    # Statistics(eac).parametric_evaluation()
    # Statistics(eac).algorithmical_speedup()    
    
    # alt_solver = AltSolver(eac.evolutionary_algorithm)
    # alt_solver.build_ea_module()
    # Statistics(eac, alt_solver).greedy_evaluation()

    # alt_solver = AltSolver(eac.evolutionary_algorithm)
    # alt_solver.build_ea_module()
    # Statistics(eac, alt_solver).informal_evaluation({"CXPB":0.8, "MUTPB":0.01})

    SEEDS = list(range(500, 500 + SEED_NUMBER))
    IMAGE_NAME = "ultima_cena.jpg" #VARIAR
    stateless_stats = Statistics(None, None)

    #PARAMETRIC
    FORMAL_VERTEX_COUNT = 100
    FORMAL_ATTRIBUTES = {#"CXPB": [0.8], "MUTPB": [0.01]} #{
        "CXPB": [0.8, 0.9], "MUTPB": [0.01, 0.05, 0.1]}
    #stateless_stats.parametric_evaluation2(FORMAL_VERTEX_COUNT, FORMAL_ATTRIBUTES, IMAGE_RESULT_PATH, IMAGE_NAME, seeds=SEEDS)

    #INFORMAL
    best_config = {"CXPB":0.8, "MUTPB":0.01} #TODO: obtenerla de la evaluación formal
    INFORMAL_ATTRIBUTES = {"MU": [50], "selection": ["best"]} #{"MU": [50, 100], "selection": ["best", "tournament", "roulette"]}
    INFORMAL_VERTEX_COUNT = 100
    #stateless_stats.informal_evaluation_2(best_config, INFORMAL_VERTEX_COUNT, INFORMAL_ATTRIBUTES, IMAGE_RESULT_PATH, IMAGE_NAME, seeds=SEEDS)

    #GREEDY
    GREEDY_CONFIG = {
        "local_search": {"max_iter": 5, "threshold": 3},
        "gaussian": {"max_iter": 5, "threshold": 50}
    }
    #stateless_stats.greedy_evaluation_2(best_config, GREEDY_CONFIG, FORMAL_VERTEX_COUNT, IMAGE_RESULT_PATH, IMAGE_NAME, seeds=SEEDS)

    #FRIEDMAN RANKING
    CSV_PATH = "results/greedy.csv"
    METHOD_COLUMN = "method"
    FITNESS_COLUMN = "best_historical_fitness"
    #stateless_stats.friedman_test(CSV_PATH, METHOD_COLUMN, FITNESS_COLUMN)
    stateless_stats.range_test()