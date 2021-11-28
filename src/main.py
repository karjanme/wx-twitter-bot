import logging
import os
import threading
import time
import signal
import sys

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

from envvarname import EnvVarName
from tasks.solartime import SolarTimeTask
from util import getEnvVar, isEmpty, loadEnvVars


def createLogger():
    log_directory = getEnvVar(EnvVarName.LOG_DIR)
    if isEmpty(log_directory):
        log_directory = "./log/"  # Default logging directory
    if not(log_directory.endswith("/")):
        log_directory += "/"

    log_filename = log_directory + "wxtwitterbot.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    log_format = "%(asctime)s | %(threadName)-12.12s | %(levelname)-8.8s | %(message)s"

    log_level = getEnvVar(EnvVarName.LOG_LEVEL)
    if (log_level is None):
        log_level = logging.INFO  # Default logging level
    else:
        log_level = log_level.upper()

    logging.basicConfig(
        filename=log_filename,
        format=log_format,
        level=log_level)
    return logging.getLogger()


def sigintHandler(sig, frame):
    LOGGER.info("Shutting down, goodbye!")
    sys.exit(0)


def threadExceptionHook(args):
    LOGGER.error(str(args.exc_value))


### MAIN ###
loadEnvVars()
LOGGER = createLogger()  # Requires that environment variables are loaded
threading.excepthook = threadExceptionHook

LOGGER.info("Application startup complete!")

SolarTimeTask()

signal.signal(signal.SIGINT, sigintHandler)

while True:
    # Keep this thread alive so it can be used to terminate the application
    time.sleep(1)
