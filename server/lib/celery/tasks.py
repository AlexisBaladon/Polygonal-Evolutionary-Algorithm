import time

from celery import shared_task
from celery.contrib.abortable import AbortableTask

from src.lib.deap_config import DeapConfig
from src.models.evolutionary_algorithm.ea_handler import EAHandler
from src.models.evolutionary_algorithm.ea_methods import EA
from src.utils.image_processor import ImageProcessor
from server.lib import broker


def get_image_callback(ea: EA, user_id: str):
    def image_added_callback(individuals_data: dict, generation: int):
        encoded_images = {"images": [], "fitness": individuals_data["fitness"]}
        images = individuals_data["population"]

        for image in images:
            image = ea.decode(image)
            image = ea.image_processor.encode_image(image)
            encoded_images["images"].append(image)
            
        added_image_key = broker.get_added_image_key(user_id, generation)
        broker.set(added_image_key, encoded_images)
        return
    
    return image_added_callback

def get_stop_condition_callback(user_id: str, max_iddle_seconds=90):
    def stop_condition_callback():
        last_connection_key = broker.get_last_connection_key(user_id)
        last_connection = broker.get(last_connection_key)
        current_time = time.time()

        if last_connection is None:
            print("First connection")
            return False
        
        if current_time - last_connection > max_iddle_seconds:
            print("Max iddle time reached")
            broker.set(last_connection_key, None)
            return True
        
        print("Connection is still alive: ", current_time - last_connection, " seconds")
        return False
    
    return stop_condition_callback

@shared_task(bind=True, base=AbortableTask)
def transform_image(self, image_processor_args: dict, ea_args: dict, user_id: str):
    try:
        image_processor_args["input_image"] = ImageProcessor.decode_image(image_processor_args["input_image"])
        image_processor = ImageProcessor(**image_processor_args)
        ea = EA(image_processor)

        image_added_callback = get_image_callback(ea, user_id)
        stop_condition_callback = get_stop_condition_callback(user_id)

        dc = DeapConfig(**ea_args)
        eac = EAHandler(ea, dc)
        eac.build_ea_module(**ea_args)
        eac.build_deap_module()
        eac.run(image_added_callback=image_added_callback,
                stop_condition_callback=stop_condition_callback,
                save=False)

    except Exception as e:
        print("Something wrong happened while initializing the EA; ", e)