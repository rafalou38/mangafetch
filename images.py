import PIL.Image
import numpy
import os


def tile(image_path):
    try:
        ratio = 1.4
        image = PIL.Image.open(image_path)
        image = numpy.array(image)
        height = image.shape[1] * ratio

        if image.shape[1] * 2 < image.shape[0]:
            # width = image.shape[0]
            images = []
            y = 0
            for i in range(0, int(image.shape[0]), int(height)):
                chunk = image[i : int(i + height)]
                p = (
                    os.path.splitext(image_path)[0]
                    + " cut "
                    + str(y)
                    + os.path.splitext(image_path)[1]
                )
                PIL.Image.fromarray(chunk).save(p)
                images.append(p)
                y += 1
            return images
        else:
            return [image_path]
    except:
        return [image_path]


# tile("tmp\\images\\sweet-home\\0\\1.jpeg")
# for image in tile("tmp\\images\\one-piece\\680\\1.jpeg"):
# 	# image.show()
# 	# input()
# 	print(image)
