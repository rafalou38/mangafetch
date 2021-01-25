from bs4 import BeautifulSoup
import urllib
import magic
import requests
import re
from re import compile as rc, findall
from pprint import pprint
import json
import os
import atexit
from urllib3.exceptions import ProtocolError

TMP_PATH = "tmp"
IMG_PATH = os.path.join(TMP_PATH, "images")
OUT_PATH = "out/"
PDF_PATH = os.path.join(TMP_PATH, "pdfs")

session = requests.session()
atexit.register(lambda: session.close())


def init():
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)
    if not os.path.exists(PDF_PATH):
        os.makedirs(PDF_PATH)
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)


def search(query="", page=1):
    uri = f"https://scansmangas.xyz/page/{page}/?s={urllib.parse.quote(query)}&post_type=manga"

    result = session.get(uri).text

    soup = BeautifulSoup(result, features="lxml")
    last_chapter = soup.find_all("a", {"class": "page-numbers"}, text=rc("\\d+"))
    last_chapter = last_chapter[-1].text if last_chapter else 0

    html_results = soup.find_all("div", {"class": "bsx"})
    dict_results = []
    for html_result in html_results:
        dict_results.append(
            {
                "name": html_result.find("a")["title"],
                "image": html_result.find("img")["src"],
                "stars": html_result.find("i").text,
                "id": html_result.find("a")["href"].split("/")[-2],
            }
        )
    return (dict_results, int(last_chapter))


def get_info(id):
    print("toto")
    uri = f"https://scansmangas.xyz/manga/{id}/"

    result = session.get(uri)
    if result.status_code != 200:
        uri = f"https://scansmangas.xyz/scan-{id}/"
        result = session.get(uri).text
        soup = BeautifulSoup(result, features="lxml")
        uri = soup.select_one("div.maincontent div center a")["href"]
        result = session.get(uri)

    soup = BeautifulSoup(result.text, features="lxml")
    spe = soup.find("div", {"class": "spe"}).find_all("span")

    banner = soup.find("div", {"class": "ime"}).find("img")["src"]

    cover = soup.find("div", {"class": "thumb"}).find("img")["src"]

    title = soup.find("h1", {"itemprop": "headline"}).text.strip()

    banner = soup.find("div", {"class": "ime"}).find("img")["src"]

    f = {}
    for e in spe:
        f[e.text.split(": ")[0].strip()] = e.text.split(": ")[1].strip()

    if "Statut" in f.keys():
        status = f["Statut"]
    else:
        status = "none"

    if "Alternatif" in f.keys():
        alternatif = f["Alternatif"]
    else:
        alternatif = "none"

    if "Auteur" in f.keys():
        author = f["Auteur"]
    else:
        author = "none"

    if "Sortie" in f.keys():
        release = f["Sortie"]
    else:
        release = "none"

    if "Edition" in f.keys():
        edition = f["Edition"]
    else:
        edition = "none"

    if "Genres" in f.keys():
        genres = f["Genres"]
    else:
        genres = "none"
    try:
        note = soup.find("span", {"itemprop": "ratingValue"}).text
    except Exception as _:
        note = "none"

    description = str(soup.find("div", {"class": "entry-content"}))
    chapters = list(
        map(lambda e: e.find("a")["href"], soup.find_all("span", {"class": "dt"}))
    )

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
        "note": note,
        "id": re.sub(r"^.+/([^/]+)/?$", r"\1", uri),
    }


def is_id_valid(id):
    url = f"https://scansmangas.xyz/manga/{id}/"
    r = session.get(url)
    return r.status_code == 200


def get_pages(chapter, manga_id):

    url = f"https://scansmangas.xyz/scan-{manga_id}-{chapter}/"
    r = session.get(url)
    if r.status_code != 200:
        url = f"https://scansmangas.xyz/manga/{manga_id}/"
        r = session.get(url)
        soup = BeautifulSoup(r.text, features="lxml")

        manga_id = re.findall(
            r"^.+/scan-(.+?)-\d+/?$", soup.select_one('[target="_top"]')["href"]
        )[0]

        url = f"https://scansmangas.xyz/scan-{manga_id}-{chapter}/"
        r = session.get(url)
    soup = BeautifulSoup(r.text, features="lxml")
    pages = soup.find("div", {"class": "nav_apb"}).findAll("a", text=rc("^\\d+$"))
    pages = list(map(lambda e: int(e.text), pages))

    return pages


def download_chapter(chapter, manga_id, pages=None):
    init()
    tryes = 0
    if pages == None:
        pages = get_pages(chapter, manga_id)
    for page in pages:
        while True:
            try:
                uri = f"https://scansmangas.xyz/scans/{manga_id}/{chapter}/{page}.jpg"
                path = os.path.join(IMG_PATH, manga_id, str(chapter))
                r = session.get(uri, stream=True)
                if not os.path.exists(path):
                    os.makedirs(path)
                buffer = r.iter_content(chunk_size=2048)
                chunk = next(buffer)
                mime = magic.from_buffer(chunk, mime=True)
                extension = os.path.split(mime)[1]
                filename = os.path.join(path, str(page) + "." + extension)
                with open(filename, "wb") as f:
                    f.write(chunk + r.raw.read())
                    break

            except ProtocolError as err:
                tryes += 1
                if tryes > 5:
                    raise err
        yield filename
