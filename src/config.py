import os
from enum import Enum


class MappleAPIConfig:
    @staticmethod
    def getMappleAPIKey():
        return os.getenv("MAPPLE_API_KEY")


class TravelModes(str, Enum):
    TRANSIT = "transit"
    DRIVING = "driving"
    CYCLING = "cycling"
    WALKING = "walking"


class TimeOfDay(str, Enum):
    MIDDAY = "midday"
    RUSH_HOUR = "rushHour"


class TimeProfile(str, Enum):
    AVERAGE = "average"
    FASTEST = "fastest"
    SLOWEST = "slowest"


class WalkingSpeeds(float, Enum):
    AVERAGE = 4.4


class CyclingSpeeds(float, Enum):
    MINIMUM = 1.0
    SLOW_CYCLING = 12.0
    AVERAGE_CYCLING = 16.0
    FAST_CYCLING = 19.0
