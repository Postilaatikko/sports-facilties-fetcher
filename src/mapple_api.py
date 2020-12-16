from enum import Enum
from typing import Dict

import aiohttp
import rapidjson
from starlette.exceptions import HTTPException
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from src.config import TimeOfDay, TimeProfile, WalkingSpeeds, CyclingSpeeds, MappleAPIConfig


def convertEnumToValue(enum_param):
    return enum_param.value if isinstance(enum_param, Enum) else enum_param


async def fetch(url, params: Dict[str, str], headers: Dict[str, str]):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                response_dict = await response.json(loads=rapidjson.loads)
                if HTTP_200_OK.__eq__(response.status):
                    return response_dict
                else:
                    detail = response_dict["detail"] if "detail" in response_dict else await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=detail
                    )
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mapple API server not reached"
        ) from e


async def fetch_walking_reachability(base_url: str, latitude: float,
                                     longitude: float,
                                     radius: int = 20000,
                                     walking_speed_kmph: float = WalkingSpeeds.AVERAGE, maxTimeThreshold: int = 30):
    try:
        url = "{baseUrl}/fi/reachability/travelTime/walking/1".format(baseUrl=base_url)
        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "radius": str(radius),
            "walkingSpeedKmph": str(convertEnumToValue(walking_speed_kmph)),
            "maxTimeThreshold": str(maxTimeThreshold)
        }
        headers = {
            "ApiKey": "{token}".format(
                token=MappleAPIConfig.getMappleAPIKey()
            )
        }

        return await fetch(url=url, params=params, headers=headers)
    except Exception as e:
        raise e


async def fetch_cycling_reachability(base_url: str, latitude: float,
                                     longitude: float,
                                     radius: int = 20000,
                                     walking_speed_kmph: float = WalkingSpeeds.AVERAGE,
                                     cycling_speed_kmph: float = CyclingSpeeds.AVERAGE_CYCLING,
                                     maxTimeThreshold: int = 30):
    try:
        url = "{baseUrl}/fi/reachability/travelTime/cycling/1".format(baseUrl=base_url)
        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "radius": str(radius),
            "walkingSpeedKmph": str(convertEnumToValue(walking_speed_kmph)),
            "cyclingSpeedKmph": str(convertEnumToValue(cycling_speed_kmph)),
            "maxTimeThreshold": str(maxTimeThreshold)
        }
        headers = {
            "ApiKey": "{token}".format(
                token=MappleAPIConfig.getMappleAPIKey()
            )
        }

        return await fetch(url=url, params=params, headers=headers)
    except Exception as e:
        raise e


async def fetch_transit_reachability(base_url: str, latitude: float,
                                     longitude: float,
                                     radius: int = 20000,
                                     walking_speed_kmph: float = WalkingSpeeds.AVERAGE,
                                     timeOfDay: TimeOfDay = TimeOfDay.RUSH_HOUR,
                                     timeProfile: TimeProfile = TimeProfile.FASTEST,
                                     maxTimeThreshold: int = 30):
    try:
        url = "{baseUrl}/fi/reachability/travelTime/transit/1".format(baseUrl=base_url)
        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "radius": str(radius),
            "walkingSpeedKmph": str(convertEnumToValue(walking_speed_kmph)),

            "timeOfDay": convertEnumToValue(timeOfDay),
            "targetType": "origin",
            "timeProfile": convertEnumToValue(timeProfile),

            "maxTimeThreshold": str(maxTimeThreshold)
        }
        headers = {
            "ApiKey": "{token}".format(
                token=MappleAPIConfig.getMappleAPIKey()
            )
        }

        return await fetch(url=url, params=params, headers=headers)
    except Exception as e:
        raise e


async def fetch_driving_reachability(base_url: str, latitude: float,
                                     longitude: float,
                                     radius: int = 20000,
                                     walking_speed_kmph: float = WalkingSpeeds.AVERAGE,
                                     timeOfDay: TimeOfDay = TimeOfDay.RUSH_HOUR,
                                     timeProfile: TimeProfile = TimeProfile.FASTEST,
                                     maxTimeThreshold: int = 30):
    try:
        url = "{baseUrl}/fi/reachability/travelTime/driving/1".format(baseUrl=base_url)
        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "radius": str(radius),
            "walkingSpeedKmph": str(convertEnumToValue(walking_speed_kmph)),

            "timeOfDay": convertEnumToValue(timeOfDay),
            "targetType": "origin",
            "timeProfile": convertEnumToValue(timeProfile),

            "maxTimeThreshold": str(maxTimeThreshold)
        }
        headers = {
            "ApiKey": "{token}".format(
                token=MappleAPIConfig.getMappleAPIKey()
            )
        }

        return await fetch(url=url, params=params, headers=headers)
    except Exception as e:
        raise e
