from scipy.spatial import Delaunay
from PIL import Image,ImageDraw
import numpy as np

from initialize import VERTEX_COUNT


idx = 0
image = Image.open("./img/pok.png")
original_image = image.convert("RGB").resize((255,255)) #TODO: CAMBIAR L
original_image.show()
original_image_matrix = np.asarray(original_image, dtype=int)

width, height = 255, 255 #TODO: DESHARDCODEAR POR AMOR A CRISTO

#<!-- DECODE

def get_vertices(individual):
    ind_size = len(individual)
    return [(individual[i], individual[i + 1]) for i in range(ind_size>>1) if i&1==0]

def create_polygonal_image(vertices):
    im = Image.new('RGB', (width, height), color="white")
    draw = ImageDraw.Draw(im)
    tri = Delaunay(vertices)
    triangles = tri.simplices
    for t in triangles:
        triangle = [tuple(vertices[t[i]]) for i in range(3)]
        range_x = range(min([x[0] for x in triangle]), max([x[0] for x in triangle]))
        range_y = range(min([x[1] for x in triangle]), max([x[1] for x in triangle]))
        #colors = [original_image_matrix[x, y] for x in range_y for y in range_x]
        #color = tuple(np.median(colors, axis=0).astype(int))
        vertices_centroid = np.mean(np.array(triangle), axis=0, dtype=int)
        color = tuple(original_image_matrix[vertices_centroid[1], vertices_centroid[0]])
        draw.polygon(triangle, fill = color)
    return im

def decode(individual):
    vertices = get_vertices(individual)
    polygonal_image = create_polygonal_image(vertices)
    global idx
    if idx % 100 == 0:
        polygonal_image.save(f'./test_images/pok/median_{idx}-{VERTEX_COUNT}.png')
    idx += 1
    return polygonal_image
#DECODE -->


def get_fitness(decoded_individual):
    individual_image_matrix = np.asarray(decoded_individual, dtype=int)#.flatten() TODO: RGB
    #original_image_matrix = np.asarray(original_image, dtype=int)#.flatten() #TODO: Se hace una sola vez
    fitness = np.linalg.norm(individual_image_matrix - original_image_matrix) 
    #fitness = np.sum([np.linalg(individual_image_matrix[i,j] - original_image_matrix[i,j]) for i in range(individual_image_matrix.shape[0]) for j in range(original_image_matrix[1])])
    #fitness = np.sum((individual_image_matrix - original_image_matrix)**2)
    #print(fitness)
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

