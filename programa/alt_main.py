import argparse
import sys
import os
from EA import EA
from ImageProcessor import ImageProcessor
from AltSolver import AltSolver

def get_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0, help="Seed for random number generator")
    #IMAGE PROCESSING
    parser.add_argument("--input_path", type=str, default="./img", help=f"")
    parser.add_argument("--input_name", type=str, default="fox.jpg", required=True, help=f"")
    parser.add_argument("--output_path", type=str, default="./", help=f"")
    parser.add_argument("--output_name", type=str, default="monalisa.jpg", help=f"")
    parser.add_argument("--width", type=int, default=None, help="Maximum width")
    parser.add_argument("--height", type=int, default=None, help="Maximum height")
    #DELAUNAY
    parser.add_argument("--vertex_count", type=int, default=50, required=True, help=f"Number of vertex")
    parser.add_argument("--tri_outline", type=int, default=None, help=f"Color of triangle outline")
    #METHOD
    parser.add_argument("--method", type=str, default="gaussian", help=f"gaussian or local_search")
    parser.add_argument("--threshold", type=int, default=5, help=f"Threshold for local search or standard deviation for gaussian")
    parser.add_argument("--max_iter", type=int, default=100, help=f"Maximum number of iterations")
    parser.add_argument("--max_evals", type=int, default=100, help=f"Maximum number of evaluations")
    parser.add_argument("--verbose", type=int, default=1, help=f"Prints information about the process")
    return vars(parser.parse_args())

def check_preconditions(args):
    #Chek domains
    if args["width"] is not None and args["width"] < 0:
        raise Exception("Invalid image width")
    if args["height"] is not None and args["height"] < 0:
        raise Exception("Invalid image height")
    if args["vertex_count"] < 5:
        raise Exception("Invalid vertex count, must be at least 5")
    if args["method"] not in ["gaussian", "local_search"]:
        raise Exception("Invalid method. Try (gaussian or local_search)")
    if args["threshold"] < 1:
        raise Exception("Threshold must be at least 1")
    if args["max_iter"] < 1:
        raise Exception("Max iter must be at least 1")
    if args["max_evals"] < 1:
        raise Exception("Max evals must be at least 1")
    if args["verbose"] not in [0, 1]:
        raise Exception("Verbose must be 0 or 1")

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

#command example
#py alt_main.py --input_name womhd.jpg --vertex_count 200 --width 250 --height 250 --method gaussian --threshold 100 --max_iter 1000
def main(args):
    ip = ImageProcessor(**args)
    ea = EA(ip)
    alt_solver = AltSolver(ea)
    alt_solver.build_ea_module()
    alt_solver.update_seed(args["seed"])
    method, max_iter, threshold, max_evals, verbose = args["method"], args["max_iter"], args["threshold"], args["max_evals"], args["verbose"]
    best_individual, _ = alt_solver.solve(method, max_iter, threshold, max_evals, verbose= verbose)
    img = ea.decode(best_individual)
    img.show()

if __name__ == "__main__":
    args = process_arguments()
    main(args)