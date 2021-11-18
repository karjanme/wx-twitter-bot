import json
import logging
import os
import time
import threading

from const import DATA_FILE_EXT
from datetime import date, datetime, timedelta
from envvarname import EnvVarName
from pylunar import MoonInfo
from pytz import timezone, utc
from typing import Dict
from util import decToDegMinSec, getEnvVar, initDataDir, isEmpty, tupleToDatetime


class LunarTimeTask(object):

    LOGGER = logging.getLogger()
    _TASK_NAME = "lunartime"
    _MESSAGE_TEMPLATE = "Hello {}! The moon will be {} illuminated. Moonrise is at {} and Moonset is at {}."

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
            tzone = timezone(self._timezone_str)
            now = datetime.now(tz=tzone)
            lunar_time_now = self._getLunarTime(now)
            print(now.isoformat())
            print(lunar_time_now)
            next_transit = lunar_time_now["transit"]
            lunar_time_next = self._getLunarTime(next_transit)
            print(next_transit.isoformat())
            print(lunar_time_next)
            for x in range(28):
                asOfDatetime = now + timedelta(days=x)
                #self._getLunarTime(asOfDatetime)
            self._sleep()


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
        self.LOGGER.debug("Timezone = " + self._timezone_str)


    def _getLunarTime(self, asOf: datetime) -> Dict:
        tzone = timezone(self._timezone_str)
        utcAsOf = asOf.astimezone(utc)
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
        lunarInfos = moon_info.rise_set_times(self._timezone_str)
        lunarTimeDict = {
            "asOf": utcAsOf,
            "rise": None,
            "transit": None,
            "fraction": moon_info.fractional_phase(),
            "set": None
        }
        for lunarInfo in lunarInfos:
            infoType = lunarInfo[0]
            infoTuple = lunarInfo[1]
            if (infoType == "rise" and type(infoTuple) is tuple):
                #print("rise: " + ",".join(map(str, infoTuple)))
                lunarTimeDict["rise"] = tupleToDatetime(infoTuple, tzone)
            if (infoType == "transit" and type(infoTuple) is tuple):
                #print("rise: " + ",".join(map(str, infoTuple)))
                lunarTimeDict["transit"] = tupleToDatetime(infoTuple, tzone)
            if (infoType == "set" and type(infoTuple) is tuple):
                #print("set: " + ",".join(map(str, infoTuple)))
                lunarTimeDict["set"] = tupleToDatetime(infoTuple, tzone)

        return lunarTimeDict


    def _tweetLunarTime(self) -> None:
        # TODO: the end goal!
        return


    def _sleep(self) -> None:
        # If tomorrow has a moonrise, then sleep until 1 hour before
        # If tomorrow does not have a moonrise, then sleep until noon tomorrow
        sleep_seconds = 60*60  # 1 hour (TODO: something better?)
        self.LOGGER.info("Sleep for {:.0f} seconds".format(sleep_seconds))
        time.sleep(sleep_seconds)


    def _loadLunarTime(self) -> Dict:
        with open(self._data_dir + self._TASK_NAME + DATA_FILE_EXT, 'r+') as fp:
            # TODO: convert datetime string into datetime object
            lunar_time = json.load(fp)
            return lunar_time


    def _saveSolarTime(self, lunar_time: Dict) -> None:
        fw = open(self._data_dir + self._TASK_NAME + DATA_FILE_EXT, 'w+')
        json.dump(lunar_time, fw, default=self._dumpConverter, indent=2)
        fw.close()


    def _dumpConverter(self, o):
        if isinstance(o, datetime):
            return o.__str__()
