import json
import logging
import threading

from airnowpy import API, Category, Observation
from const import DATA_FILE_EXT
from datetime import datetime, timedelta
from envvarname import EnvVarName
from pathlib import Path
from pytz import timezone
from time import sleep
from twitter import TwitterUtil
from typing import List
from util import generateHashtag, getEnvVar, initDataDir, isEmpty


class AirQualityTask(object):
    """
    This task is responsible for determining the desired information to publish.
    """

    LOGGER = logging.getLogger()
    _TASK_NAME = "airquality"
    _TIME_FORMAT = "%I:%M %p"
    _MESSAGE_TEMPLATE = "Hello {}! The air quality has {} from {} to {}.{}"
    _EXECUTION_INTERVAL_SECONDS = 360

    def __init__(self):
        """
        Constructor for the Air Quality Task. 
        """
        self._thread = threading.Thread(name=self._TASK_NAME, target=self._run, args=())
        self._thread.daemon = True                            # Daemonize thread
        self._thread.start()                                  # Start the execution


    def _run(self):
        self.LOGGER.info("Starting the '" + self._TASK_NAME + "' task")
        self._setup()

        """ Routine that runs forever """
        while True:
            self.now = datetime.now(tz=self._tzone)

            self.LOGGER.debug("Getting air quality for now {}".format(self.now.isoformat()))
            observations = self._getCurrentObservations()

            # Get prior 'air_quality' from the saved data file
            prior_air_quality = self._loadAirQualityFromFile()
            current_primary = self._getPrimaryObservation(observations)

            if (prior_air_quality is not None):
                has_category_changed = prior_air_quality.category.getValue() != current_primary.category.getValue()
                is_current_within_threshold_of_prior = prior_air_quality.timestamp + timedelta(hours=3) >= self.now
                if (has_category_changed and is_current_within_threshold_of_prior):
                    self._tweetAirQuality(prior_air_quality, current_primary)

            # Always save the current primary observation
            self._saveAirQuality(current_primary)

            # Go to sleep for a little while
            self._sleep()


    def _setup(self):
        # Data Directory
        self._data_dir = initDataDir(self._TASK_NAME)

        # Latitude
        latitude_str = getEnvVar(EnvVarName.LATITUDE)
        if isEmpty(latitude_str):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LATITUDE.name)
        self._latitude = float(latitude_str)
        self.LOGGER.debug("Latitude = " + latitude_str)

        # Longitude
        longitude_str = getEnvVar(EnvVarName.LONGITUDE)
        if isEmpty(longitude_str):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.LONGITUDE.name)
        self._longitude = float(longitude_str)
        self.LOGGER.debug("Longitude = " + longitude_str)

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

        # API Key
        self._api_key = getEnvVar(EnvVarName.AIRNOW_API_KEY)
        if isEmpty(self._api_key):
            raise RuntimeError("Missing required environment variable: " + EnvVarName.AIRNOW_API_KEY.name)
        self.LOGGER.debug("API Key = " + self._api_key)


    def _getCurrentObservations(self) -> List[Observation]:
        api = API(self._api_key)
        return api.getCurrentObservationByLatLon(self._latitude, self._longitude)


    def _getPrimaryObservation(self, observations: List[Observation]) -> Observation:
        # Determine the primary pollutant in the list of observations provided
        current_primary = None
        for obs in observations:
            if (current_primary is None):
                current_primary = obs
            elif (obs.aqiValue > current_primary.aqiValue):
                current_primary = obs
            elif (obs.aqiValue == current_primary.aqiValue):
                if (obs.parameterName > current_primary.parameterName):
                    current_primary = obs

        self.LOGGER.debug("Current primary pollutant is " + current_primary.parameterName)
        return current_primary


    def _tweetAirQuality(self, prior_observation: Observation, current_observation: Observation) -> None:
        type_of_change = ""
        if (current_observation.category.getValue() < prior_observation.category.getValue()):
            type_of_change = "improved"
        elif (current_observation.category.getValue() > prior_observation.category.getValue()):
            type_of_change = "worsened"
        else:
            self.LOGGER.warn("No change in category needs to be reported")
            return

        message = self._MESSAGE_TEMPLATE.format(
            self._location_str,
            type_of_change,
            prior_observation.category.getLabel(),
            current_observation.category.getLabel(),
            generateHashtag()
        )
        self.LOGGER.info("A message will be tweeted!")
        self.LOGGER.info(message)
        TwitterUtil.tweet(message)


    def _sleep(self) -> None:
        sleep_seconds = self._EXECUTION_INTERVAL_SECONDS
        self.LOGGER.debug("Sleep for {:.0f} seconds".format(sleep_seconds))
        sleep(sleep_seconds)


    def _loadAirQualityFromFile(self) -> Observation:
        filePath = Path.joinpath(self._data_dir, self._TASK_NAME + DATA_FILE_EXT)
        filePath.touch(exist_ok=True)
        with open(filePath, 'r') as fp:
            try: 
                air_quality = json.load(fp)
                return Observation(datetime.fromisoformat(air_quality["timestamp"]),
                                   air_quality["reportingArea"],
                                   air_quality["stateCode"],
                                   air_quality["latitude"],
                                   air_quality["longitude"],
                                   air_quality["parameterName"],
                                   air_quality["aqiValue"],
                                   Category.lookupByValue(air_quality["category"]))
            except:
                return None


    def _saveAirQuality(self, air_quality: Observation) -> None:
        fw = open(Path.joinpath(self._data_dir, self._TASK_NAME + DATA_FILE_EXT), 'w+')
        json.dump(air_quality.__dict__, fw, default=self._dumpConverter, indent=2)
        fw.close()


    def _dumpConverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
        if isinstance(o, Category):
            return o.getValue()
