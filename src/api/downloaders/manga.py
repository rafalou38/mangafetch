import os

import pdfManip
from myLog import logger
from . import dict_chunk, downloader, ClosedThread


class manga_downloader(downloader):
    def __init__(
        self,
        chapters: list,
        manga_id: str,
        group: int,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.group = group
        self.manga_id = manga_id
        self.chapters = chapters
        self.chapters.sort()

        self._bookmarks = {}
        self._pages = {}
        self._pages_count = 0

        if len(self.chapters) != 1:
            self.task_id = f"download {self.manga_id} chapters {self.chapters[0]} to {self.chapters[-1:][0]}"
        else:
            self.task_id = f"download {self.manga_id} chapter {self.chapters[0]}"

    def run(self):
        try:
            self.__class__._current_downloads.append(self)

            logger.info(f"download: " + self.task_id)
            self.info = self.api.get_info(self.manga_id)

            self.chek_running()

            logger.debug("download: getting pages")
            self._pages_count, self._pages = self._get_pages()

            self.chek_running()

            logger.debug("download: downloading pages")
            self._download_pages()

            self.chek_running()

            logger.debug("download: merging pdf")
            self._merge_pages()

            self.chek_running()

            if self.OUT_FILE:
                self.set_status("finished", 1, self.OUT_FILE)
            else:
                self.set_status("finished", 1)
            logger.info(f"download: finished " + self.task_id)

            # self._remove()
        except ClosedThread:
            return

    def _get_pages(self):

        self.set_status("getting pages")

        all_pages = {}
        pages_cnt = 0
        for chapter in self.chapters:  # get page's info for each chapter
            self.chek_running()
            cu_pages = self.api.get_pages(chapter, self.manga_id)
            pages_cnt += len(cu_pages)
            all_pages[chapter] = cu_pages
        return pages_cnt, all_pages

    def _download_pages(self):

        c_page = 0
        for chapter in sorted(self.chapters, key=float):
            self._bookmarks[chapter] = []
            pages = self._pages[chapter]
            logger.debug(f"download: chapter {chapter}")
            for file in self.api.download_chapter(chapter, self.manga_id, pages):
                self.chek_running()
                c_page += 1
                logger.debug(f"download: page {c_page}/{self._pages_count}")
                self._bookmarks[chapter].append(file)
                self.set_status(
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
            filepath = os.path.join(self.out_path, self.manga_id)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            self.OUT_FILE = os.path.join(
                filepath,
                filename,
            )
            for _ in pdfManip.mergeBookmarks(book, self.OUT_FILE):
                self.chek_running()

                ci += 1
                self.set_status(f"merging pdf", min(((ci / len(total)) / 2) + 0.5, 0.9))
