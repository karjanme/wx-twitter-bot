import json
import logging
import threading

from const import DATA_FILE_EXT
from datetime import datetime, timedelta
from envvarname import EnvVarName
from pathlib import Path
from pytz import timezone
from time import sleep
from twitter import TwitterUtil
from typing import Dict
from util import decToDegMinSec, generateHashtag, getEnvVar, initDataDir, isEmpty


class AirQualityTask(object):

    LOGGER = logging.getLogger()
    _TASK_NAME = "airquality"
    _TIME_FORMAT = "%I:%M %p"
    _MESSAGE_TEMPLATE = "Hello {}! The air quality has {} from {} to {}.{}"
    _EXECUTION_INTERVAL_SECONDS = 3600

    def __init__(self):
        """
        Constructor for the Air Quality Task. This task is responsible for
        determining the desired information to publish.
        """
        self._thread = threading.Thread(name=self._TASK_NAME, target=self._run, args=())
        self._thread.daemon = True                            # Daemonize thread
        self._thread.start()                                  # Start the execution


    def _run(self):
        self.LOGGER.info("Starting the '" + self._TASK_NAME + "' task")
        self._setup()

        """ Routine that runs forever """
        while True:
            self.now = self._tzone.localize(datetime.now())

            self.LOGGER.info("Getting lunar times for now {}".format(self.now.isoformat()))
            lunar_time_current = self._getLunarTimeCurrent()
            moonrise_current = lunar_time_current["rise"]

            # Get prior 'lunar_time' from the saved data file
            lunar_time_from_file = self._loadLunarTime()

            if (lunar_time_from_file):
                transit_from_file = datetime.fromisoformat(lunar_time_from_file["transit"])
                self.LOGGER.info("Got lunar times from file for {}".format(transit_from_file.isoformat()))
                if (transit_from_file == lunar_time_current["transit"]):
                    self.LOGGER.info("Current lunar times are the same as the file")
                    self._sleep(moonrise_current)
                    continue

            threshold_before_moonrise_current = moonrise_current - timedelta(seconds=self._THRESHOLD_SECONDS)
            if (self.now < threshold_before_moonrise_current or moonrise_current < self.now):
                self.LOGGER.info("Now is not within the threshold before moonrise")
                self._sleep(moonrise_current)
                continue

            self._tweetAirQuality(lunar_time_current)
            self._saveAirQuality(lunar_time_current)
            self._sleep(moonrise_current)


    def _setup(self):
        # Data Directory
        self._data_dir = initDataDir(self._TASK_NAME)

        # Latitude
        latitude_str = getEnvVar(EnvVarName.LATITUDE)
        if isEmpty(latitude_str):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LATITUDE.name)
        self._latitude_dms = decToDegMinSec(float(latitude_str))
        self.LOGGER.debug("Latitude = " + ','.join(map(str, self._latitude_dms)))

        # Longitude
        longitude_str = getEnvVar(EnvVarName.LONGITUDE)
        if isEmpty(longitude_str):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LONGITUDE.name)
        self._longitude_dms = decToDegMinSec(float(longitude_str))
        self.LOGGER.debug("Longitude = " + ','.join(map(str, self._longitude_dms)))

        # Location
        self._location_str = getEnvVar(EnvVarName.LOCATION)
        if isEmpty(self._location_str):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LOCATION.name)
        self.LOGGER.debug("Location = " + self._location_str)

        # Timezone
        self._timezone_str = getEnvVar(EnvVarName.TIMEZONE)
        if isEmpty(self._timezone_str):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.TIMEZONE.name)
        self._tzone = timezone(self._timezone_str)
        self.LOGGER.debug("Timezone = " + self._timezone_str)


    def _getAirQualityCurrent(self) -> Dict:
        return


    def _tweetAirQuality(self, air_quality) -> None:
        message = self._MESSAGE_TEMPLATE.format(
            self._location_str,
            "improved/declined",
            air_quality["prior_level"],
            air_quality["current_level"],
            generateHashtag()
        )
        self.LOGGER.info("A message will be tweeted!")
        self.LOGGER.info(message)
        TwitterUtil.tweet(message)


    def _sleep(self) -> None:
        sleep_seconds = self._EXECUTION_INTERVAL_SECONDS
        self.LOGGER.info("Sleep for {:.0f} seconds".format(sleep_seconds))
        sleep(sleep_seconds)


    def _loadAirQuality(self) -> Dict:
        filePath = Path.joinpath(self._data_dir, self._TASK_NAME + DATA_FILE_EXT)
        filePath.touch(exist_ok=True)
        with open(filePath, 'r') as fp:
            try: 
                # TODO: convert datetime string into datetime object
                air_quality = json.load(fp)
                return air_quality
            except:
                return None


    def _saveAirQuality(self, air_quality: Dict) -> None:
        fw = open(Path.joinpath(self._data_dir, self._TASK_NAME + DATA_FILE_EXT), 'w+')
        json.dump(air_quality, fw, default=self._dumpConverter, indent=2)
        fw.close()


    def _dumpConverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
