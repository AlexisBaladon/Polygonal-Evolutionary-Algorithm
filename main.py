import argparse
import sys

from AE import AE
from DeapConfig import DeapConfig
from ImageProcessor import ImageProcessor

def get_arguments() -> dict:
    parser = argparse.ArgumentParser()

    #DEAP CONFIGURATION
    parser.add_argument("--INDPB", type=float, default=0.1, help="Individual probability")
    parser.add_argument("--CXPB", type=float, default=0.8, help="Crossover probability")
    parser.add_argument("--MUTPB", type=float, default=0.2, help="Mutation probability")
    parser.add_argument("--NGEN", type=int, default=100, help="Number of generations")
    parser.add_argument("--MU", type=int, default=50, help="Population size")
    parser.add_argument("--LAMBDA", type=int, default=50, help="Number of children to produce at each generation")
    parser.add_argument("--seed", type=int, default=64, help="Seed")

    #IMAGE PROCESSING
    parser.add_argument("--input_path", type=str, default="./img", help=f"")
    parser.add_argument("--input_name", type=str, default="monalisa.jpg", required=True, help=f"")
    parser.add_argument("--output_path", type=str, default="./", help=f"")
    parser.add_argument("--output_name", type=str, default="monalisa.jpg", help=f"")
    parser.add_argument("--width", type=int, default=None, help="Maximum width")
    parser.add_argument("--height", type=int, default=None, help="Maximum height")

    #DELAUNAY
    parser.add_argument("--vertex_count", type=int, default=50, required=True, help=f"")
    parser.add_argument("--cpu_count", type=int, default=1, help="Number of CPUs to use")

    args = vars(parser.parse_args())
    return args

def check_preconditions(args):
    if args["width"] is not None and args["width"] < 0:
        raise Exception("Invalid image width")
    if args["height"] is not None and args["height"] < 0:
        raise Exception("Invalid image height")
    if args["vertex_count"] < 5:
        raise Exception("Invalid vertex count")
    if args["cpu_count"] < 1:
        raise Exception("Invalid CPU count")

    #TODO: Check if input file exists
    #TODO: Check if output file exists
    #TODO: Check if output path exists
    #TODO: Check if input path exists
    #TODO: Check if input file is an image
    
    #Variable renaming
    args["ind_size"] = args["vertex_count"] * 2
    return args

def main():
    #command example
    #py main.py --input_name Bart.jpg --vertex_count 50 
    try:
        args = get_arguments()
        args = check_preconditions(args)
    except Exception as e:
        print(e.with_traceback()) #Remove traceback in production
        sys.exit(1)

    dc = DeapConfig(**args)
    ip = ImageProcessor(**args)
    ae = AE(ip,dc)
    ae.run()
    return

if __name__ == "__main__":
    main()