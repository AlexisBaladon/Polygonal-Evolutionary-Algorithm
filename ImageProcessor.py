from PIL import Image, ImageDraw
from scipy.spatial import Delaunay
import numpy as np
import cv2

class ImageProcessor:
    def __init__(self, input_path="img/", input_name="triangles.jpg",
                 output_path="out/triangles/", output_name="delaunay.jpg",
                 width=None, height=None, vertex_count=50, **kwargs):
        
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

    def read_image(self, verbose=True):
        w, h = self.width, self.height

        image = cv2.imread(self.img_in_dir, cv2.IMREAD_COLOR)
        #show image
        #image = Image.open(self.img_in_dir).convert("RGB")
        
        # Resize image if needed
        if w is not None or h is not None:
            print("no deberia entrar")
            if h is not None:
                original_width, = image.size
                w = int(h * original_width / image.height)
            else:
                _, original_height = image.size
                h = int(w * original_height / image.width)
            image = image.resize((w, h))

        self.height, self.width = image.shape[:2]
        self.original_image_matrix = image#np.asarray(image, dtype=np.uint64)

        if verbose:
            #show image with cv2
            cv2.imshow("Original Image", image)
            cv2.waitKey(0)

    def get_vertices(self, individual):
        #clip the odd indices to be between 0 and self.width and the pair indices to be between 0 and self.height
        individual[::2] = np.clip(individual[::2], 0, self.width)
        individual[1::2] = np.clip(individual[1::2], 0, self.height)
        individual = list(map(int, individual))
        vertices = list(zip(individual[::2], individual[1::2]))
        vertices.extend([(0,0), (0,self.height), (self.width,0), (self.width,self.height)])
        return vertices

    def create_polygonal_image(self, vertices):
        w, h = self.width, self.height
        #creates cv2 white image
        #create numpy image with white background
        im = np.zeros((h, w, 3), np.uint8)
        
        #im = Image.new('RGB', (w, h), color="white") TODO: PIL
        #draw = ImageDraw.Draw(im) TODO: PIL
        tri = Delaunay(vertices)
        triangles = tri.simplices
        for t in triangles:
            triangle = [tuple(vertices[t[i]]) for i in range(3)]
            triangle = np.array(triangle, np.int32)
            vertices_centroid = np.mean(triangle, axis=0, dtype=int)
            #from height and width to cv2 coordinates
            vertices_centroid[0] = h - vertices_centroid[0] - 1
            #print(vertices_centroid, self.original_image_matrix)
            color = tuple(self.original_image_matrix[vertices_centroid[1], vertices_centroid[0]])
            color = tuple([int(x) for x in color])
            cv2.fillConvexPoly(im, triangle, color)
            #draw.polygon(triangle, fill = color)
        return im

    def decode(self, individual):
        vertices = self.get_vertices(individual)
        polygonal_image = self.create_polygonal_image(vertices)

        if self.idx % 100 == 0:
            cv2.imwrite(f"test/{self.idx}-{self.order}.png", polygonal_image)
            #polygonal_image.save(f'test/{self.idx}-{self.order}.png') TODO: PIL
            self.order += 1
        self.idx += 1
        
        return polygonal_image

    def get_fitness(self, decoded_individual):
        #individual_image_matrix = decoded_individual#np.asarray(decoded_individual, dtype=np.uint64) TODO: PIL
        fitness = np.sum((decoded_individual - self.original_image_matrix)**2)
        return fitness

    def evalDelaunay(self, individual):
        decoded_individual = self.decode(individual)
        fit = self.get_fitness(decoded_individual)
        return fit,
