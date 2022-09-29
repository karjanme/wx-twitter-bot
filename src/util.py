import os

from const import APP_ROOT_DEFAULT
from datetime import datetime, MINYEAR, MAXYEAR
from dotenv import load_dotenv
from envvarname import EnvVarName
from pathlib import Path
from pytz import timezone


globalAppRootDir = APP_ROOT_DEFAULT


def loadEnvVars(appRootDir: Path) -> None:
    global globalAppRootDir
    globalAppRootDir = appRootDir
    load_dotenv(Path.joinpath(appRootDir, ".env"))


def getEnvVar(name: EnvVarName) -> str:
    """
    Retrieve the value of a specified environment variable.

    Parameters:
        name (EnvVarName): 

    Returns:
        string: 
    """

    value = os.getenv(name.value, None)
    return value


def isEmpty(value: str) -> bool:
    return value == "" or value is None


def decToDegMinSec(dd: float) -> tuple:
    """
    Converts decimal degrees to deg/min/sec.

    Parameters:
        dd (float): Decimal Degrees

    Returns:
        tuple: (degrees,minutes,seconds) of integers
    """

    isPositive = dd >= 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600, 60)
    degrees,minutes = divmod(minutes, 60)
    degrees = degrees if isPositive else -degrees

    return (round(degrees),round(minutes),round(seconds))


def initDataDir(dirName: str) -> Path:
    dataDir = Path.joinpath(globalAppRootDir, "data", dirName)

    if not(os.path.exists(dataDir)):
        os.makedirs(dataDir, exist_ok=True)

    return dataDir


def getLogDir() -> Path:
    return Path.joinpath(globalAppRootDir, "log")


def generateHashtag() -> str:
    hashtag = getEnvVar(EnvVarName.TWITTER_HASHTAG)
    if (isEmpty(hashtag)):
        return ""

    return " #" + hashtag


def tupleToDateTime(dtTuple: tuple, tzone: timezone) -> datetime:
    """
    Converts a given typle representation of a datetime into a datatime object.

    Parameterrs:
        dtTuple (tuple): A tuple representation of the datetime (YYYY, m, d, H, M, S)
        tzone (timezone): The timezone of the datetime represented by the tuple

    Returns:
        datetime: timezone aware representationn of the given tuple
    """

    if (len(dtTuple) != 6):
        raise ValueError("Tuple must contain 6 items (year, month, day, hour, minute, second)")

    # TODO: validation of each item in the tuple to ensure it is in the acceptable range for a datatime
    year = dtTuple[0]
    if (year < MINYEAR or MAXYEAR < year):
        raise ValueError("YEAR must be between (inclusive) " + MINYEAR + " and " + MAXYEAR)
    month = dtTuple[1]
    if (month < 1 or 12 < month):
        raise ValueError("MONTH must be between (inclusive) 1 and 12")
    day = dtTuple[2]
    if (day < 1 or 31 < day):
        raise ValueError("DAY must be between (inclusive) 1 and 31")
    hour = dtTuple[3]
    if (hour < 0 or 23 < hour):
        raise ValueError("HOUR must be between (inclusive) 0 and 23")
    minute = dtTuple[4]
    if (minute < 0 or 59 < minute):
        raise ValueError("MINUTE must be between (inclusive) 0 and 59")
    second = dtTuple[5]
    if (second < 0 or 59 < second):
        raise ValueError("SECOND must be between (inclusive) 0 and 59")

    return tzone.localize(datetime(year, month, day, hour, minute, second))
