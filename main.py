import eel
import api
import pdfManip
import pretty_errors
from pprint import pprint
from data import MagicSave
import os
import debug_values
import time
import threading
import platform
import subprocess

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
    print("searched", query)
    result, pages = api.search(query, page)
    return result, pages


@eel.expose
def get_info(id):
    print("get_info", id)
    return api.get_info(id)


# ==> FAVORITES
@eel.expose
def get_favorites(filter=""):
    favorites = save.get("favorites")
    if filter:
        favorites = [favorite for favorite in favorites if filter in favorite["id"]]
    return favorites


@eel.expose
def get_favorites_id():
    favorites = save.get("favorites")
    if favorites:
        favorites = [favorite["id"] for favorite in favorites]
    return favorites


@eel.expose
def add_to_favorites(manga):
    favorites = save.get("favorites")
    print("added to favorites : ", manga)
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
        print("failed")
        return False


@eel.expose
def remove_from_favorites(manga):
    favorites = save.get("favorites")
    print("remove from favorites : ", manga)
    for favorite in favorites:
        if manga["id"] == favorite["id"]:
            favorites.remove(manga)
            save.set({"favorites": favorites})
            return True
        print("failed to remove favorite", manga)


@eel.expose
def display_favorites(filter):
    favorites = save.get("favorites")
    eel.add_results(favorites)


# ==> DOWNLOAD


@eel.expose
def get_curent_downloads():
    return list(download_steps.values())


def download_chapter_th(event: threading.Event, chapter, manga_id, th_id):
    global download_steps
    OUT_FILE = os.path.join("out", f"{manga_id} - {str(chapter)}.pdf")
    # for step in debug_values.download_steps:
    #     if event.is_set():
    #         return
    #     step["th_id"] = th_id
    #     download_steps[step["id"]] = step
    #     eel.diplay_inividual_chapter_progresion(step)
    #     time.sleep(0.1)
    # return
    info = api.get_info(manga_id)
    cover = info["cover"]
    manga_id = info["id"]
    task_id = f"download_chapter_{chapter}_{manga_id}"
    event.manga_task_id = task_id
    files = []
    pages = api.get_pages(chapter, manga_id)
    for file in api.download_chapter(chapter, manga_id, pages):
        if event.is_set():
            print(download_steps)
            del download_steps[task_id]
            print(download_steps)
            print(task_id, "stoped")
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
            print(task_id, "stoped")
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
    print("th: download group", manga_id, chapters)
    info = api.get_info(manga_id)
    cover = info["cover"]
    manga_id = info["id"]
    task_id = f"download_chapters_{manga_id}_{chapters[0]}_to_{chapters[-1:]}"
    event.manga_task_id = task_id
    bookmarks = {}
    all_pages = {}
    pages_cnt = 0
    c_page = 0
    for chapter in chapters:
        cu_pages = api.get_pages(chapter, manga_id)
        pages_cnt += len(cu_pages)
        all_pages[chapter] = cu_pages
    for chapter in chapters:
        bookmarks[chapter] = []
        pages = all_pages[chapter]
        for file in api.download_chapter(chapter, manga_id, pages):
            c_page += 1
            if event.is_set():
                print(download_steps)
                del download_steps[task_id]
                print(download_steps)
                print(task_id, "stoped")
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

        # eel.diplay_inividual_chapter_progresion(
        # 	download_steps[task_id]
        # )

    OUT_FILE = os.path.join("out", f"{manga_id} - {str(chapter)}.pdf")
    for step in pdfManip.mergeBookmarks(bookmarks, OUT_FILE):
        if event.is_set():
            del download_steps[task_id]
            print(task_id, "stoped")
            return
        download_steps[task_id] = {
            "th_id": th_id,
            "id": f"chapter {chapter} {manga_id}",
            "cover": cover,
            "name": f"merging pdf",
            "percent": (step / 2) + 0.5,
            "out": "",
        }
        eel.diplay_inividual_chapter_progresion(download_steps[task_id])
        # eel.diplay_inividual_chapter_progresion(
        # 	download_steps[task_id]
        # )
        # print(download_steps[task_id]["name"], download_steps[task_id]["percent"])

    download_steps[task_id] = {
        "id": f"chapter {chapter} {manga_id}",
        "cover": cover,
        "name": f"finished",
        "percent": 1,
        "out": OUT_FILE,
    }
    # eel.diplay_inividual_chapter_progresion(download_steps[task_id])
    print(download_steps[task_id]["name"], download_steps[task_id]["percent"])

    # del download_steps[task_id]


@eel.expose
def download_group(chapters, manga):
    global threads
    print("download group", manga, chapters)
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
    threads[int(id)][0].set()
    del download_steps[threads[int(id)][0].manga_task_id]
    print("stoped", id)


@eel.expose
def reveal_file(path):
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
