from logging import log
import colorlog

formatter = colorlog.ColoredFormatter(
    "[%(log_color)s%(levelname)-8s%(reset)s][%(name)-8s] %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
handler = colorlog.StreamHandler()
handler.setFormatter(formatter)


def title_formatter(r):
    title, *msg = r.msg.split(": ")
    r.msg = ": ".join(msg)
    r.name = title
    return r


logger = colorlog.getLogger('test')
logger.addHandler(handler)
logger.addFilter(title_formatter)


def get_logger():
    return logger


logger.setLevel("DEBUG")
