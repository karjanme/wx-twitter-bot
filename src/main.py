import logging
import os
import threading
import signal
import sys

from envvarname import EnvVarName
from tweepy import API, OAuthHandler
from tasks.solartime import SolarTimeTask
from util import getEnvVar, isEmpty, loadEnvVars


def createLogger():
    log_directory = getEnvVar(EnvVarName.LOG_DIR)
    if (not(log_directory.endswith("/"))):
        log_directory += "/"
    log_filename = log_directory + "wxtwitterbot.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    logging.basicConfig(
        filename=log_filename,
        format="%(asctime)s | %(threadName)-12.12s | %(levelname)-8.8s | %(message)s",
        level=logging.INFO)
    return logging.getLogger()


def createTwitterAPI():
    LOGGER.debug("Crearing the Twitter API")

    consumer_key = getEnvVar(EnvVarName.TWITTER_CONSUMER_KEY)
    if (isEmpty(consumer_key)):
        message = "Environment Variable " + EnvVarName.TWITTER_CONSUMER_KEY + " is not set"
        LOGGER.error(message)
        raise RuntimeError(message)

    consumer_secret = getEnvVar(EnvVarName.TWITTER_CONSUMER_SECRET)
    if (isEmpty(consumer_secret)):
        message = "Environment Variable " + EnvVarName.TWITTER_CONSUMER_SECRET + " is not set"
        LOGGER.error(message)
        raise RuntimeError(message)

    access_token = getEnvVar(EnvVarName.TWITTER_ACCESS_TOKEN)
    if (isEmpty(access_token)):
        message = "Environment Variable " + EnvVarName.TWITTER_ACCESS_TOKEN + " is not set"
        LOGGER.error(message)
        raise RuntimeError(message)

    access_token_secret = getEnvVar(EnvVarName.TWITTER_ACCESS_TOKEN_SECRET)
    if (isEmpty(access_token_secret)):
        message = "Environment Variable "+EnvVarName.TWITTER_ACCESS_TOKEN_SECRET + " is not set"
        LOGGER.error(message)
        raise RuntimeError(message)

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        LOGGER.error("Error creating Twitter API", exc_info=True)
        raise e

    LOGGER.info("Twitter API created successfully")
    return api


def sigintHandler(sig, frame):
    LOGGER.info("Shutting down, goodbye!")
    sys.exit(0)


def threadExceptionHook(args):
    LOGGER.error(str(args.exc_value))


### MAIN ###
loadEnvVars()
LOGGER = createLogger()  # Requires that environment variables are loaded
threading.excepthook = threadExceptionHook

twitterAPI = createTwitterAPI()

SolarTimeTask()

signal.signal(signal.SIGINT, sigintHandler)

while True:
    continue
