from scipy.spatial import Delaunay
from PIL import Image,ImageDraw
import numpy as np


idx = 0
image = Image.open("./img/wom.png")
original_image = image.convert("L").resize((255,255)) #TODO: CAMBIAR L
#original_image.show()
original_image_matrix = np.asarray(original_image, dtype=int)

width, height = 255, 255 #TODO: DESHARDCODEAR POR AMOR A CRISTO

#<!-- DECODE
def get_color(individual, rgb=False) -> tuple: #TODO: ABSTRAER
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

def area(x1, y1, x2, y2, x3, y3):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)))
 
def isInside(x1, y1, x2, y2, x3, y3, x, y):
    A = area (x1, y1, x2, y2, x3, y3)
    A1 = area (x, y, x2, y2, x3, y3)
    A2 = area (x1, y1, x, y, x3, y3)
    A3 = area (x1, y1, x2, y2, x, y)
    if(A == A1 + A2 + A3):
        return True
    return False

def create_polygonal_image(colored_vertices):
    im = Image.new('L', (width, height), color="white")
    draw = ImageDraw.Draw(im)
    vertices = [vertex_data[0] for vertex_data in colored_vertices]
    tri = Delaunay(vertices)
    triangles = tri.simplices
    for t in triangles:
        triangle = [tuple(vertices[t[i]]) for i in range(3)]
        colors = [colored_vertices[t[i]][1] for i in range(3)]
        #color = tuple(np.mean(colors, axis=0, dtype=int)) #TODO: no anda para grayscale
        #color = int(np.median(colors)) #TODO: solo anda para grayscale
        #isIn = lambda x,y: isInside(*triangle[0], *triangle[1], *triangle[2], x, y)
        range_x = range(min([x[0] for x in triangle]), max([x[0] for x in triangle]))
        range_y = range(min([x[1] for x in triangle]), max([x[1] for x in triangle]))
        colorsss = [original_image_matrix[x, y] for x in range_y for y in range_x]
        color = int(np.median(colorsss))
        draw.polygon(triangle, fill = color)
    return im

def decode(individual):
    colored_vertices = get_colored_vertices(individual)
    polygonal_image = create_polygonal_image(colored_vertices)
    global idx
    if idx % 2001 == 0:
        polygonal_image.save(f'./test_images/{idx}.png')
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
