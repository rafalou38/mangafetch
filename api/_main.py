import atexit
import os
from tempfile import TemporaryDirectory

import requests
from magic import magic

from myLog import logger
from urllib3.exceptions import ProtocolError

tmp_dir = TemporaryDirectory()
TMP_PATH = tmp_dir.name
IMG_PATH = os.path.join(TMP_PATH, "images")
OUT_PATH = "out/"
PDF_PATH = os.path.join(TMP_PATH, "pdfs")

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
)

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
    name = "website"

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

    @classmethod
    def download_chapter(cls, chapter, manga_id, pages=None):
        init()
        tries = 0
        if pages is None:
            pages = cls.get_pages(chapter, manga_id)
        for page in pages:
            try:
                path = os.path.join(IMG_PATH, manga_id, str(chapter))
                r = session.get(page, stream=True)
                if not os.path.exists(path):
                    os.makedirs(path)
                buffer = r.iter_content(chunk_size=2048)
                chunk = next(buffer)
                mime = magic.from_buffer(chunk, mime=True)
                extension = os.path.split(mime)[1]
                filename = os.path.join(
                    path, os.path.splitext(os.path.split(page)[1])[0] + "." + extension
                )
                with open(filename, "wb") as f:
                    f.write(chunk + r.raw.read())
                yield filename
            except Exception as err:
                logger.error(
                    'api: failed downloading image from "' + page + '" : ' + repr(err)
                )
