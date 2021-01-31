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
import functools

logger.setLevel("DEBUG")
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


def dict_chunk(in_dict, group):
    f = []
    d = {}
    for i, obj in enumerate(in_dict.items()):
        d[obj[0]] = obj[1]
        if not (i + 1) % int(group):
            f.append(d)
            d = {}
    else:
        if d:
            f.append(d)
    return f


@eel.expose
def search(query="", page=1):
    logger.info('api: searched "' + query + '"')
    result, pages = api.scansmangas_xyz.search(query, page)
    return result, pages


@eel.expose
def get_info(id):
    logger.info('api: got info for manga "' + id + '"')
    return api.scansmangas_xyz.get_info(id)


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
    if api.scansmangas_xyz.is_id_valid(manga["id"]):
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


class downloader(threading.Thread):
    _current_downloads: List["downloader"] = []

    def __init__(self, chapters: list, manga_id: str, group: int, capi: Type[api.website] = api.scansmangas_xyz):
        super().__init__()
        self.group = group
        self.manga_id = manga_id
        self.chapters = chapters
        self.th_id = id(self)
        self.chapters.sort()
        self._running = True
        self.api = capi

        #  not yet set
        self._info = {}
        self.status = {}
        self._bookmarks = {}
        self._pages = {}
        self._pages_count = 0

        if len(self.chapters) != 1:
            self.task_id = f"download {self.manga_id} chapters {self.chapters[0]} to {self.chapters[-1:][0]}"
        else:
            self.task_id = f"download {self.manga_id} chapter {self.chapters[0]}"

    @classmethod
    def get_all(cls) -> List["downloader"]:
        return cls._current_downloads

    @classmethod
    def get_by_id(cls, th_id) -> "downloader":
        for e in cls._current_downloads:
            if e.th_id == int(th_id):
                return e

    def stop(self):
        self._running = False

    def _remove(self):
        if self in self.__class__._current_downloads:
            self.__class__._current_downloads.remove(self)

    def _set_status(self, name="", percent=0.0, out=""):
        self.status = {
            "th_id": self.th_id,
            "id": self.task_id,
            "cover": self._info["cover"],
            "name": name,
            "percent": percent,
            "out": out,
        }
        eel.diplay_inividual_chapter_progresion(self.status)

    def run(self):
        self.__class__._current_downloads.append(self)

        logger.info(f"download: " + self.task_id)
        self._info = self.api.get_info(self.manga_id)

        if not self._running:  # check if the thread is stopped
            self._remove()
            return

        logger.debug("download: getting pages")
        self._pages_count, self._pages = self._get_pages()

        if not self._running:  # check if the thread is stopped
            self._remove()
            return

        logger.debug("download: downloading pages")
        self._download_pages()

        if not self._running:  # check if the thread is stopped
            self._remove()
            return

        logger.debug("download: merging pdf")
        self._merge_pages()

        if not self._running:  # check if the thread is stopped
            self._remove()
            return

        self._set_status("finished", 1, OUT_PATH)
        logger.info(f"download: finished " + self.task_id)

        self._remove()

    def _get_pages(self):

        self._set_status("getting pages")

        all_pages = {}
        pages_cnt = 0
        for chapter in self.chapters:  # get page's info for each chapter
            if not self._running:  # check if the thread is stopped
                self._remove()
                return
            cu_pages, img_url = self.api.get_pages(chapter, self.manga_id)
            pages_cnt += len(cu_pages)
            all_pages[chapter] = [cu_pages, img_url]
        return pages_cnt, all_pages

    def _download_pages(self):

        c_page = 0
        for chapter in self.chapters:
            self._bookmarks[chapter] = []
            pages, img_url = self._pages[chapter]
            logger.debug(f"download: chapter {chapter}")
            for file in self.api.download_chapter(
                chapter, self.manga_id, pages, img_url
            ):
                if not self._running:  # check if the thread is stopped
                    self._remove()
                    return
                c_page += 1
                logger.debug(f"download: page {c_page}/{self._pages_count}")
                self._bookmarks[chapter].append(file)
                self._set_status(
                    "downloading chapter" + str(chapter), c_page / self._pages_count / 2
                )

    def _merge_pages(self):
        ch = dict_chunk(self._bookmarks, self.group)
        total = [
            item for sublist in self._bookmarks.values() for item in sublist
        ]  # flatten files lists
        ci = 0
        for book in ch:
            if len(book.keys()) == 1:
                filename = f"{self.manga_id} - {str(list(book.keys())[0])}.pdf"
            else:
                filename = f"{self.manga_id} - {str(list(book.keys())[0])}-{str(list(book.keys())[-1:][0])}.pdf"
            OUT_FILE = os.path.join(
                OUT_PATH,
                filename,
            )
            for _ in pdfManip.mergeBookmarks(book, OUT_FILE):
                if not self._running:  # check if the thread is stopped
                    self._remove()
                    return

                ci += 1
                self._set_status(f"merging pdf", min(((ci / len(total)) / 2) + 0.5, 0.9))


@eel.expose
def get_current_downloads():
    logger.info("main: loaded downloads")
    # return list(download_steps.values())
    return [e.status for e in downloader.get_all()]


@eel.expose
def download_group(chapters: list, manga: str, group: int):
    # global threads
    logger.info(
        f"threads: starting thread to download chapters {chapters} from {manga}"
    )
    # e = threading.Event()
    # eid = id(e)
    # th = threading.Thread(
    #     name=f"download_chapters_{manga}_{chapters[0]}_to_{chapters[-1:]}",
    #     target=download_chapters_th,
    #     args=(e, chapters, manga, group, eid),
    # )
    # th.start()
    # threads[eid] = (e, th)
    th = downloader(chapters, manga, group, api.scansmangas_xyz)
    th.start()


@eel.expose
def stop_download(th_id):
    th = downloader.get_by_id(th_id)
    if th:
        th.stop()
        logger.info(f"threads: stopped thread {th_id}")
    else:
        logger.warning(f"threads: no matching thread for {th_id}")


@eel.expose
def reveal_file(path):
    logger.info(f"system: revealing file {path}")
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
eel.init("public")
eel.start("html/index.html", cmdline_args=["--incognito"], jinja_templates="html")
