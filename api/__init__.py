import atexit
import os
from tempfile import TemporaryDirectory, gettempdir

import requests

from myLog import logger
from .downloaders import downloader
from .extractors import Extractor

from .extractors.crunchyroll import crunchyroll
from .extractors.scan_1_com import scan_1_com
from .extractors.scan_fr_cc import scan_fr_cc
from .extractors.scansmangas_xyz import scansmangas_xyz

tmp_root_dir = os.path.join(gettempdir(), "mangafetch")
if not os.path.exists(tmp_root_dir):
    os.makedirs(tmp_root_dir)
temp_dir = TemporaryDirectory(dir=tmp_root_dir)

TMP_PATH = temp_dir.name
IMG_PATH = os.path.join(TMP_PATH, "images")
OUT_PATH = os.path.abspath("out/")
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


sources = {
    "crunchyroll.com": crunchyroll,
    "scansmangas.xyz": scansmangas_xyz,
    "scan-1.com": scan_1_com,
    "scan-fr.cc": scan_fr_cc,
}
