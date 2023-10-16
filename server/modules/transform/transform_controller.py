import os
import random
from typing import Callable

from flask import request

from server.lib import sockets
from src.lib.deap_config import DeapConfig
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.models.evolutionary_algorithm.ea_methods import EA
from src.utils.image_processor import ImageProcessor
from src.utils.argument_checker import ArgumentChecker
from server.lib.sockets import socketio
from server import config

def parse_value_signature(value, signature):
    try:
        value = signature(value)
        return value
    except:
        return None

def get_form_arguments(form):
    cpu_count = 1 if config.production else os.cpu_count()
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
    NGEN = None if NGEN is None else min(NGEN, 100) # NGEN > 100 would cause the system to overload

    MU = form.get("MU", 50)
    MU = parse_value_signature(MU, int)
    MU = None if MU is None else min(MU, 100) # MU > 100 would cause the system to overload

    LAMBDA = form.get("LAMBDA", 50)
    LAMBDA = parse_value_signature(LAMBDA, int)
    LAMBDA = None if LAMBDA is None else min(LAMBDA, 100) # LAMBDA > 100 would cause the system to overload

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
    vertex_count = None if vertex_count is None else min(vertex_count, 20_000) # vertex_count > 20_000 would cause the system to overload

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

import collections

client_eac = {}
client_responses = collections.defaultdict(collections.deque)

def get_image_callback(ea: EA):
    def image_added_callback(individuals_data: dict):
        encoded_images = {"images": [], "fitness": individuals_data["fitness"]}
        images = individuals_data["population"]

        for image in images:
            image = ea.decode(image)
            image = ea.image_processor.encode_image(image)
            encoded_images["images"].append(image)
            
        print("added image")
        #sockets.emit('added_image', encoded_images)
        client_responses[request.remote_addr].append(encoded_images)
        return
    
    return image_added_callback

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    if request.remote_addr in client_eac:
        try:
            client_eac[request.remote_addr].exit()
        except:
            pass

@socketio.on('process_transformation_parameters')
def transform(form_data):
    try:
        image_base64 = form_data['image']

        argument_checker = ArgumentChecker()
        get_arguments = lambda: get_form_arguments(form_data)
        args = argument_checker.process_arguments(get_arguments=get_arguments)

        seed = args["seed"]
        random.seed(seed)

        decoded_image = ImageProcessor.decode_image(image_base64)
        base64_image = ImageProcessor.encode_image(decoded_image)

        image_processor_args = {**args, 'input_image': decoded_image}
        image_processor = ImageProcessor(**image_processor_args)
        evolutionary_algorithm = EA(image_processor)

        context = {**args, 
                    'width': decoded_image.width,
                    'height': decoded_image.height,
                    'input_image': base64_image}
        
        client_eac[request.remote_addr] = (context, evolutionary_algorithm)
        
    except Exception as e:
        print("Something wrong happened while initializing the EA", e.with_traceback())
        socketio.emit('error', "Something wrong happened while initializing the EA")

@socketio.on('start_sending_images')
def start_sending_images():
    try:
        context, evolutionary_algorithm = client_eac.pop(request.remote_addr)
        image_added_callback = get_image_callback(evolutionary_algorithm)
        dc = DeapConfig(**context)
        eac = EAHandler(evolutionary_algorithm, dc)
        eac.build_ea_module(**context)
        eac.build_deap_module()
        client_eac[request.remote_addr] = eac
        eac.run(image_added_callback=image_added_callback, save=False)
    except Exception as e:
        print("Something wrong happened while initializing the EA; ", e)