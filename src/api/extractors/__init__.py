import os

from magic import magic

from ..downloaders.manga import manga_downloader


class Extractor:
    name = "website"
    downloader = manga_downloader

    @classmethod
    def search(cls, query="", page=1):
        pass

    @classmethod
    def get_info(cls, id):
        pass

    @classmethod
    def is_id_valid(cls, id):
        pass

    @classmethod
    def get_pages(cls, chapter, manga_id):
        pass

    @classmethod
    def download_chapter(cls, chapter, manga_id, pages=None, img_url=None):
        pass

    @classmethod
    def download_chapter(cls, chapter, manga_id, pages=None):
        from .. import init, IMG_PATH, session, logger

        init()
        tries = 0
        if pages is None:
            pages = cls.get_pages(chapter, manga_id)
        for page in pages:
            try:
                path = os.path.join(IMG_PATH, manga_id, str(chapter))
                r = session.get(page, stream=True)
                if not os.path.exists(path):
                    os.makedirs(path)
                buffer = r.iter_content(chunk_size=2048)
                chunk = next(buffer)
                mime = magic.from_buffer(chunk, mime=True)
                extension = os.path.split(mime)[1]
                filename = os.path.join(
                    path, os.path.splitext(os.path.split(page)[1])[0] + "." + extension
                )
                with open(filename, "wb") as f:
                    f.write(chunk + r.raw.read())
                yield filename
            except Exception as err:
                logger.error(
                    'api: failed downloading image from "' + page + '" : ' + repr(err)
                )
