"""Logging of images building output."""
import logging
from os import getcwd
from pathlib import Path

_LOGNAME = "build_log"
_LOGDIR = getcwd() + "/logs/"

_FORMAT_STR = u'%(levelname)-8s [%(asctime)s] %(message)s'

_LOG = logging.getLogger(_LOGNAME)
_LOG.setLevel(logging.INFO)

Path(_LOGDIR).mkdir(parents=True, exist_ok=True)

FILE_HANDLER = logging.FileHandler(_LOGDIR + _LOGNAME + ".log")
FILE_HANDLER.setFormatter(logging.Formatter(_FORMAT_STR))
_LOG.addHandler(FILE_HANDLER)


def write(line):
    """Writes a line into logfile."""
    _LOG.info(line)
