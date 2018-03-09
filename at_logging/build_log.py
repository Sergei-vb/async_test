import logging
from os import getcwd
from pathlib import Path

_LOGNAME = "build_log"
_LOGDIR = getcwd() + "/logs/"

_FORMAT_STR = u'%(levelname)-8s [%(asctime)s] %(message)s'

_LOG = logging.getLogger(_LOGNAME)
_LOG.setLevel(logging.INFO)

Path(_LOGDIR).mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(_LOGDIR + _LOGNAME + ".log")
file_handler.setFormatter(logging.Formatter(_FORMAT_STR))
_LOG.addHandler(file_handler)


def write(line):
    _LOG.info(line)