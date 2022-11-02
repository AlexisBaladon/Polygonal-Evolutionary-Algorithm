from PIL import Image, ImageDraw
from scipy.spatial import Delaunay
import numpy as np

class ImageProcessor:
    def __init__(self, img_in_dir="img/girl.jpg", img_out_dir="out/girl/",    img_desired_width=255, img_desired_height=255):
        self.img_in_dir = img_in_dir
        self.img_out_dir = img_out_dir
        self.img_desired_width = img_desired_width
        self.img_desired_height = img_desired_height

        self.original_image_matrix = None
        self.idx = 0
        self.order = 0

    def read_image(self, verbose=False):
        w, h = self.img_desired_width, self.img_desired_height
        image = Image.open(self.img_in_dir).convert("RGB")

        if verbose:
            image.show()

        self.original_image = image.resize((w,h))
        self.original_image_matrix = np.asarray(self.original_image, dtype=int)

    def get_vertices(self, individual):
        ind_size = len(individual)
        return [(individual[i], individual[i + 1]) for i in range(ind_size) if i&1==0]

    def create_polygonal_image(self, vertices):
        w, h = self.img_desired_width, self.img_desired_height
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
            polygonal_image.save(f'{self.img_out_dir}/{self.idx}-{self.order}.png')
            self.order += 1
        self.idx += 1
        
        return polygonal_image

    def get_fitness(self, decoded_individual):
        individual_image_matrix = np.asarray(decoded_individual, dtype=int)
        fitness = np.linalg.norm(individual_image_matrix - self.original_image_matrix) 
        return fitness

    def evalDelaunay(self, individual):
        decoded_individual = self.decode(individual)
        fit = self.get_fitness(decoded_individual)
        return fit,
