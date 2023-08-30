import logging

from envvarname import EnvVarName
from tweepy import Client
from util import getEnvVar, isEmpty


class TwitterUtil(object):

    LOGGER = logging.getLogger()

    def __init__(self):
        # Do not instantiate
        return


    @staticmethod
    def tweet(message: str) -> None:
        try:
            api = TwitterUtil.createTwitterAPI()
            api.create_tweet(text=message)
        except Exception:
            TwitterUtil.LOGGER.exception("Problem occurned while tweeting message")


    @staticmethod
    def createTwitterAPI() -> Client:
        TwitterUtil.LOGGER.debug("Creating the Twitter API")

        consumer_key = getEnvVar(EnvVarName.TWITTER_CONSUMER_KEY)
        if (isEmpty(consumer_key)):
            message = "Environment Variable " + EnvVarName.TWITTER_CONSUMER_KEY.name + " is not set"
            TwitterUtil.LOGGER.error(message)
            raise RuntimeError(message)

        consumer_secret = getEnvVar(EnvVarName.TWITTER_CONSUMER_SECRET)
        if (isEmpty(consumer_secret)):
            message = "Environment Variable " + EnvVarName.TWITTER_CONSUMER_SECRET.name + " is not set"
            TwitterUtil.LOGGER.error(message)
            raise RuntimeError(message)

        access_token = getEnvVar(EnvVarName.TWITTER_ACCESS_TOKEN)
        if (isEmpty(access_token)):
            message = "Environment Variable " + EnvVarName.TWITTER_ACCESS_TOKEN.name + " is not set"
            TwitterUtil.LOGGER.error(message)
            raise RuntimeError(message)

        access_token_secret = getEnvVar(EnvVarName.TWITTER_ACCESS_TOKEN_SECRET)
        if (isEmpty(access_token_secret)):
            message = "Environment Variable " + EnvVarName.TWITTER_ACCESS_TOKEN_SECRET.name + " is not set"
            TwitterUtil.LOGGER.error(message)
            raise RuntimeError(message)
        
        bearer_token = getEnvVar(EnvVarName.TWITTER_BEARER_TOKEN)
        if (isEmpty(bearer_token)):
            message = "Environment Variable " + EnvVarName.TWITTER_BEARER_TOKEN.name + " is not set"
            TwitterUtil.LOGGER.error(message)
            raise RuntimeError(message)

        client = Client(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret,
                        bearer_token=bearer_token)
        TwitterUtil.LOGGER.info("Twitter API created successfully")
        return client
