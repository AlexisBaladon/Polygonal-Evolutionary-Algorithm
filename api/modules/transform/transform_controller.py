import os
import random
from typing import Callable
import threading

from PIL import Image
from flask import Request, render_template
import socketio

from api.lib import sockets
from src.lib.deap_config import DeapConfig
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.models.evolutionary_algorithm.ea_methods import EA
from src.utils.image_processor import ImageProcessor
from src.utils.argument_checker import ArgumentChecker

def parse_value_signature(value, signature):
    try:
        value = signature(value)
        return value
    except:
        return None

def get_form_arguments(form):
    cpu_count = os.cpu_count()
    verbose = 1
    show = 0
    manual_console = 0

    seed = form.get("seed", 0)
    seed = parse_value_signature(seed, int)

    INDPB = form.get("INDPB", 0.1)
    INDPB = parse_value_signature(INDPB, float)
    CXPB = form.get("CXPB", 0.9)
    CXPB = parse_value_signature(CXPB, float)
    MUTPB = form.get("MUTPB", 0.1)
    MUTPB = parse_value_signature(MUTPB, float)

    NGEN = form.get("NGEN", 5)
    NGEN = parse_value_signature(NGEN, int)
    MU = form.get("MU", 50)
    MU = parse_value_signature(MU, int)
    LAMBDA = form.get("LAMBDA", 50)
    LAMBDA = parse_value_signature(LAMBDA, int)

    selection = form.get("selection", "best")
    tournament_size = form.get("tournament_size", 2)
    tournament_size = parse_value_signature(tournament_size, int)
    gaussian_rate = form.get("gaussian_rate", 0.05)
    gaussian_rate = parse_value_signature(gaussian_rate, float)

    width = form.get("width", None)
    width = parse_value_signature(width, int)
    height = form.get("height", None)
    height = parse_value_signature(height, int)
    vertex_count = form.get("vertex_count", None)
    vertex_count = parse_value_signature(vertex_count, int)

    tri_outline = None
    edge_rate = form.get("edge_rate", 0.5)
    edge_rate = parse_value_signature(edge_rate, float)

    return {
        "seed": seed,
        "INDPB": INDPB,
        "CXPB": CXPB,
        "MUTPB": MUTPB,
        "NGEN": NGEN,
        "MU": MU,
        "LAMBDA": LAMBDA,
        "selection": selection,
        "tournament_size": tournament_size,
        "gaussian_rate": gaussian_rate,
        "width": width,
        "height": height,
        "vertex_count": vertex_count,
        "cpu_count": cpu_count,
        "tri_outline": tri_outline,
        "edge_rate": edge_rate,
        "verbose": verbose,
        "show": show,
        "manual_console": manual_console
    }

def transform_image(args: dict, ea: EA, image_added_callback: Callable):
    dc = DeapConfig(**args)
    eac = EAHandler(ea, dc)
    eac.build_ea_module(**args)
    eac.build_deap_module()
    eac.run(image_added_callback=image_added_callback)
    return eac

def get_image_callback(ea: EA):
    def image_added_callback(images: list[Image.Image]):
        encoded_images = []

        for image in images:
            image = ea.decode(image)
            image = ea.image_processor.encode_image(image)
            encoded_images.append(image)
            
        sockets.emit('added_image', encoded_images)
        return
    
    return image_added_callback

# @socketio.on('disconnect')
# def handle_disconnect():

def transform(request: Request):
    image_file = request.files['image']
    
    if image_file is not None:
        try:
            argument_checker = ArgumentChecker()
            get_arguments = lambda: get_form_arguments(request.form)
            args = argument_checker.process_arguments(get_arguments=get_arguments)
            print(args)

            seed = args["seed"]
            random.seed(seed)

            image_data = image_file.read()
            decoded_image = ImageProcessor.decode_image(image_data)

            image_processor_args = {**args, 'input_image': decoded_image}
            image_processor = ImageProcessor(**image_processor_args)
            evolutionary_algorithm = EA(image_processor)

            image_added_callback = get_image_callback(evolutionary_algorithm)
            thread_args = (args, evolutionary_algorithm, image_added_callback)
            thread = threading.Thread(target=transform_image, args=thread_args) # Should i join?
            thread.start()

            return render_template('transform/transform_template.html')
        except Exception as e:
            return str(e.with_traceback())
    return "No image received :("