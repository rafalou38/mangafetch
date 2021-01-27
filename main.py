import subprocess
import platform
import threading
import os
from data import MagicSave
import pretty_errors
import pdfManip
import api
import eel
from os.path import isdir
from myLog import logger
logger.setLevel("DEBUG")
logger.info("main: starting app")


logger.debug("import: eel")

logger.debug("import: api")

logger.debug("import: pdf")

logger.debug("import: pretty_errors")

# logger.debug("import: eel")
# from pprint import pprint
logger.debug("import: save")

logger.debug("import: os")

logger.debug("import: threading")

logger.debug("import: platform")

logger.debug("import: subprocess")


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
download_steps = {}
threads = {}


@eel.expose
def search(query="", page=1):
    logger.info("api: searched \"" + query+"\"")
    result, pages = api.search(query, page)
    return result, pages


@eel.expose
def get_info(id):
    logger.info("api: got info for manga \"" + id+"\"")
    return api.get_info(id)


# ==> FAVORITES
@eel.expose
def get_favorites(filter=""):
    favorites = save.get("favorites")
    logger.info("save: loaded favorites")
    if filter:
        favorites = [
            favorite for favorite in favorites if filter in favorite["id"]]
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
    logger.info("save: adding to favorites\"" + manga["id"]+"\"")
    if api.is_id_valid(manga["id"]):
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
        logger.error("save: failed to add \"" + manga["id"]+"\" to favorites")
        return False


@eel.expose
def remove_from_favorites(manga):
    favorites = save.get("favorites")
    logger.info("save: removing from favorites\"" + str(manga)+"\"")
    for favorite in favorites:
        if manga["id"] == favorite["id"]:
            favorites.remove(manga)
            save.set({"favorites": favorites})
            return True
    logger.error("save: failed to remove  \"" + manga["id"]+"\" to favorites")


@eel.expose
def display_favorites(filter):
    favorites = save.get("favorites")
    logger.info("save: loaded favorites")
    eel.add_results(favorites)


# ==> DOWNLOAD


@eel.expose
def get_curent_downloads():
    logger.info("api: loaded downloads")
    return list(download_steps.values())


def download_chapter_th(event: threading.Event, chapter, manga_id, th_id):
    global download_steps
    OUT_FILE = os.path.join("out", f"{manga_id} - {str(chapter)}.pdf")
    info = api.get_info(manga_id)
    cover = info["cover"]
    manga_id = info["id"]
    task_id = f"download_chapter_{chapter}_{manga_id}"
    event.manga_task_id = task_id
    files = []
    pages = api.get_pages(chapter, manga_id)
    for file in api.download_chapter(chapter, manga_id, pages):
        if event.is_set():
            del download_steps[task_id]
            return
        download_steps[task_id] = {
            "th_id": th_id,
            "id": f"chapter {chapter} {manga_id}",
            "cover": cover,
            "name": "downloading",
            "percent": int(os.path.splitext(os.path.split(file)[1])[0])
            / len(pages)
            / 2,
            "out": "",
        }
        eel.diplay_inividual_chapter_progresion(download_steps[task_id])

        files.append(file)

    for step in pdfManip.merge(files, OUT_FILE):
        if event.is_set():
            del download_steps[task_id]
            return
        download_steps[task_id] = {
            "th_id": th_id,
            "id": f"chapter {chapter} {manga_id}",
            "cover": cover,
            "name": f"merging pdf {manga_id} chapter {chapter}",
            "percent": (step / 2) + 0.5,
            "out": "",
        }
        eel.diplay_inividual_chapter_progresion(download_steps[task_id])
        download_steps[task_id] = {
            "id": f"chapter {chapter} {manga_id}",
            "cover": cover,
            "name": f"finished",
            "percent": 1,
            "out": OUT_FILE,
        }
    eel.diplay_inividual_chapter_progresion(download_steps[task_id])

    # del download_steps[task_id]


def download_chapters_th(event: threading.Event, chapters: list, manga_id, th_id):
    global download_steps

    logger.info(
        f"download: started download of {chapters} from {manga_id} in thread {th_id}")
    info = api.get_info(manga_id)
    cover = info["cover"]
    manga_id = info["id"]
    task_id = f"download_chapters_{manga_id}_{chapters[0]}_to_{chapters[-1:]}"
    event.manga_task_id = task_id
    bookmarks = {}
    all_pages = {}
    pages_cnt = 0
    c_page = 0
    logger.debug("download: getting pages")
    for chapter in chapters:
        cu_pages = api.get_pages(chapter, manga_id)
        pages_cnt += len(cu_pages)
        all_pages[chapter] = cu_pages
    logger.debug("download: downloading chapter")
    for chapter in chapters:
        bookmarks[chapter] = []
        pages = all_pages[chapter]
        logger.debug(f"download: chapter {chapter}")
        for file in api.download_chapter(chapter, manga_id, pages):
            c_page += 1
            logger.debug(f"download: page {c_page}/{len(pages)}")
            if event.is_set():
                del download_steps[task_id]
                return
            bookmarks[chapter].append(file)
            download_steps[task_id] = {
                "th_id": th_id,
                "id": f"download_chapters_{manga_id}_{chapters[0]}_to_{chapters[-1:]}",
                "cover": cover,
                "name": "downloading chapter" + str(chapter),
                "percent": c_page / pages_cnt / 2,
                "out": "",
            }
            eel.diplay_inividual_chapter_progresion(download_steps[task_id])

    logger.debug("download: merging pdf")
    OUT_FILE = os.path.join("out", f"{manga_id} - {str(chapter)}.pdf")
    for step in pdfManip.mergeBookmarks(bookmarks, OUT_FILE):
        if event.is_set():
            del download_steps[task_id]
            return
        download_steps[task_id] = {
            "th_id": th_id,
            "id": f"download_chapters_{manga_id}_{chapters[0]}_to_{chapters[-1:]}",
            "cover": cover,
            "name": f"merging pdf",
            "percent": (step / 2) + 0.5,
            "out": "",
        }
        eel.diplay_inividual_chapter_progresion(download_steps[task_id])

    download_steps[task_id] = {
        "id": f"download_chapters_{manga_id}_{chapters[0]}_to_{chapters[-1:]}",
        "cover": cover,
        "name": f"finished",
        "percent": 1,
        "out": OUT_FILE,
    }
    eel.diplay_inividual_chapter_progresion(download_steps[task_id])
    logger.info(
        f"download: finished download of {chapters} from {manga_id} in thread {th_id}")
    # del download_steps[task_id]


@eel.expose
def download_group(chapters, manga):
    global threads
    logger.info(
        f"threads: starting thread to download chapters {chapters} from {manga}")
    e = threading.Event()
    eid = id(e)
    th = threading.Thread(
        name=f"download_chapters_{manga}_{chapters[0]}_to_{chapters[-1:]}",
        target=download_chapters_th,
        args=(e, chapters, manga, eid),
    )
    th.start()
    threads[eid] = (e, th)


@eel.expose
def download_chapter(chapter, manga_id):
    global threads
    logger.info(
        f"threads: starting thread to download chapter {chapter} from {manga_id}")
    e = threading.Event()
    eid = id(e)
    th = threading.Thread(
        name=f"download_chapter_{chapter}_{manga_id}",
        target=download_chapter_th,
        args=(e, chapter, manga_id, eid),
    )
    th.start()
    threads[eid] = (e, th)


@eel.expose
def stop_download(id):
    logger.info(f"threads: stoped thread {id}")
    threads[int(id)][0].set()
    del download_steps[threads[int(id)][0].manga_task_id]


@eel.expose
def reveal_file(path):
    logger.info(f"system: revaealing file {path}")
    if platform.system() == "Windows":
        subprocess.Popen("explorer /select," + path, shell=True)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# download_group(
#     list(map(str, range(80, 91))),
#     "the-promised-neverland",
# )
# download_group(
#     list(map(str, range(91, 100))),
#     "the-promised-neverland",
# )
# input()
eel.init('public')
eel.start('html/index.html',
          cmdline_args=["--incognito"], jinja_templates="html")
