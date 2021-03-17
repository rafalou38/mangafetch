import os
import re
from magic import magic
from bs4 import BeautifulSoup
import base64

import requests

from . import Extractor
from myLog import logger


class scan_fr_cc(Extractor):
    name = "scan-fr.cc"

    @classmethod
    def search(cls, query="", page=1):
        from .. import session

        uri = f"https://www.scan-fr.cc/search?query={query}"
        response = session.get(uri).json()

        dict_results = []
        for result in response["suggestions"]:
            dict_results.append(
                {
                    "name": result["value"],
                    "image": None,
                    "stars": None,
                    "id": result["data"],
                    "type": "manga",
                }
            )
        return dict_results, 0

    @classmethod
    def get_info(cls, id):
        from .. import session

        uri = f"https://www.scan-fr.cc/manga/{id}/"
        bad_char_remove_regex = r"\s\s|\\[ntr]"
        result = session.get(uri)

        soup = BeautifulSoup(result.text, features="lxml")

        banner = "none"

        cover = soup.select_one("img.img-responsive")["src"]
        encoded = base64.b64encode(requests.get(cover).content).decode()
        cover = "data:image/png;base64,{}".format(encoded)

        title = soup.select_one(".widget-title").text.strip()

        dl = iter(soup.select_one(".dl-horizontal").select("dd, dt"))

        f = {}
        for dt, dd in zip(dl, dl):

            f[dt.text.strip()] = dd.text.strip()

        if "Statut" in f.keys():
            status = f["Statut"]
        else:
            status = "none"

        if "Autres noms" in f.keys():
            alternatif = f["Autres noms"]
        else:
            alternatif = "none"

        if "Auteur(s)" in f.keys():
            author = f["Auteur(s)"]
        else:
            author = "none"

        if "Date de sortie" in f.keys():
            release = f["Date de sortie"]
        else:
            release = "none"

        edition = "none"

        if "Catégories" in f.keys():
            genres = f["Catégories"]
        else:
            genres = "none"

        try:
            note = soup.select_one("#item-rating")["data-score"]
        except Exception as _:
            note = "none"

        description = str(soup.select_one(".well"))
        chapters = []
        split_regex = r"(\d+(?:[\d\.]{2,})?)(?:[: \n]*)(.*)"
        for ch in soup.select("ul.chapterszozo li:not(.btn)"):
            ch_url = ch.select_one("a")["href"].strip()
            ch_name = ch.select_one("h5").text.strip()
            ch_number, ch_name = re.findall(split_regex, ch_name)[0]
            chapters.append({"url": ch_url, "name": ch_name, "number": ch_number})

        return {
            "banner": banner,
            "cover": cover,
            "title": title,
            "alternatif": alternatif,
            "status": status,
            "author": author,
            "release": release,
            "edition": edition,
            "genres": genres,
            "description": description,
            "chapters": chapters,
            "note": float(note) * 2,
            "id": re.sub(r"^.+/([^/]+)/?$", r"\1", uri),
        }

    @classmethod
    def is_id_valid(cls, id):
        from .. import session

        url = f"https://www.scan-fr.cc/manga/{id}/"
        r = session.get(url)
        return r.status_code == 200

    @classmethod
    def get_pages(cls, chapter, manga_id):
        from .. import session

        print("get page", chapter)

        url = f"https://www.scan-fr.cc/manga/{manga_id}/{chapter}/1"
        r = session.get(url)
        soup = BeautifulSoup(r.text, features="lxml")
        pages = soup.select("#all>img")
        pages = list(map(lambda e: e["data-src"].strip(), pages))

        return pages

    @classmethod
    def download_chapter(cls, chapter, manga_id, pages=None):
        from .. import init, IMG_PATH, session, logger

        init()
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
                    path,
                    os.path.splitext(os.path.split(page)[1])[0].split("_")[0]
                    + "."
                    + extension,
                )
                with open(filename, "wb") as f:
                    f.write(chunk + r.raw.read())
                yield filename
            except Exception as err:
                logger.error(
                    'api: failed downloading image from "' + page + '" : ' + repr(err)
                )