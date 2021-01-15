import os
from PIL import Image
import image_slicer
import PIL.Image
import numpy
def crop(input, height, width, area):
	k = 0
	im = Image.open(input)
	imgwidth, imgheight = im.size
	for i in range(0,imgheight,height):
		for j in range(0,imgwidth,width):
			box = (j, i, j+width, i+height)
			a = im.crop(box)
			try:
				o = a.crop(area)
				o.save(input + str(k) + "-split.png")
			except:
				pass
			k += 1
def tile(image_path):
	ratio  = 1.4
	image  = PIL.Image.open(image_path);
	image  = numpy.array(image)

	height = image.shape[1] * ratio
	# width = image.shape[0]
	y = 0
	for i in range(0, int(image.shape[0]), int(height)):
		chunk = image[i:int(i + height)]
		PIL.Image.fromarray(chunk).save(f"test/cut-{str(y)}.png")
		y += 1



	# image_slicer.slice("test/1.jpeg", row=11, col=1)
tile("test/1.jpeg")
# crop("test/1.jpeg", 842, 566)