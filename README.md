# MangaFetch

MangaFetch is a material design app to download mangas from different sites

- [MangaFetch](#mangafetch)
  - [included websites](#included-websites)
  - [Install](#install)
  - [Screenshots](#screenshots)
    - [search view](#search-view)
    - [info view](#info-view)
    - [table](#table)

## included websites

| website                            | status         |
| ---------------------------------- | -------------- |
| [scansmangas.xyz](scansmangas.xyz) | ✅ working     |
| [scan-1.com](scan-1.com)           | ✅ working     |
| [scan-fr.cc](scan-fr.cc)           | ✅ working     |
| [crunchyroll.com](crunchyroll.com) | 🟨 no download |

## Install

first install the dependencies with

```shell
pip install -r requirements.txt
```

or

```shell
python install.py
```

then run it with

```shell
python main.py
```

## Screenshots

### search view

![main view](images/search.png)

---

### info view

![info view](images/details.png)

here you can get info about the manga or bookmark is, so it also appears in the bookmarks view

---

### table

![table](images/table.png)

On the table you can select all chapters, download individually, read or download directly.
You can also limit the displayed chapters

the group option is for how much chapters you want to put on each PDF.

---
