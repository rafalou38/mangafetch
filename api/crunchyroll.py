import re
import subprocess

from bs4 import BeautifulSoup

from ._main import session, website, user_agent
from myLog import logger
import json
import urllib.request
import gzip
import consolog
import os


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _get(url):
    request = urllib.request.Request(url)

    request.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    )
    request.add_header(
        "Accept",
        "application/atom+xml,application/rdf+xml,application/rss+xml,application/x-netcdf,"
        "application/xml;q=0.9,text/xml;q=0.2,*/*;q=0.1",
    )
    request.add_header("Accept-encoding", "gzip, deflate")

    opener = urllib.request.build_opener()
    with opener.open(request) as got_file:
        gzip_fd = gzip.GzipFile(fileobj=got_file)
        result = gzip_fd.read()

    return result


class crunchyroll(website):
    anime_list = []
    name = "crunchyroll.com"

    @classmethod
    def _init_anime_list(cls):
        try:
            logger.info("api: downloading crunchyroll series list")
            uri = (
                "https://www.crunchyroll.com/ajax/?req=RpcApiSearch_GetSearchCandidates"
            )
            response_text = _get(uri)
            response_text = (
                response_text.decode("UTF-8")
                .replace("/*-secure-\n", "")
                .replace("\n*/", "")
            )
            cls.anime_list = json.loads(response_text)
        except Exception as e:
            logger.error("api: failed to get anime list for crunchyroll: " + repr(e))
            logger.info("api: loading default from file (not up to date)")
            with open("api/crunchy.json", "r") as f:
                cls.anime_list = json.load(f)

    @classmethod
    def search(cls, query="", page=1, max=30):
        if not cls.anime_list:
            cls._init_anime_list()

        dict_results = []
        pages = 0
        for e in cls.anime_list["data"]:
            if query.lower() in e["name"].lower():
                dict_results.append(
                    {
                        "name": e["name"],
                        "image": e["img"].replace("small", "large"),
                        "stars": None,
                        "id": e["link"].replace("/", ""),
                        "type": e["type"],
                    }
                )
        if len(dict_results) > 30:
            ch = list(_chunks(dict_results, 30))
            pages = len(ch)
            return ch[page - 1], pages
        return dict_results, 0

    @classmethod
    def get_info(cls, id):
        uri = f"https://www.crunchyroll.com/fr/{id}/more"
        result = _get(uri)

        soup = BeautifulSoup(result, features="lxml")

        cover = soup.select_one("img.poster")["src"]

        title = soup.select_one(".ellipsis>span").text.strip()

        edition = soup.find("span", text="Éditeur").findNext().text

        genres = list(
            map(lambda e: e.text, soup.select(".large-margin-bottom>ul>li>a"))
        )

        id = soup.select_one('input[name="from"]')["value"]
        # try:
        #     note = soup.select_one(".average").text
        # except Exception as _:
        note = float(soup.select_one('.left>meta[itemprop="ratingValue"]')["content"])

        description = str(soup.select_one(".series-extended-information ").text)

        uri = f"https://www.crunchyroll.com/fr/{id}/videos"
        result = _get(uri)
        soup = BeautifulSoup(result, features="lxml")

        chapters = []
        for ch in soup.select(".episode"):
            ch_url = "https://www.crunchyroll.com/" + ch["href"].strip()
            ch_number = ch.select_one(".series-title").text.strip().split(" ")[1]
            ch_name = ch.select_one(".short-desc").text.strip()
            chapters.append({"url": ch_url, "name": ch_name, "number": ch_number})

        return {
            "banner": cover,
            "cover": cover,
            "title": title,
            "alternatif": "none",
            "status": "none",
            "author": "none",
            "release": "none",
            "edition": edition,
            "genres": genres,
            "description": description,
            "chapters": chapters,
            "note": float(note) * 2,
            "id": id,
        }


# consolog.log(crunchyroll.search("one piece"))
