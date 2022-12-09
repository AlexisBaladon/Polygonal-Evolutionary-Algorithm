import argparse
import sys
import os
from EA import EA
from EAController import EAController
from DeapConfig import DeapConfig
from ImageProcessor import ImageProcessor

from threading import Thread
import random

def get_arguments() -> dict:
    parser = argparse.ArgumentParser()
    #DEAP CONFIGURATION
    parser.add_argument("--seed", type=int, default=64, help="Seed")
    parser.add_argument("--INDPB", type=float, default=0.1, help="Probability of mutating a gene")
    parser.add_argument("--CXPB", type=float, default=0.9, help="Crossover probability")
    parser.add_argument("--MUTPB", type=float, default=0.1, help="Mutation probability")
    parser.add_argument("--NGEN", type=int, default=100, help="Number of generations")
    parser.add_argument("--MU", type=int, default=50, help="Population size")
    parser.add_argument("--LAMBDA", type=int, default=50, help="Number of children to produce at each generation")
    parser.add_argument("--selection", type=str, default="best", help="Selection method (best, roulette, tournament)")
    parser.add_argument("--tournament_size", type=int, default=3, help="Tournament size")
    parser.add_argument("--gaussian_rate", type=float, default=0.05, help="Gaussian rate. Multiplied by the max value of the mutated gene (coordinate)")
    #IMAGE PROCESSING
    parser.add_argument("--input_path", type=str, default="./img", help=f"")
    parser.add_argument("--input_name", type=str, default="monalisa.jpg", required=True, help=f"")
    parser.add_argument("--output_path", type=str, default="./", help=f"")
    parser.add_argument("--output_name", type=str, default="monalisa.jpg", help=f"")
    parser.add_argument("--width", type=int, default=None, help="Maximum width")
    parser.add_argument("--height", type=int, default=None, help="Maximum height")
    #DELAUNAY
    parser.add_argument("--vertex_count", type=int, default=None, help=f"Number of vertices")
    parser.add_argument("--cpu_count", type=int, default=1, help="Number of CPUs to use")
    parser.add_argument("--tri_outline", type=int, default=None, help=f"Color of triangle outline")
    parser.add_argument("--edge_rate", type=float, default=0.5, help=f"Number of edges in initialized individual")
    #CONSOLE
    parser.add_argument("--verbose", type=int, default=1, help=f"Prints information to console")
    parser.add_argument("--show", type=int, default=0, help=f"Show images")
    parser.add_argument("--manual_console", type=int, default=0, help=f"allow to write commands while the algorithm is running (exit)")
    return vars(parser.parse_args())

def check_preconditions(args):
    #Check domain
    if args["width"] is not None and args["width"] <= 0:
        raise Exception("Width must be greater than 0")
    if args["height"] is not None and args["height"] <= 0:
        raise Exception("Height must be greater than 0")
    if args["vertex_count"] is not None and args["vertex_count"] < 5:
        raise Exception("Vertex count must be greater than 4")
    if args["cpu_count"] < 1:
        raise Exception("CPU count must be greater than 0")
    if args["edge_rate"] < 0 or args["edge_rate"] > 1:
        raise Exception("Edge rate must be between 0 and 1")
    if args["manual_console"] != 0 and args["manual_console"] != 1:
        raise Exception("manual_console is a boolean value")
    if args["verbose"] != 0 and args["verbose"] != 1:
        raise Exception("verbose is a boolean value")
    if args["show"] != 0 and args["show"] != 1:
        raise Exception("show is a boolean value")
    if args["selection"] not in ["best", "tournament"]:
        raise Exception("Selection method must be one of the following: best, tournament")
    if args["selection"] == "tournament" and args["tournament_size"] < 1:
        raise Exception("Tournament size must be greater than 0")
    
    #Check directories
    if not os.path.isdir(args["input_path"]):
        raise Exception(f"Input path {args['input_path']} does not exist")
    if not os.path.isfile(args["input_path"] + "/" + args["input_name"]):
        raise Exception(f"Input file {args['input_name']} does not exist in {args['input_path']}")
    if not os.path.isdir(args["output_path"]):
        raise Exception("Output path does not exist")
    return args

def process_arguments():
    try:
        args = get_arguments()
        args = check_preconditions(args)
    except Exception as e:
        print(str(e))
        sys.exit(1)
    return args

def main(args):
    dc = DeapConfig(**args)
    ip = ImageProcessor(**args)
    ea = EA(ip)
    eac = EAController(ea, dc)
    eac.build_ea_module(**args)
    eac.build_deap_module()
    return eac

def handle_inputs(algorithm_thread: Thread, eac: EAController):
    while True:
        usr_input = input()
        if not algorithm_thread.is_alive():
            print("Algorithm finished")
            break
        if usr_input == "exit":
            eac.exit()
            print("Waiting for next generation to finish before exiting...")
            break

DeapConfig.register_fitness() #DEAP CONFIGURATION MUST BE OUTSIDE OF MAIN WHEN USING PARALLELISM

#py main.py --input_name womhd.jpg --vertex_count 10000 --cpu_count 4 --manual_console 1 --width 500 --height 500 --output_name Bart.jpg
if __name__ == "__main__":
    args = process_arguments()
    random.seed(args["seed"])
    eac = main(args)
    if args["manual_console"] == 1:
        algorithm_thread = Thread(target=eac.run, args=())
        algorithm_thread.start()
        handle_inputs(algorithm_thread, eac)
        algorithm_thread.join()
    else:
        eac.run()
