from PIL import Image, ImageDraw
from scipy.spatial import Delaunay
import numpy as np

class ImageProcessor:
    def __init__(self, input_path="img/", input_name="triangles.jpg",
                 output_path="out/triangles/", output_name="delaunay.jpg",
                 width=255, height=255, vertex_count=50, **kwargs):
        
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

    def read_image(self, verbose=False):
        w, h = self.width, self.height
        image = Image.open(self.img_in_dir).convert("RGB").resize((w,h))
        self.original_image_matrix = np.asarray(image, dtype=int)
        if verbose:
            image.show()

    def get_vertices(self, individual):
        individual = [max(0, min(255, x)) for x in individual]
        individual = list(map(int, individual))
        vertices = list(zip(individual[::2], individual[1::2]))
        vertices.extend([[0,0], [0,255], [255,0], [255,255]])
        return vertices

    def create_polygonal_image(self, vertices):
        w, h = self.width, self.height
        im = Image.new('RGB', (w, h), color="white")
        draw = ImageDraw.Draw(im)
        tri = Delaunay(vertices)
        triangles = tri.simplices
        for t in triangles:
            triangle = [tuple(vertices[t[i]]) for i in range(3)]
            vertices_centroid = np.mean(np.array(triangle), axis=0, dtype=int)
            color = tuple(self.original_image_matrix[vertices_centroid[1], vertices_centroid[0]])
            draw.polygon(triangle, fill = color)
        return im

    def decode(self, individual):
        vertices = self.get_vertices(individual)
        polygonal_image = self.create_polygonal_image(vertices)

        if self.idx % 100 == 0:
            polygonal_image.save(f'test/{self.idx}-{self.order}.png')
            self.order += 1
        self.idx += 1
        
        return polygonal_image

    def get_fitness(self, decoded_individual):
        individual_image_matrix = np.asarray(decoded_individual, dtype=int)
        fitness = np.sum((individual_image_matrix - self.original_image_matrix)**2)
        return fitness

    def evalDelaunay(self, individual):
        decoded_individual = self.decode(individual)
        fit = self.get_fitness(decoded_individual)
        return fit,
