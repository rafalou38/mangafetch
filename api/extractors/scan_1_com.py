import re

from bs4 import BeautifulSoup


from . import Extractor
from myLog import logger


class scan_1_com(Extractor):
    name = "scan-1.com"

    @classmethod
    def search(cls, query="", page=1):
        from .. import session

        uri = f"https://wwv.scan-1.com/search?query={query}"
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

        uri = f"https://wwv.scan-1.com/{id}/"
        bad_char_remove_regex = r"\s\s|\\[ntr]"
        result = session.get(uri)

        soup = BeautifulSoup(result.text, features="lxml")

        spe = soup.select_one(".panel-body").select("h3")

        banner = "none"

        cover = soup.select_one("img.img-responsive")["src"]

        title = soup.select_one(".panel-heading").text.strip()
        f = {}

        for e in spe:
            text = e.text
            n_text = re.sub(bad_char_remove_regex, "", text)
            sp = n_text.split(":")
            f[sp[0].strip()] = sp[1].strip()

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
            note = soup.select_one(".average").text
        except Exception as _:
            note = "none"

        description = str(soup.select_one(".well"))
        chapters = []
        split_regex = r"(\d+(?:[\d\.]{2,})?)(?:[: ]*)(.*)"
        for ch in soup.select("ul.chapters li"):
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

        url = f"https://wwv.scan-1.com/{id}/"
        r = session.get(url)
        return r.status_code == 200

    @classmethod
    def get_pages(cls, chapter, manga_id):
        from .. import session

        url = f"https://wwv.scan-1.com/{manga_id}/chapitre-{chapter}"
        r = session.get(url)
        soup = BeautifulSoup(r.text, features="lxml")
        pages = soup.select("#all>img")
        pages = list(map(lambda e: e["data-src"].strip(), pages))

        return pages
