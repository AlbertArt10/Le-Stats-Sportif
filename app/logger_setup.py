"""Modul care definește setup-ul pentru logger-ul aplicației web Flask."""

import logging
from logging.handlers import RotatingFileHandler
from time import gmtime, strftime
import os

def setup_logger():
    """Configurează și returnează un logger cu RotatingFileHandler și timestamp în UTC."""
    logger = logging.getLogger("webserver")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Ștergem handler-ele existente
    if logger.hasHandlers():
        logger.handlers.clear()

    # Setăm handler-ul cu o dimensiune maximă de 1 MB și 5 backup-uri
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, "..")
    log_path = os.path.join(project_root, "webserver.log")

    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)

    # Cream un formatter care folosește gmtime pentru timestamp-uri în UTC
    class UTCFormatter(logging.Formatter):
        """Formatter care scrie timestamp-urile în format UTC."""
        def formatTime(self, record, datefmt=None):
            ct = gmtime(record.created)
            if datefmt:
                s = strftime(datefmt, ct)
            else:
                t = strftime("%Y-%m-%d %H:%M:%S", ct)
                s = "%s,%03d" % (t, record.msecs)  # pylint: disable=consider-using-f-string
            return s

    formatter = UTCFormatter(
        fmt="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
