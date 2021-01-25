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


def mergeBookmarks(bookmarks: dict, out_file: str):
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    for chapter, files in bookmarks.items():
        files.sort(key=lambda file: int(
            os.path.splitext(os.path.split(file)[1])[0]))
        i = 0
        for imagef in files:
            i += 1
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
            yield min(i / len(files), 0.9)
    yield 0.9
    pdf.output(out_file, "F")


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

# for step in mergeBookmarks(
#     {'60': ['https://scansmangas.xyz/scans/one-piece/972/1.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/2.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/3.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/4.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/5.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/6.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/7.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/8.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/9.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/10.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/11.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/12.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/13.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/14.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/15.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/16.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/17.jpg',
#             'https://scansmangas.xyz/scans/one-piece/972/18.jpg'],
#      },
#     "out/jujutsu-kaisen.pdf"
# ):
#     print(step)
