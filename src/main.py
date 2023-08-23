import argparse
import logging
import os
import threading
import time
import signal
import sys

from datetime import datetime
from pathlib import Path
from pytz import timezone, utc

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

from const import APP_ROOT_DEFAULT
from envvarname import EnvVarName
from tasks.lunartime import LunarTimeTask
from tasks.solartime import SolarTimeTask
from util import getEnvVar, getLogDir, isEmpty, loadEnvVars


def createLogger():
    log_directory = getLogDir()
    log_filename = Path.joinpath(log_directory, "wxtwitterbot.log")
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    log_format = "%(asctime)s | %(threadName)-12.12s | %(levelname)-8.8s | %(message)s"

    log_level = getEnvVar(EnvVarName.LOG_LEVEL)
    if (log_level is None):
        log_level = logging.INFO  # Default logging level
    else:
        log_level = log_level.upper()

    logging.Formatter.converter = loggingFormatterTZ
    logging.basicConfig(
        filename=log_filename,
        format=log_format,
        level=log_level)
    return logging.getLogger()


def loggingFormatterTZ(*args):
    tzString = getEnvVar(EnvVarName.TIMEZONE)
    tz = utc
    if (not isEmpty(tzString)):
        tz = timezone(tzString)
    return datetime.now(tz).timetuple()


def sigintHandler(sig, frame):
    LOGGER.info("Shutting down, goodbye!")
    sys.exit(0)


def threadExceptionHook(args):
    LOGGER.error(str(args.exc_value))


### MAIN ###
parser = argparse.ArgumentParser()
parser.add_argument('--app-root', type=Path, default=APP_ROOT_DEFAULT, help='path to application root directory')
args = parser.parse_args()
loadEnvVars(args.app_root)
LOGGER = createLogger()  # Requires that environment variables are loaded
threading.excepthook = threadExceptionHook
signal.signal(signal.SIGINT, sigintHandler)

LOGGER.info("Application initialization complete!")

SolarTimeTask()
LunarTimeTask()

LOGGER.info("All tasks have been delegated to background threads.")

while True:
    # Keep this thread alive so it can be used to terminate the application
    time.sleep(1)
