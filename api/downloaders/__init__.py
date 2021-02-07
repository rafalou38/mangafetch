import threading
from typing import List, Type


class ClosedThread(Exception):
    pass


class downloader(threading.Thread):
    _current_downloads: List["downloader"] = []

    def __init__(self, capi: Type["website"], display: callable, out_path: str = "out"):
        super().__init__()
        self.out_path = out_path
        self.th_id = id(self)
        self._running = True
        self.api = capi
        self._display = display
        self.status = {}
        self.info = {}
        self.task_id = ""

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

    def chek_running(self):
        if not self._running:
            if self in self.__class__._current_downloads:
                self.__class__._current_downloads.remove(self)
            raise ClosedThread()

    def set_status(self, name="", percent=0.0, out=""):
        self.status = {
            "th_id": self.th_id,
            "id": self.task_id,
            "cover": self.info["cover"],
            "name": name,
            "percent": percent,
            "out": out,
        }
        self._display(self.status)


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
