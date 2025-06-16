import logging
from colorlog import ColoredFormatter
from .color import *

red = '\x1b[31m'
green = '\x1b[32m'
yellow = '\x1b[33m'
blue = '\x1b[34m'
pink = '\x1b[35m'
cyan = '\x1b[36m'
reset = '\x1b[0m'
FORMATS = {
    "DEBUG": "green",
    "INFO": "blue",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red"
}
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

logger = None

def get_logger():
    global logger
    if not logger:
        LOGFORMAT = '[%(asctime)s] [%(log_color)s%(levelname)s%(reset)s] %(message)s'
        formatter = ColoredFormatter(LOGFORMAT, log_colors=FORMATS, datefmt="%H:%M:%S")
        logging.root.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        stream.setFormatter(formatter)
        logger = logging.getLogger('main')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(stream)

    return logger
