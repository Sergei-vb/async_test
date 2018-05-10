"""Logging of images building output."""
import logging
from os import getcwd
from pathlib import Path

_LOGNAME = "build_log"
_LOGDIR = getcwd() + "/logs/"

_FORMAT_STR = u'%(levelname)-8s [%(asctime)s] %(message)s'

Path(_LOGDIR).mkdir(parents=True, exist_ok=True)

_FILE_HANDLER = logging.FileHandler(_LOGDIR + _LOGNAME + ".log")
_FILE_HANDLER.setFormatter(logging.Formatter(_FORMAT_STR))

APP_LOG = logging.getLogger(_LOGNAME)
APP_LOG.addHandler(_FILE_HANDLER)
APP_LOG.propagate = False
