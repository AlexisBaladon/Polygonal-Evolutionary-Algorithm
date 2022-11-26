from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import Delaunay
import numpy as np
import cv2

class ImageProcessor():
    def __init__(self, vertex_count: int, 
                 input_name: str, input_path="img/",
                 output_path="test", output_name="delaunay.jpg",
                 width=None, height=None,
                 tri_outline=None, **kwargs):

        # Image parameters
        self.input_path = input_path
        self.input_name = input_name
        self.output_path = output_path
        self.output_name = output_name
        self.img_in_dir = f"{self.input_path}/{self.input_name}"
        self.img_out_dir = f"{self.output_path}/{self.output_name}"

        # Image dimensions
        self.width = width
        self.height = height
        self.vertex_count = vertex_count
        self.triangle_outline = tri_outline

        # Matrix of the original image
        self.original_image_matrix = None
        self.idx = {}
        self.order = 0

        # Edge detection
        self.edges_coordinates = None

    def __edge_detection(self, image, verbose=False):
        edges = cv2.Canny(np.array(image), 100, 200)
        self.edges_coordinates = list(np.argwhere(edges > 0))
        self.edges_coordinates = [tuple(reversed(x)) for x in self.edges_coordinates]
        
        if verbose:
            cv2.imshow("Edge detection", edges)
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

    def __tune_image(self, image: Image.Image, denoise: bool, edge_detection: bool, verbose=False) -> Image.Image:
        w, h = self.width, self.height

        if w is not None or h is not None:
            image = self.__resize_image(image, w, h)
            
        if denoise:
            image = self.__denoise(image)

        if edge_detection:
            self.__edge_detection(image, verbose)

        return image

    def read_image(self, verbose=False, edge_detection=True, denoise=True):
        image = Image.open(self.img_in_dir).convert("RGB")
        image = self.__tune_image(image, denoise, edge_detection, verbose=verbose)
        self.width, self.height = image.size
        self.original_image_matrix = np.asarray(image, dtype=np.uint64)

        ##entropy of image
        #w, h = self.width, self.height
        #image = Image.new('RGB', (w, h))
        ##create random image
        #image2 = Image.fromarray(np.random.randint(0, 255, (w, h, 3), dtype=np.uint8))
        #image.show()
        #image2.show()
        #print(image.entropy(), image2.entropy())
        ##create random image
#
        #exit()
#

        if verbose:
            image.show()

    def create_polygonal_image(self, vertices):
        w, h = self.width, self.height
        im = Image.new('RGB', (w, h))
        draw = ImageDraw.Draw(im)
        tri = Delaunay(vertices)
        triangles = tri.simplices
        for t in triangles:
            triangle = [tuple(vertices[t[i]]) for i in range(3)]
            vertices_centroid = np.mean(np.array(triangle), axis=0, dtype=int)
            color = tuple(self.original_image_matrix[vertices_centroid[1], vertices_centroid[0]])
            draw.polygon(triangle, fill=color, outline=self.triangle_outline)
        return im
