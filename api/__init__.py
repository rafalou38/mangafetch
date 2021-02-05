from .scan_1_com import scan_1_com
from .scansmangas_xyz import scansmangas_xyz
from .crunchyroll import crunchyroll
from ._main import website

sources = {
    "crunchyroll.com": crunchyroll,
    "scansmangas.xyz": scansmangas_xyz,
    "scan-1.com": scan_1_com,
}
