from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import Delaunay
import numpy as np
import cv2
import random

class ImageProcessor():
    def __init__(self, input_path="img/", input_name="scarlet.jpg",
                 output_path="test", output_name="delaunay.jpg",
                 width=None, height=None, vertex_count=150, **kwargs):
        
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

        #Matrix of the original image
        self.original_image_matrix = None
        self.idx = 0
        self.order = 0

        # Edge detection
        self.edges_coordinates = None

        #TODO: PARAMETRIZAR
        # Triangle outline
        self.triangle_outline = None
        self.initial_color = "white"

    def __edge_detection(self, image):
        edges = cv2.Canny(np.array(image), 100, 200)
        cv2.imshow("edges", edges)
        cv2.waitKey(0)
        self.edges_coordinates = list(np.argwhere(edges > 0))
        self.edges_coordinates = [tuple(reversed(x)) for x in self.edges_coordinates]

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

    def __tune_image(self, image: Image.Image, color_palette: int, denoise: bool, edge_detection: bool) -> Image.Image:
        w, h = self.width, self.height

        if color_palette:
            image = image.convert('P', palette=Image.ADAPTIVE, colors=color_palette).convert('RGB')

        if denoise:
            image = self.__denoise(image)

        if edge_detection:
            self.__edge_detection(image)

        if w is not None or h is not None:
            image = self.__resize_image(image, w, h)
        
        return image

    def read_image(self, verbose=False, edge_detection=False, color_palette: int=0, denoise=True):
        image = Image.open(self.img_in_dir).convert("RGB")
        image = self.__tune_image(image, color_palette, denoise, edge_detection)
        self.width, self.height = image.size
        self.original_image_matrix = np.asarray(image, dtype=np.uint64)

        if verbose:
            image.show()

    def get_vertices(self, individual):
        individual[::2] = np.clip(individual[::2], 0, self.width)
        individual[1::2] = np.clip(individual[1::2], 0, self.height)
        individual = list(map(int, individual))
        vertices = list(zip(individual[::2], individual[1::2]))
        vertices.extend([(0,0), (0,self.height), (self.width,0), (self.width,self.height)])
        return vertices

    def create_polygonal_image(self, vertices):
        w, h = self.width, self.height
        im = Image.new('RGB', (w, h), color=self.initial_color)
        draw = ImageDraw.Draw(im)
        tri = Delaunay(vertices)
        triangles = tri.simplices
        for t in triangles:
            triangle = [tuple(vertices[t[i]]) for i in range(3)]
            vertices_centroid = np.mean(np.array(triangle), axis=0, dtype=int)
            color = tuple(self.original_image_matrix[vertices_centroid[1], vertices_centroid[0]])
            draw.polygon(triangle, fill=color, outline=self.triangle_outline)

        return im

    def decode(self, individual):
        vertices = self.get_vertices(individual)
        polygonal_image = self.create_polygonal_image(vertices)

        #if self.idx % 100 == 0:
        #    polygonal_image.save(f'test/{self.idx}-{self.order}-{random.randint(0,500)}.png')
        #    self.order += 1
        #self.idx += 1
        
        return polygonal_image

    def get_fitness(self, decoded_individual):
        individual_image_matrix = np.asarray(decoded_individual, dtype=np.uint64)
        fitness = np.sum((individual_image_matrix - self.original_image_matrix)**2)
        return fitness

    def evalDelaunay(self, individual):
        decoded_individual = self.decode(individual)
        fit = self.get_fitness(decoded_individual)
        return fit,
