import json
import logging
import threading

from const import DATA_FILE_EXT, UTC
from datetime import datetime, timedelta
from envvarname import EnvVarName
from pathlib import Path
from pylunar import MoonInfo
from pytz import timezone, utc
from time import sleep
from typing import Dict
from util import decToDegMinSec, getEnvVar, initDataDir, isEmpty, tupleToDateTime


class LunarTimeTask(object):

    LOGGER = logging.getLogger()
    _TASK_NAME = "lunartime"
    _TIME_FORMAT = "%I:%M %p"
    _MESSAGE_TEMPLATE = "Hello {}! The moon will be {}% illuminated. Moonrise is at {} and Moonset is at {}."
    _THRESHOLD_SECONDS = 3600

    def __init__(self):
        """
        Constructor for the Lunar Time Task. This task is responsible for
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
                    rise_from_file = datetime.fromisoformat(lunar_time_from_file["rise"])
                    self._sleep(moonrise_current)
                    continue

            threshold_before_moonrise_current = moonrise_current - timedelta(seconds=self._THRESHOLD_SECONDS)
            if (self.now < threshold_before_moonrise_current or moonrise_current < self.now):
                self.LOGGER.info("Now is not within the threshold before moonrise")
                self._sleep(moonrise_current)
                continue

            self._tweetLunarTime(lunar_time_current)
            self._saveLunarTime(lunar_time_current)
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


    def _getLunarTimeCurrent(self) -> Dict:
        lunar_time_now = self._getLunarTime(self.now)
        return self._getLunarTime(lunar_time_now["transit"])


    def _getLunarTime(self, asOf: datetime) -> Dict:
        utcAsOf = utc.normalize(asOf)
        utcAsOfTuple = (
            utcAsOf.year,
            utcAsOf.month,
            utcAsOf.day,
            utcAsOf.hour,
            utcAsOf.minute,
            utcAsOf.second
        )
        moon_info = MoonInfo(self._latitude_dms, self._longitude_dms)
        moon_info.update(utcAsOfTuple)
        lunarInfos = moon_info.rise_set_times(UTC)
        lunarTimeDict = {
            "asOf": asOf,
            "rise": None,
            "transit": None,
            "fraction": moon_info.fractional_phase(),
            "set": None
        }
        for lunarInfo in lunarInfos:
            infoType = lunarInfo[0]
            infoTuple = lunarInfo[1]
            if (infoType == "rise" and type(infoTuple) is tuple):
                lunarTimeDict["rise"] = tupleToDateTime(infoTuple, utc, self._tzone)
            if (infoType == "transit" and type(infoTuple) is tuple):
                lunarTimeDict["transit"] = tupleToDateTime(infoTuple, utc, self._tzone)
            if (infoType == "set" and type(infoTuple) is tuple):
                lunarTimeDict["set"] = tupleToDateTime(infoTuple, utc, self._tzone)
        return lunarTimeDict


    def _tweetLunarTime(self, lunar_time) -> None:
        message = self._MESSAGE_TEMPLATE.format(
            self._location_str,
            str(round(100 * lunar_time["fraction"])),
            lunar_time["rise"].strftime(self._TIME_FORMAT),
            lunar_time["set"].strftime(self._TIME_FORMAT)
        )
        self.LOGGER.info("A message will be tweeted!")
        self.LOGGER.info(message)
        #TwitterUtil.tweet(message)  # TODO: enable after testing is complete


    def _sleep(self, moonrise: datetime) -> None:
        seconds_until_moonrise = (moonrise - self.now).total_seconds()

        if (seconds_until_moonrise > self._THRESHOLD_SECONDS):
            self.LOGGER.info("Sleeping until later this time")
            sleep_seconds = seconds_until_moonrise - self._THRESHOLD_SECONDS
        else:
            self.LOGGER.info("Sleeping until next time")
            next_lunar = moonrise + timedelta(days=1)
            lunar_time_next = self._getLunarTime(next_lunar)
            moonrise_next = lunar_time_next["rise"]
            seconds_until_moonrise_next = (moonrise_next - self.now).total_seconds()
            sleep_seconds = seconds_until_moonrise_next - self._THRESHOLD_SECONDS

        self.LOGGER.info("Sleep for {:.0f} seconds".format(sleep_seconds))
        sleep(sleep_seconds)


    def _loadLunarTime(self) -> Dict:
        filePath = Path(self._data_dir + self._TASK_NAME + DATA_FILE_EXT)
        filePath.touch(exist_ok=True)
        with open(filePath, 'r') as fp:
            try: 
                # TODO: convert datetime string into datetime object
                lunar_time = json.load(fp)
                return lunar_time
            except:
                return None


    def _saveLunarTime(self, lunar_time: Dict) -> None:
        fw = open(self._data_dir + self._TASK_NAME + DATA_FILE_EXT, 'w+')
        json.dump(lunar_time, fw, default=self._dumpConverter, indent=2)
        fw.close()


    def _dumpConverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
