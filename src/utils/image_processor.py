import os
import io
import base64

from PIL import Image, ImageDraw
from scipy.spatial import Delaunay
import numpy as np
import cv2

class ImageProcessor():
    def __init__(self, input_name=None, 
                 vertex_count: int = None, 
                 input_path=os.path.join('data', 'inputs'),
                 output_path=os.path.join('results', 'experiments', 'formal', 'images'), 
                 output_name="delaunay.jpg",
                 width=None, height=None, tri_outline=None,
                 input_image: Image.Image=None, **kwargs):

        # Image parameters
        self.input_path = input_path
        self.input_name = input_name
        self.output_path = output_path
        self.output_name = output_name
        self.input_image = input_image
        
        if input_image is None:
            self.img_in_dir = os.path.join(self.input_path, self.input_name)
        self.img_out_dir = os.path.join(self.output_path, self.output_name)

        # Image dimensions
        self.width = width
        self.height = height
        self.vertex_count = vertex_count
        self.triangle_outline = tri_outline

        # Matrix of the original image
        self.original_image_matrix = None

        # Edge detection
        self.edges_coordinates = None

    def __edge_detection(self, image, show=False):
        edges_mask = cv2.Canny(np.array(image), 100, 200)
        self.edges_coordinates = list(np.argwhere(edges_mask > 0))
        self.edges_coordinates = [tuple(reversed(x)) for x in self.edges_coordinates]
        
        if show:
            cv2.imshow("Edge detection", edges_mask)
            cv2.waitKey(0)

    def __resize_image(self, image: Image.Image, w: int, h: int):
        if w is None:
            original_width,_ = image.size
            w = int(h * original_width / image.height)
        elif h is None:
            _, original_height = image.size
            h = int(w * original_height / image.width)
        image = image.resize((w, h))
        return image

    def __denoise(self, image):
        image = np.array(image)
        dst = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        image = Image.fromarray(dst)
        return image

    def __tune_image(self, image: Image.Image, denoise: bool, 
                     edge_detection: bool, show=False) -> Image.Image:
        w, h = self.width, self.height

        if w is not None or h is not None:
            image = self.__resize_image(image, w, h)
            
        if denoise:
            image = self.__denoise(image)

        if edge_detection:
            self.__edge_detection(image, show)

        return image

    def read_image(self, verbose=False, show=False, 
                   edge_detection=True, denoise=True):
        image = self.input_image

        if image is None:
            image = Image.open(self.img_in_dir)
        image = image.convert("RGB")

        image = self.__tune_image(image, denoise, edge_detection, show=show)
        self.width, self.height = image.size
        self.original_image_matrix = np.asarray(image, dtype=np.uint64)

        if self.vertex_count is None:
            image_entropy = image.entropy()
            self.vertex_count = max(int(np.power(2, image_entropy+3)), 5) # 5 is the minimum number of vertices

            if verbose:
                print(f"Image entropy: {image_entropy}")
                print(f"Vertex count: {self.vertex_count}")

        self.vertex_count -= 4 # 4 vertices are added to the image corners

        if show:
            image.show("Preprocessed image")

    def create_polygonal_image(self, vertices):
        w, h = self.width, self.height
        im = Image.new('RGB', (w, h))
        draw = ImageDraw.Draw(im)
        tri = Delaunay(vertices)
        triangles = tri.simplices
        for t in triangles:
            triangle = [tuple(vertices[t[i]]) for i in range(3)]
            vertices_centroid = np.mean(np.array(triangle), axis=0, dtype=int)
            color = tuple(self.original_image_matrix[vertices_centroid[1], 
                                                     vertices_centroid[0]])
            draw.polygon(triangle, fill=color, outline=self.triangle_outline)
        return im
    
    @staticmethod
    def encode_image(image: Image.Image):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        return image_base64

    @staticmethod
    def decode_image(image_data: str, base64_=False):
        if base64_:
            image_data = image_data.encode('utf-8')
            image_data = base64.b64decode(image_data)

        image = Image.open(io.BytesIO(image_data))
        return image
