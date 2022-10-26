from scipy.spatial import Delaunay
from PIL import Image,ImageDraw
import numpy as np


#<!-- DECODE
def get_color(individual, rgb=True) -> tuple: #TODO: ABSTRAER
    if rgb:
        return individual[0:3], 3 
    return individual[0], 1

def get_colored_vertices(individual):
    decoded_individual = []
    i = 0
    ind_size = len(individual)
    while i < ind_size:
        coord = individual[i], individual[i + 1]
        color, size_color = get_color(individual[i+2:])
        decoded_individual.append((coord, color))
        i += 2 + size_color
    return decoded_individual

width, height = 255, 255 #TODO: DESHARDCODEAR POR AMOR A CRISTO

def create_polygonal_image(colored_vertices):
    im = Image.new('RGB', (width, height), color="white")
    draw = ImageDraw.Draw(im)
    vertices = [vertex_data[0] for vertex_data in colored_vertices]
    tri = Delaunay(vertices)
    triangles = tri.simplices
    for t in triangles:
        triangle = [tuple(vertices[t[i]]) for i in range(3)]
        colors = [colored_vertices[t[i]][1] for i in range(3)]
        color = tuple(np.mean(colors, axis=0, dtype=int))
        draw.polygon(triangle, fill = color)
    return im

idx = 0
def decode(individual):
    colored_vertices = get_colored_vertices(individual)
    polygonal_image = create_polygonal_image(colored_vertices)
    global idx
    if idx % 2000 == 0:
        polygonal_image.save(f'./test_images/{idx}.png')
    idx += 1
    return polygonal_image
#DECODE -->

image = Image.open("img/black_inverted_triangle.jpeg")
original_image = image.convert("RGB").resize((25,25))
original_image.show()

def get_fitness(decoded_individual):
    individual_image_matrix = np.asarray(decoded_individual, dtype=int)
    original_image_matrix = np.asarray(original_image, dtype=int)
    fitness = np.sum((individual_image_matrix - original_image_matrix)**2, dtype=int)
    return fitness

def evalDelaunay(individual):
    decoded_individual = decode(individual)
    fit = get_fitness(decoded_individual)
    return fit,

if __name__ == "__main__":
    ind1 = [
        5,5, 0,0,0,
        255,20, 255,255,255,
        128,50, 0,0,0,
    ]
    ind2 = [
        15,15, 0,0,0,
        200,20, 255,255,255,
        12,50, 0,0,0,
    ]
    img1, img2 = decode(ind1), decode(ind2)
    img1.show(), img2.show()
    img1, img2 = np.asarray(img1), np.asarray(img2)
    print(np.sum((img1 - img2)**2, dtype=int))
