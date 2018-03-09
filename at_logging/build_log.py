import logging
from os import getcwd

_FORMAT_STR = u'%(levelname)-8s [%(asctime)s] %(message)s'

_LOG = logging.getLogger("build_log")
_LOG.setLevel(logging.INFO)

file_handler = logging.FileHandler(getcwd() + "/logs/build.log")
file_handler.setFormatter(logging.Formatter(_FORMAT_STR))
_LOG.addHandler(file_handler)


def write(line):
    _LOG.info(line)