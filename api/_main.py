import atexit
import os
from tempfile import TemporaryDirectory

import requests
from myLog import logger
from urllib3.exceptions import ProtocolError

tmp_dir = TemporaryDirectory()
TMP_PATH = tmp_dir.name
IMG_PATH = os.path.join(TMP_PATH, "images")
OUT_PATH = "out/"
PDF_PATH = os.path.join(TMP_PATH, "pdfs")

session = requests.session()


def _exit():
    session.close()
    logger.info("main: \033[31mclosing app")


atexit.register(_exit)


def init():
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)
    if not os.path.exists(PDF_PATH):
        os.makedirs(PDF_PATH)
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)


class website:
    @classmethod
    def search(cls, query="", page=1):
        pass

    @classmethod
    def get_info(cls, id):
        pass

    @classmethod
    def is_id_valid(cls, id):
        pass

    @classmethod
    def get_pages(cls, chapter, manga_id):
        pass

    @classmethod
    def download_chapter(cls, chapter, manga_id, pages=None, img_url=None):
        pass
