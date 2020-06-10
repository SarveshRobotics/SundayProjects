# coding: utf-8

# Create 2D landscapes using Midpoint Displacement

import random
import bisect
import cv2
from PIL import Image, ImageDraw
from colourlovers import clapi
import argparse
import numpy as np
from matplotlib.patches import Circle

# Midpoint Displacement Algorithm
def midpoint_displacement(start, end, roughness, v_dis=None, iter=16):
	# create more and more fractals
	if v_dis is None:
		v_dis = (start[1] + end[1])/2 # initial vertical displacement

	points = [start, end]
	
	for i in range(iter):
		points_tup = tuple(points)

		for j in range(len(points) - 1):
			midpoint = list(map(lambda x:(points_tup[j][x]+points_tup[j+1][x])/2, [0, 1]))

			midpoint[1] += random.choice([-v_dis, v_dis])

			bisect.insort(points, midpoint)

		v_dis *= 2**(-roughness)

	return points


# Draw different Layers
def draw_layers(layers, width, height, colorKeyword):
	color_dict = None

	if colorKeyword:
		c1 = clapi.ColourLovers()
		palettes = c1.search_palettes(request = "top", keywords=colorKeyword, numResults=15)
		palette = palettes[random.choice(range(len(palettes)))]

		color_dict = {str(iter):palette.hex_to_rgb()[iter] for iter in range(len(palette.colors))}

	if color_dict is None or len(color_dict.keys()) < len(layers):
		color_dict = {
            "0": (195, 157, 224),
            "1": (158, 98, 204),
            "2": (130, 79, 138),
            "3": (68, 28, 99),
            "4": (49, 7, 82),
            "5": (23, 3, 38),
            "6": (240, 203, 163),
        }

	# Create image into which the terrain will be drawn
	landscape = Image.new("RGBA", (width, height), color_dict[str(len(color_dict) - 1)])
	landscape_draw = ImageDraw.Draw(landscape)

	# Sun
	landscape_draw.ellipse((50, 25, 100, 75), fill=(255, 255, 255, 255))

	# Sample the y values of all x in image
	final_layers = []

	for layer in layers:
		sampled_layer = []
		for i in range(len(layer) - 1):
			sampled_layer += [layer[i]]
			if layer[i+1][0] - layer[i][0] > 1:
				m = float(layer[i+1][1] - layer[i][1])/(layer[i + 1][0] - layer[i][0])
				c = layer[i][1] - m*layer[i][0]
				y = lambda x: m*x + c

				for j in range(int(layer[i][0]+1), int (layer[i+1][0])):
					sampled_layer += [[j, y(j)]]
		final_layers += [sampled_layer]

	final_layers_enum = enumerate(final_layers)

	for final_layer in final_layers_enum:
		for x in range(len(final_layer[1]) - 1):
			    landscape_draw.line(
                (
                    final_layer[1][x][0],
                    height - final_layer[1][x][1],
                    final_layer[1][x][0],
                    height),
                color_dict[str(final_layer[0])]
                )
	
	# pixels = list(landscape.getdata())
	# width, height = landscape.size
	# pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
	# print(pixels)
	return landscape


parser = argparse.ArgumentParser(description="2D Procedural Landscape generator")
parser.add_argument("-t", "--theme", type=str, help="theme for colour palette")
args = parser.parse_args()


# Simpler approach
def draw_image(layers, width, height):
	blank_image = np.zeros((height, width, 3), np.uint8)

	# Moon is round the corner
	cv2.ellipse(blank_image,(75, 75),(50, 50), 0, 0, 360, [255,255,255], -1)

	color_dict = {
            "0": (195, 157, 224),
            "1": (158, 98, 204),
            "2": (130, 79, 138),
            "3": (68, 28, 99),
            "4": (49, 7, 82),
            "5": (23, 3, 38),
            "6": (240, 203, 163)}

	for i, layer in enumerate(layers):
		try:
			# Create line art
			for pixel in layer:
				blank_image[height - int(pixel[1]), int(pixel[0])] = color_dict[str(i)]
				y = height - int(pixel[1])
				while(y+1 < height):
					y += 1
					blank_image[y, int(pixel[0])] = color_dict[str(i)]
		except:
			print(pixel)

	return blank_image

def create_a_landscape():

	# Image Dimensions
	width = 900; height = 500

	# A four layer landscape is on my mind!
	layer_1 = midpoint_displacement([250, 0], [width, 200], 1.4, 20, 12)
	layer_2 = midpoint_displacement([0, 180], [width, 80], 1.2, 30, 12)
	layer_3 = midpoint_displacement([0, 270], [width, 190], 1, 120, 9)
	layer_4 = midpoint_displacement([0, 350], [width, 320], 0.9, 250, 8)

	if args.theme:
		color_theme = args.theme
	else:
		color_theme = None

	landscape1 = draw_image([layer_4, layer_3, layer_2, layer_1], width, height)
	landscape1 = Image.fromarray(landscape1, 'RGB')
	landscape1.save("LandscapeNightLines.png")
	landscape = draw_layers([layer_4, layer_3, layer_2, layer_1], width, height, color_theme)
	landscape.save("Landscape.png")

if __name__ == "__main__":
	create_a_landscape()
