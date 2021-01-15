from images import tile
import os
import shutil
import threading
import PIL
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader
from fpdf import FPDF
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--stretch', action='store_true',
                    help='stretch the image on the page')

stretch = parser.parse_args().stretch


def _chunk(l, n): return [l[i:i + n] for i in range(0, len(l), n)]


def merge(images_paths, out_file):
    images_paths.sort(key=lambda file: int(
        os.path.splitext(os.path.split(file)[1])[0]))

    pdf = FPDF(orientation='P', unit='pt', format='A4')
    chunk_bookmarks = {}
    i = 0
    for imagef in images_paths:
        i += 1
        if imagef in chunk_bookmarks.keys():
            chunk_bookmarks[imagef] += 1
        else:
            chunk_bookmarks[imagef] = 1

        try:
            with Image.open(imagef) as image:
                if image.width > image.height:
                    pdf.add_page("vertical")
                    pdf.image(imagef, x=0, y=00, w=842, h=596)
                else:
                    tilled = tile(imagef)
                    for image in tilled:
                        pdf.add_page()
                        if stretch or len(tilled) == 1:
                            pdf.image(image, x=0, y=00, h=842, w=596)
                        else:
                            pdf.image(image, x=0, y=00, w=596)  # h=842,
        except OSError as e:
            pdf.add_page()

        yield i / len(images_paths)

    yield 0.9
    pdf.output(out_file, "F")
