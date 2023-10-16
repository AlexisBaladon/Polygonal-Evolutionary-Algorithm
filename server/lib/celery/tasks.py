from celery import shared_task
from celery.contrib.abortable import AbortableTask

from src.lib.deap_config import DeapConfig
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.models.evolutionary_algorithm.ea_methods import EA
from src.utils.image_processor import ImageProcessor

def get_image_callback(ea: EA):
    from server.lib import sockets

    def image_added_callback(individuals_data: dict):
        encoded_images = {"images": [], "fitness": individuals_data["fitness"]}
        images = individuals_data["population"]

        for image in images:
            image = ea.decode(image)
            image = ea.image_processor.encode_image(image)
            encoded_images["images"].append(image)
            
        sockets.emit('added_image', encoded_images)
        return
    
    return image_added_callback

@shared_task(bind=True, base=AbortableTask)
def transform_image(self, image_processor_args: dict, ea_args: dict):
    try:
        print("Starting EA")
        image_processor_args["input_image"] = ImageProcessor.decode_image(image_processor_args["input_image"])
        image_processor = ImageProcessor(**image_processor_args)
        ea = EA(image_processor)
        image_added_callback = get_image_callback(ea)
        dc = DeapConfig(**ea_args)
        eac = EAHandler(ea, dc)
        eac.build_ea_module(**ea_args)
        eac.build_deap_module()
        eac.run(image_added_callback=image_added_callback, save=False)
    except Exception as e:
        print("Something wrong happened while initializing the EA; ", e)