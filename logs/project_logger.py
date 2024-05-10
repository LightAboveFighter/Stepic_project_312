import logging as log
from random import choice as ch
import string
import sys

def __generate_session_id__():
    id = ""
    for i in range(5):
        id += ch(string.ascii_lowercase)
    return id

def activate_logger(level):
    """ 'D' - Debug, 'I' - Info, 'W' - Warning, 'E' - Error, 'C' - Critical """
    match(level):
        case "D":
            level=log.DEBUG
        case "I":
            level=log.INFO
        case "W":
            level=log.WARNING
        case "E":
            level=log.ERROR
        case "C":
            level=log.CRITICAL
    log.getLogger("Current_logger")
    log.basicConfig(filename="logs/Current_session.log", filemode="w", level=level, format="%(asctime)s %(levelname)s: %(message)s")
    id = __generate_session_id__()
    log.info(f"Session [{id}] started")
    handler = log.StreamHandler(sys.stderr)
    formatter = log.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.getLogger().addHandler(handler)
    # log.basicConfig(filename="logs/All_sessions.log", filemode="a", level=level, format="%(asctime)s %(levelname)s SESSION: [%(message)s]")
