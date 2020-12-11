import os

from dotenv import load_dotenv
from envvarname import EnvVarName


def loadEnvVars() -> None:
  load_dotenv()


def getEnvVar(name: EnvVarName) -> str:
    """
    Retrieve the value of a specified environment variable.

    Parameters:
        name (EnvVarName): 

    Returns:
        string: 
    """

    value = os.getenv(name.value, "")
    if (value is None):
        #LOGGER: The environment variable is not set
        value = value

    return value


def isEmpty(value: str) -> bool:
    return value == "" or value is None
