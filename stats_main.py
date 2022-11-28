from main import main

if __name__  == "__main__":
    parameters = {
        "input_path": "input",
        "input_name": "womhd.jpg",
        "output_path": "output",
        "output_name": "delaunay.jpg",
    }

    main(**parameters)

            
    # Statistics(eac).parametric_evaluation()
    # Statistics(eac).algorithmical_speedup()    
    
    # alt_solver = AltSolver(eac.evolutionary_algorithm)
    # alt_solver.build_ea_module()
    # Statistics(eac, alt_solver).greedy_evaluation()

    # alt_solver = AltSolver(eac.evolutionary_algorithm)
    # alt_solver.build_ea_module()
    # Statistics(eac, alt_solver).informal_evaluation({"CXPB":0.8, "MUTPB":0.01})