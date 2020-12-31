import json
import logging
import os
import time
import threading

from astral import LocationInfo
from astral.sun import sun
from datetime import date, datetime, timedelta
from envvarname import EnvVarName
from pytz import timezone
from twitter import TwitterUtil
from typing import Dict
from util import getEnvVar, isEmpty


class SolarTimeTask(object):

    LOGGER = logging.getLogger()
    _FILE_EXT = ".json"
    _DATE_FORMAT = "%b %d, %Y"
    _TIME_FORMAT = "%I:%M %p"
    _MESSAGE_TEMPLATE = "Hello {}! Today is {}. Sunrise is at {}, Solar Noon is at {}, and Sunset is at {}."

    def __init__(self):
        """
        Constructor for the Solar Time Task. This task is responsible for
        determining the desired information to publish.
        """
        self._thread = threading.Thread(name="solartime", target=self._run, args=())
        self._thread.daemon = True                            # Daemonize thread
        self._thread.start()                                  # Start the execution


    def _run(self):
        self.LOGGER.info("Starting the '" + self._thread.name + "' task")
        self._setup()

        """ Routine that runs forever """
        while True:
            self.now = datetime.now(tz=self.location.timezone)
            self.today = self.now.date()

            self.LOGGER.info("Getting solar times for today {}".format(self.today.isoformat()))
            solar_time_today = sun(self.location.observer, date=self.today, tzinfo=self.location.timezone)

            # Get prior 'solar_time' from the saved data file
            solar_time_from_file = self._loadSolarTime()

            if (solar_time_from_file):
                noon_from_file = datetime.fromisoformat(solar_time_from_file["noon"])
                date_from_file = noon_from_file.date()
                self.LOGGER.info("Got solar times from file for date {}".format(date_from_file.isoformat()))
                if (self.today == date_from_file):
                    self.LOGGER.info("Today is the same as the date from the file")
                    self._sleep(solar_time_today)
                    continue

            sunrise_today = solar_time_today["sunrise"]
            one_hour_before_sunrise_today = sunrise_today - timedelta(hours=1)
            if (self.now < one_hour_before_sunrise_today or sunrise_today < self.now):
                self.LOGGER.info("Now is not within the hour before sunrise today")
                self._sleep(solar_time_today)
                continue

            self._tweetSolarTime(solar_time_today)
            self._saveSolarTime(solar_time_today)
            self._sleep(solar_time_today)


    def _setup(self):
        # Data Directory
        data_dir_root = getEnvVar(EnvVarName.DATA_DIR)
        if isEmpty(data_dir_root):
            data_dir_root = "./data/"  # Default data directory
        if not(data_dir_root.endswith("/")):
            data_dir_root += "/"

        self._data_dir = data_dir_root + self._thread.name + "/"

        if not(os.path.exists(self._data_dir)):
            os.makedirs(self._data_dir, exist_ok=True)

        # Region
        region = getEnvVar(EnvVarName.REGION)
        if isEmpty(region):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.REGION.name)

        # Timezone
        tz = timezone(getEnvVar(EnvVarName.TIMEZONE))
        if isEmpty(tz):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.TIMEZONE.name)

        # Latitude
        latitude = getEnvVar(EnvVarName.LATITUDE)
        if isEmpty(latitude):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LATITUDE.name)

        # Longitude
        longitude = getEnvVar(EnvVarName.LONGITUDE)
        if isEmpty(longitude):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LONGITUDE.name)

        # Location
        location = getEnvVar(EnvVarName.LOCATION)
        if isEmpty(location):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LOCATION.name)

        self.location = LocationInfo(location, region, tz, latitude, longitude)


    def _tweetSolarTime(self, solar_time: Dict) -> None:
        sunrise = solar_time["sunrise"]
        solar_time_date = sunrise.date()

        if (self.today != solar_time_date):
            self.LOGGER.warn("The solar times provided are not for today -- skip tweet message")
            return

        message = self._MESSAGE_TEMPLATE.format(
            self.location.name,
            self.today.strftime(self._DATE_FORMAT),
            solar_time["sunrise"].strftime(self._TIME_FORMAT),
            solar_time["noon"].strftime(self._TIME_FORMAT),
            solar_time["sunset"].strftime(self._TIME_FORMAT)
        )
        self.LOGGER.info("A message will be tweeted!")
        self.LOGGER.info(message)
        TwitterUtil.tweet(message)
        return


    def _sleep(self, solar_time_today: Dict) -> None:
        sunrise_today = solar_time_today["sunrise"]

        if (self.today != sunrise_today.date()):
            self.LOGGER.warn("The solar times provided are not for today")

        seconds_until_sunrise_today = (sunrise_today - self.now).total_seconds()

        if (seconds_until_sunrise_today > 3600):
            self.LOGGER.info("Sleeping until later today")
            sleep_seconds = seconds_until_sunrise_today - 3600
        else:
            self.LOGGER.info("Sleeping until tomorrow")
            tomorrow = self.today + timedelta(days=1)
            solar_time_tomorrow = sun(self.location.observer, date=tomorrow, tzinfo=self.location.timezone)
            sunrise_tomorrow = solar_time_tomorrow["sunrise"]
            seconds_until_sunrise_tomorrow = (sunrise_tomorrow - self.now).total_seconds()
            sleep_seconds = seconds_until_sunrise_tomorrow - 3600

        self.LOGGER.info("Sleep for {:.0f} seconds".format(sleep_seconds))
        time.sleep(sleep_seconds)


    def _loadSolarTime(self) -> Dict:
        with open(self._data_dir + "solartime" + self._FILE_EXT, 'r+') as fp:
            # TODO: convert datetime string into datetime object
            solar_time = json.load(fp)
            return solar_time


    def _saveSolarTime(self, solar_time: Dict) -> None:
        fw = open(self._data_dir + "solartime" + self._FILE_EXT, 'w+')
        json.dump(solar_time, fw, default=self._dumpConverter, indent=2)
        fw.close()


    def _dumpConverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
