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
from typing import Dict
from util import getEnvVar, isEmpty


class SolarTimeTask(object):

    LOGGER = logging.getLogger()
    _DATA_DIR = "./data/solartime/"
    _FILE_EXT = ".json"
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
        self._setup()

        """ Routine that runs forever """
        while True:
            # Get prior 'solar_time' from the saved data file
            solar_time_from_file = self._loadSolarTime()

            if (solar_time_from_file):
                noon_from_file = datetime.fromisoformat(solar_time_from_file["noon"])
                self.LOGGER.info("Got solar times from file for date {}".format(noon_from_file.date().isoformat()))

            now = datetime.now(tz=self.location.timezone)
            today = now.date()
            tomorrow = today + timedelta(days=1)

            self.LOGGER.info("Getting solar times for today {}".format(today.isoformat()))

            solar_time_today = sun(self.location.observer, date=today, tzinfo=self.location.timezone)
            sunrise_today = solar_time_today["sunrise"]
            
            print("Sunrise: " + sunrise_today.isoformat(timespec='seconds'))
            print("Noon:    " + solar_time_today["noon"].isoformat(timespec='seconds'))
            print("Sunset:  " + solar_time_today["sunset"].isoformat(timespec='seconds'))

            self._saveSolarTime(solar_time_today)

            #TODO: sub-routine to figure out sleep time
            seconds_until_sunrise_today = (sunrise_today - now).total_seconds()
            if (seconds_until_sunrise_today > 3600):
                self.LOGGER.info("Sleeping until later today")
                sleep_seconds = seconds_until_sunrise_today - 3600
            else:
                self.LOGGER.info("Sleeping until tomorrow")
                solar_time_tomorrow = sun(self.location.observer, date=tomorrow, tzinfo=self.location.timezone)
                sunrise_tomorrow = solar_time_tomorrow['sunrise']
                seconds_until_sunrise_tomorrow = (sunrise_tomorrow - now).total_seconds()
                sleep_seconds = seconds_until_sunrise_tomorrow - 3600

            self.LOGGER.info("Sleep for {:.0f} seconds".format(sleep_seconds))
            time.sleep(sleep_seconds)


    def _setup(self):
        location = getEnvVar(EnvVarName.LOCATION)
        region = getEnvVar(EnvVarName.REGION)
        tz = timezone(getEnvVar(EnvVarName.TIMEZONE))
        latitude = getEnvVar(EnvVarName.LATITUDE)
        longitude = getEnvVar(EnvVarName.LONGITUDE)

        if isEmpty(location):
            raise RuntimeError("Missing required environment variable: LOCATION")
        if isEmpty(region):
            raise RuntimeError("Missing required environment variable: REGION")
        if isEmpty(tz):
            raise RuntimeError("Missing required environment variable: TIMEZONE")
        if isEmpty(latitude):
            raise RuntimeError("Missing required environment variable: LATITUDE")
        if isEmpty(longitude):
            raise RuntimeError("Missing required environment variable: LONGITUDE")
        
        if not(os.path.exists(self._DATA_DIR)):
            os.makedirs(self._DATA_DIR)

        self.location = LocationInfo(location, region, tz, latitude, longitude)


    def _getTimeStringForMessage(self, date_time: str) -> str:
        return datetime.fromisoformat(date_time).strftime("%I:%M %p")


    def _loadSolarTime(self) -> Dict:
        with open(self._DATA_DIR + "solartime" + self._FILE_EXT, 'r+') as fp:
            solar_time = json.load(fp)
            return solar_time


    def _saveSolarTime(self, solar_time: Dict) -> None:
        fw = open(self._DATA_DIR + "solartime" + self._FILE_EXT, 'w+')
        json.dump(solar_time, fw, default=self._dumpConverter, indent=2)
        fw.close()


    def _dumpConverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
