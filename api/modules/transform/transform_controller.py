import base64
import os
import io
import random

from PIL import Image
from flask import Request

from src.lib.deap_config import DeapConfig
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.models.evolutionary_algorithm.ea_methods import EA
from src.utils.image_processor import ImageProcessor

def get_arguments() -> dict:
    mock_arguments = {"seed": 0,
                      "INDPB": 0.1,
                      "CXPB": 0.9,
                      "MUTPB": 0.1,
                      "NGEN": 5,
                      "MU": 50,
                      "LAMBDA": 50,
                      "selection": "best",
                      "tournament_size": 2,
                      "gaussian_rate": 0.05,
                      "input_path": "./data/inputs",
                      "input_name": "input.png",
                      "output_path": "./data/outputs/executions",
                      "output_name": "polygonal_evolutionary_algorithm_result.png",
                      "width": None,
                      "height": None,
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
    if not os.path.isdir(args["output_path"]):
        raise Exception("Output path does not exist")
    return args

def process_arguments():
    try:
        args = get_arguments()
        args = check_preconditions(args)
    except Exception as e:
        print(str(e))
    return args

def save_image(image: Image.Image, dir: str):
    image.save(dir)

def transform_image(args):
    seed = args["seed"]; random.seed(seed)
    dc = DeapConfig(**args)
    ip = ImageProcessor(**args)
    ea = EA(ip)
    eac = EAHandler(ea, dc)
    eac.build_ea_module(**args)
    eac.build_deap_module()
    eac.run()
    return eac

def get_image(image_save_dir: str):
    image = Image.open(image_save_dir)
    return image

def encode_image(image: Image.Image):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_base64

def decode_image(image_data: bytes):
    image = Image.open(io.BytesIO(image_data))
    return image

def transform(request: Request):
    image_file = request.files['image']

    if image_file is not None:
        try:
            image_data = image_file.read()
            decoded_image = decode_image(image_data)
            args = process_arguments()
            input_dir = os.path.join(args["input_path"], args["input_name"])
            save_image(decoded_image, input_dir)
            eac = transform_image(args)
            image = get_image(eac.evolutionary_algorithm.image_processor.img_out_dir)
            image_base64 = encode_image(image)
            img_tag = f"<img src='data:image/{image_file.content_type};base64,{image_base64}' width='250px'>"
            return img_tag
        except Exception as e:
            return str(e)
    return "No image received :("