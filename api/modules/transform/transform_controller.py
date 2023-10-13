import os
import random
from typing import Callable

from PIL import Image
from flask import Request

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
    input_path = "./data/inputs"
    input_name = "input.png"
    output_path = "./data/outputs/executions"
    output_name = "polygonal_evolutionary_algorithm_result.png"
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
        "input_path": input_path,
        "input_name": input_name,
        "output_path": output_path,
        "output_name": output_name,
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

def transform_image(args: dict, image_added_callback: Callable):
    dc = DeapConfig(**args)
    ip = ImageProcessor(**args)
    ea = EA(ip)
    eac = EAHandler(ea, dc)
    eac.build_ea_module(**args)
    eac.build_deap_module()
    eac.run(image_added_callback=image_added_callback)
    return eac

def transform(request: Request):
    image_file = request.files['image']

    if image_file is not None:
        try:
            argument_checker = ArgumentChecker()
            image_data = image_file.read()
            get_arguments = lambda: get_form_arguments(request.form)
            args = argument_checker.process_arguments(get_arguments=get_arguments)
            print(args)

            input_dir = os.path.join(args["input_path"], args["input_name"])
            seed = args["seed"]; random.seed(seed)

            image_processor = ImageProcessor(**args)
            evolutionary_algorithm = EA(image_processor)

            evolutionary_algorithm.load_image()
            decoded_image = image_processor.decode_image(image_data)
            decoded_image.save(input_dir)

            image = Image.open(image_processor.img_out_dir)
            image_base64 = image_processor.encode_image(image)
            sockets.emit('added_image', image_base64)

            def image_added_callback(image):
                image = evolutionary_algorithm.decode(image)
                image = image_processor.encode_image(image)
                sockets.emit('added_image', image)
                return

            import threading
            t = threading.Thread(target=transform_image, args=(args, image_added_callback))
            t.start()

            #img_tag = f"<img src='data:image/{image_file.content_type};base64,{image_base64}' width='250px'>"
            img_tag = create_response()
            return img_tag
        except Exception as e:
            return str(e.with_traceback())
    return "No image received :("

def create_response():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Processing</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.2.0/socket.io.js"></script>
        <script type="text/javascript">
            var socket = io.connect('http://' + document.domain + ':' + location.port);

            socket.on('connect', function() {
                console.log('Connected');
            });

            socket.on('added_image', function(image_data) {
                console.log('Image updated');
                // Get the image element by its ID
                var img = document.getElementById('image-container');
                
                // Set the src attribute to the new image data
                img.src = 'data:image/png;base64,' + image_data;
            });
        </script>
    </head>
    <body>
        <!-- Add an image element with an ID -->
        <img id="image-container" src="" width="250px" height="auto">
    </body>
    </html>
    """