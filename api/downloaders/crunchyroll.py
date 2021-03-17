import os

import youtube_dl

import pdfManip
from myLog import logger
from . import dict_chunk, downloader, ClosedThread


class manga_downloader(downloader):
    def __init__(
        self,
        urls: list,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.quality = quality
        self.urls = urls

        self._bookmarks = {}
        self._pages = {}
        self._pages_count = 0

        if len(self.chapters) != 1:
            self.task_id = f"download {self.manga_id} chapters {self.chapters[0]} to {self.chapters[-1:][0]}"
        else:
            self.task_id = f"download {self.manga_id} chapter {self.chapters[0]}"

        self.ydl_opts = {
            "format": "worst/worst",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "logger": logger,
            "progress_hooks": [self.handle_change],
            "hls_prefer_native": True,
        }

    def handle_change(self, data):
        self.out_file = data["filename"]
        percent = data["downloaded_bytes"] / data["total_bytes_estimate"]
        self.set_status(data["status"], percent, data["filename"])

    def run(self):
        try:
            self.__class__._current_downloads.append(self)

            from .. import OUT_PATH

            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(
                    self.urls
                )

            logger.info(f"download: finished " + self.task_id)
        except ClosedThread:
            return
