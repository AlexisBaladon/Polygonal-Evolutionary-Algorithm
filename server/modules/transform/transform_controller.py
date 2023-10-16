import os
import random
from flask import Request, request, render_template

from src.utils.image_processor import ImageProcessor
from src.utils.argument_checker import ArgumentChecker
from server.lib.sockets import socketio
from server import config
from server.lib.celery.tasks import transform_image

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
    NGEN = None if NGEN is None else min(NGEN, 15) # NGEN > 10 would cause the system to overload

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
    vertex_count = None if vertex_count is None else min(vertex_count, 10_000) # vertex_count > 10_000 would cause the system to overload

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


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

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

            image_processor_args = {**args, 'input_image': image_data}
            transform_image.delay(image_processor_args, args)

            context = {**args, 
                       'width': decoded_image.width,
                       'height': decoded_image.height,
                       'input_image': base64_image}
            return render_template('transform/transform_template.html', **context)
        except Exception as e:
            return str(e.with_traceback())
    return "No image received :("