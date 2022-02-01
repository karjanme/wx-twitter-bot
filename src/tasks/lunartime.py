import json
import logging
import threading

from const import DATA_FILE_EXT, UTC
from datetime import datetime, time, timedelta
from envvarname import EnvVarName
from pathlib import Path
from pylunar import MoonInfo
from pytz import timezone, utc
from time import sleep
from twitter import TwitterUtil
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
        lunar_time_now = self._getLunarTime(self.now, True)
        if (lunar_time_now["transit"] < self.now):
            lunarTimeTomorrow = self._getLunarTimeTomorrow(self.now)
            return self._getLunarTime(lunarTimeTomorrow["transit"], True)

        return self._getLunarTime(lunar_time_now["transit"], True)


    def _getLunarTime(self, asOf: datetime, doFinalCorrections: bool) -> Dict:
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
        moon_times = moon_info.rise_set_times(self._timezone_str)
        return self._getLunarTimeFromMoonTimes(moon_times, asOf, moon_info.fractional_phase(), doFinalCorrections)


    def _getLunarTimeFromMoonTimes(self,
                                   moonTimes: list,
                                   asOf: datetime,
                                   fractPhase: float,
                                   doFinalCorrections: bool) -> Dict:
        lunarTimeDict = {
            "asOf": asOf,
            "rise": None,
            "transit": None,
            "fraction": fractPhase,
            "set": None
        }

        for moonTime in moonTimes:
            infoType = moonTime[0]
            infoTuple = moonTime[1]
            if (infoType == "rise" and type(infoTuple) is tuple):
                lunarTimeDict["rise"] = tupleToDateTime(infoTuple, self._tzone)
            if (infoType == "transit" and type(infoTuple) is tuple):
                lunarTimeDict["transit"] = tupleToDateTime(infoTuple, self._tzone)
            if (infoType == "set" and type(infoTuple) is tuple):
                lunarTimeDict["set"] = tupleToDateTime(infoTuple, self._tzone)

        # Fixes for lunar times that do not occur on the asOf date
        if ((lunarTimeDict["rise"] is None)
         or (lunarTimeDict["transit"] is None)
         or (lunarTimeDict["set"] is None)):
            tomorrowLunarTime = self._getLunarTimeTomorrow(asOf)
            if (lunarTimeDict["rise"] is None):
                lunarTimeDict["rise"] = tomorrowLunarTime["rise"]
            if (lunarTimeDict["transit"] is None):
                lunarTimeDict["transit"] = tomorrowLunarTime["transit"]
            if (lunarTimeDict["set"] is None):
                lunarTimeDict["set"] = tomorrowLunarTime["set"]

        # Final corrections (only is prescribed)
        if (doFinalCorrections):
            if (lunarTimeDict["rise"] > lunarTimeDict["transit"]):
                yesterdayLunarTime = self._getLunarTimeYesterday(asOf)
                lunarTimeDict["rise"] = yesterdayLunarTime["rise"]
            if (lunarTimeDict["set"] < lunarTimeDict["transit"]):
                tomorrowLunarTime = self._getLunarTimeTomorrow(asOf)
                lunarTimeDict["set"] = tomorrowLunarTime["set"]

        return lunarTimeDict


    def _getLunarTimeYesterday(self, asOfToday: datetime) -> Dict:
        yesterdayDate = asOfToday.date() - timedelta(days=1)
        yesterdayDateTime = self._tzone.localize(datetime.combine(yesterdayDate, time(23,59,59)))
        return self._getLunarTime(yesterdayDateTime, False)


    def _getLunarTimeTomorrow(self, asOfToday: datetime) -> Dict:
        tomorrowDate = asOfToday.date() + timedelta(days=1)
        tomorrowDateTime = self._tzone.localize(datetime.combine(tomorrowDate, time()))
        return self._getLunarTime(tomorrowDateTime, False)


    def _tweetLunarTime(self, lunar_time) -> None:
        message = self._MESSAGE_TEMPLATE.format(
            self._location_str,
            str(round(100 * lunar_time["fraction"])),
            lunar_time["rise"].strftime(self._TIME_FORMAT),
            lunar_time["set"].strftime(self._TIME_FORMAT)
        )
        self.LOGGER.info("A message will be tweeted!")
        self.LOGGER.info(message)
        TwitterUtil.tweet(message)


    def _sleep(self, moonrise: datetime) -> None:
        seconds_until_moonrise = (moonrise - self.now).total_seconds()

        if (seconds_until_moonrise > self._THRESHOLD_SECONDS):
            self.LOGGER.info("Sleeping until later this time")
            sleep_seconds = seconds_until_moonrise - self._THRESHOLD_SECONDS
        else:
            self.LOGGER.info("Sleeping until next time")
            next_lunar = moonrise + timedelta(days=1)
            lunar_time_next = self._getLunarTime(next_lunar, False)
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
