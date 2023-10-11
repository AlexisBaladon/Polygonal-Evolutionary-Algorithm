import sys
import os
import random
import base64
import io

from PIL import Image

from api import app
from src.models.evolutionary_algorithm.ea_methods import EA
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.lib.deap_config import DeapConfig
from src.utils.image_processor import ImageProcessor

def get_arguments() -> dict:
    mock_arguments = {"seed": 0,
                      "INDPB": 0.1,
                      "CXPB": 0.9,
                      "MUTPB": 0.1,
                      "NGEN": 1,
                      "MU": 50,
                      "LAMBDA": 50,
                      "selection": "best",
                      "tournament_size": 2,
                      "gaussian_rate": 0.05,
                      "input_path": "./data/inputs",
                      "input_name": "fox.jpg",
                      "output_path": "./data/outputs/executions",
                      "output_name": "polygonal_evolutionary_algorithm_result.png",
                      "width": 250,
                      "height": 250,
                      "vertex_count": None,
                      "cpu_count": 4,
                      "tri_outline": None,
                      "edge_rate": 0.5,
                      "verbose": 1,
                      "show": 0,
                      "manual_console": 0}

    return mock_arguments

def check_preconditions(args):
    # Check values' domain
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
    
    # Check directories
    if not os.path.isdir(args["input_path"]):
        raise Exception(f"Input path {args['input_path']} does not exist")
    if not os.path.isfile(os.path.join(args["input_path"], args["input_name"])):
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
    eac = EAHandler(ea, dc)
    eac.build_ea_module(**args)
    eac.build_deap_module()
    return eac

DeapConfig.register_fitness() #DEAP CONFIGURATION MUST BE OUTSIDE OF MAIN WHEN USING PARALLELISM

@app.route("/")
def index():
    args = process_arguments()
    seed = args["seed"]; random.seed(seed)
    eac = main(args)
    eac.run()
    saved_image = Image.open(eac.evolutionary_algorithm.image_processor.img_out_dir)
    # get base64 image
    img_byte_arr = io.BytesIO()
    saved_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    base64_image = base64.b64encode(img_byte_arr)
    base64_utf8_image = base64_image.decode("utf-8")
    return f"<img src='data:image/png;base64,{base64_utf8_image}' width='250px'>"

if __name__ == "__main__":
    app.run(debug=True)