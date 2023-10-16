import os
import time
import random
from typing import Callable
import collections
import threading

from flask import Request, render_template

from src.lib.deap_config import DeapConfig
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.models.evolutionary_algorithm.ea_methods import EA
from src.utils.image_processor import ImageProcessor
from src.utils.argument_checker import ArgumentChecker
from server import config, g, UserContext, app

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

def get_image_callback(ea: EA, user_id: str):
    def image_added_callback(individuals_data: dict):
        encoded_images = {"images": [], "fitness": individuals_data["fitness"]}
        images = individuals_data["population"]

        for image in images:
            image = ea.decode(image)
            image = ea.image_processor.encode_image(image)
            encoded_images["images"].append(image)

        with app.app_context():
            user_context: UserContext = getattr(g, user_id, None)
            if user_context is None:
                raise Exception("User context not found")
            
            user_context.encoded_images.append(encoded_images) # TODO: THREAD SAFE
            setattr(g, user_id, user_context)
        
        return
    
    return image_added_callback

def get_user_id(request: Request):
    return request.remote_addr

def get_next_generation(request: Request):
    try:
        user_id = get_user_id(request)

        with app.app_context():
            user_context: UserContext = getattr(g, user_id, None)
            if user_context is None:
                raise Exception("User context not found")
            
            while len(user_context.encoded_images) == 0:
                time.sleep(1)

            encoded_images = user_context.encoded_images.pop(0)

        return encoded_images
    except Exception as e:
        print("Something wrong happened while getting the next generation; ", e)
        return str(e)
    
def run_ea(eac: EAHandler, args: tuple):
    with app.app_context():
        eac.run(*args)

def transform_image(request: Request):
    try:
        with app.app_context():
            user_id = get_user_id(request)
            user_context: UserContext = getattr(g, user_id, None)
            if user_context is None:
                raise Exception("User context not found")
            
            args = user_context.args
            if args is None:
                raise Exception("Arguments not found")
            
            decoded_image = user_context.decoded_image
            if decoded_image is None:
                raise Exception("Input image not found")

            image_processor_args = {**args, 'input_image': decoded_image}
            image_processor = ImageProcessor(**image_processor_args)
            evolutionary_algorithm = EA(image_processor)

            user_id = get_user_id(request)
            image_added_callback = get_image_callback(evolutionary_algorithm, user_id)
            
            deap_config = DeapConfig(**args)
            eac = EAHandler(evolutionary_algorithm, deap_config)
            eac.build_ea_module(**args)
            eac.build_deap_module()

            # user_context.user_eac = eac
            # setattr(g, user_id, user_context)

            eac_args = (image_added_callback, False, False, 0, False)
            # thread_args = (eac, eac_args)
            # thread = threading.Thread(target=eac.run, args=thread_args)
            # thread.start()

            eac.run(*eac_args)

        return "ok"
    except Exception as e:
        print("Something wrong happened while initializing the EA; ", e.with_traceback())
        return str(e)

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
            base64_image = ImageProcessor.encode_image(decoded_image)

            user_id = get_user_id(request)

            with app.app_context():
                user_context = getattr(g, user_id, None)
                if user_context is None:
                    user_context = UserContext(args=args, decoded_image=decoded_image)
                    setattr(g, user_id, user_context)

            thread_args = (request,)
            thread = threading.Thread(target=transform_image, args=thread_args)
            thread.start()

            context = {**args, 
                       'width': decoded_image.width,
                       'height': decoded_image.height,
                       'input_image': base64_image}
            return render_template('transform/transform_template.html', **context)
        except Exception as e:
            return str(e.with_traceback())
    return "No image received :("