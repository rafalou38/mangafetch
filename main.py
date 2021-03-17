import subprocess
import platform
import threading
import os
from typing import Type, List

from data import MagicSave
import pretty_errors
import pdfManip
import api
import eel
from myLog import logger

import os, sys

sys.path.insert(0, os.getcwd())

logger.info("main: starting app")

save = MagicSave(dev=True)

pretty_errors.configure(
    name="my_config",
    separator_character="₪",
    filename_display=pretty_errors.FILENAME_EXTENDED,
    line_number_first=True,
    display_link=True,
    lines_before=2,
    lines_after=2,
    line_color="═"
    + pretty_errors.RED
    + "❯ "
    + pretty_errors.default_config.line_color
    + "│ ",
    code_color="   " + pretty_errors.default_config.code_color + "│ ",
    truncate_code=True,
    display_arrow=True,
)
pretty_errors.blacklist("C:\\Users\\Rafael\\Anaconda3")
pretty_errors.replace_stderr()

OUT_PATH = "out"

# current_api = api.sources[list(api.sources.keys())[0]]
current_api = api.scansmangas_xyz


@eel.expose
def search(query="", page=1):
    logger.info('api: searched "' + query + '"')
    result, pages = current_api.search(query, page)
    return result, pages


@eel.expose
def get_info(id):
    logger.info('api: got info for manga "' + id + '"')
    return current_api.get_info(id)


# ==> SOURCES


@eel.expose
def get_sources():
    return list(api.sources.keys())


@eel.expose
def get_current_source():
    return current_api.name


@eel.expose
def set_source(source):
    global current_api

    if source in api.sources:
        current_api = api.sources[source]
        logger.info("api: source set to " + source)
    else:
        logger.warn("api: failed to find source " + source)


# ==> FAVORITES
@eel.expose
def get_favorites(filter=""):
    favorites = save.get("favorites")
    logger.info("save: loaded favorites")
    if filter:
        favorites = [favorite for favorite in favorites if filter in favorite["id"]]
    return favorites


@eel.expose
def get_favorites_id():
    favorites = save.get("favorites")
    logger.info("save: loaded favorites ids")
    if favorites:
        favorites = [favorite["id"] for favorite in favorites]
    return favorites


@eel.expose
def add_to_favorites(manga):
    favorites = save.get("favorites")
    logger.info('save: adding to favorites"' + manga["id"] + '"')
    if current_api.is_id_valid(manga["id"]):
        if favorites:
            if manga not in favorites:
                favorites.append(manga)
        else:
            favorites = [
                manga,
            ]

        save.set({"favorites": favorites})
        return True
    else:
        logger.error('save: failed to add "' + manga["id"] + '" to favorites')
        return False


@eel.expose
def remove_from_favorites(manga):
    favorites = save.get("favorites")
    logger.info('save: removing from favorites"' + str(manga) + '"')
    for favorite in favorites:
        if manga["id"] == favorite["id"]:
            favorites.remove(manga)
            save.set({"favorites": favorites})
            return True
    logger.error('save: failed to remove  "' + manga["id"] + '" to favorites')


@eel.expose
def display_favorites(filter):
    favorites = save.get("favorites")
    logger.info("save: loaded favorites")
    eel.add_results(favorites)


# ==> DOWNLOAD


@eel.expose
def get_current_downloads():
    logger.info("main: loaded downloads")
    return [e.status for e in current_api.downloader.get_all()]


@eel.expose
def download_group(chapters: list, manga: str, group: int):
    logger.info(
        f"threads: starting thread to download chapters {chapters} from {manga}"
    )
    th = current_api.downloader(
        chapters=chapters,
        manga_id=manga,
        current_api=current_api,
        group=group,
        display=eel.diplay_inividual_chapter_progresion,
    )
    th.start()


@eel.expose
def stop_download(th_id):
    th = current_api.downloader.get_by_id(th_id)
    if th:
        th.stop()
        logger.info(f"threads: stopped thread {th_id}")
    else:
        logger.warning(f"threads: no matching thread for {th_id}")


@eel.expose
def reveal_file(path):
    if path:
        logger.info(f"system: revealing file {path}")
        if platform.system() == "Windows":
            subprocess.Popen("explorer /select," + path, shell=True)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


eel.init("public")
eel.start(
    "html/index.html",
    cmdline_args=["--incognito"],
    jinja_templates="html",
    mode="auto",
)
