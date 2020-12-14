import argparse
import asyncio
import json
import os
import tempfile
import time
from typing import List

import geopandas

from src.config import TimeOfDay, TimeProfile, WalkingSpeeds, CyclingSpeeds, TravelModes
from src.mapple_api import fetch_walking_reachability, fetch_cycling_reachability, fetch_transit_reachability, \
    fetch_driving_reachability


async def main(points_geojson, mapple_url="http://localhost:8080", prefix="reachability", travel_mode: List = None,
               maxTimeThreshold: int = 30, radius: int = 20000, output_folder=None):
    pois_df = geopandas.read_file(points_geojson,
                                  driver="GeoJSON")

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    prefix_pattern = "{prefix}_{travel_mode}_"
    walking_target_file_fd, walking_target_file_path = tempfile.mkstemp(
        prefix=prefix_pattern.format(prefix=prefix,
                                     travel_mode=TravelModes.WALKING),
        dir=output_folder,
        suffix=".acc_dump")
    cycling_target_file_fd, cycling_target_file_path = tempfile.mkstemp(
        prefix=prefix_pattern.format(prefix=prefix,
                                     travel_mode=TravelModes.CYCLING),
        dir=output_folder,
        suffix=".acc_dump")
    transit_target_file_fd, transit_target_file_path = tempfile.mkstemp(
        prefix=prefix_pattern.format(prefix=prefix,
                                     travel_mode=TravelModes.TRANSIT),
        dir=output_folder,
        suffix=".acc_dump")
    driving_target_file_fd, driving_target_file_path = tempfile.mkstemp(
        prefix=prefix_pattern.format(prefix=prefix,
                                     travel_mode=TravelModes.DRIVING),
        dir=output_folder,
        suffix=".acc_dump")

    for index in range(0, len(pois_df) + 10, 10):  # +10 to if the length is not multiple of 10
        chunk = pois_df[index:index + 10]
        if not chunk.empty:
            if (travel_mode is None) or (TravelModes.WALKING in travel_mode):
                coroutines = chunk.apply(lambda row: fetch_walking_reachability(
                    base_url=mapple_url, latitude=row.geometry.y, longitude=row.geometry.x, radius=radius,
                    walking_speed_kmph=WalkingSpeeds.AVERAGE, maxTimeThreshold=maxTimeThreshold), axis=1).to_list()

                walking_reachability = await asyncio.gather(*coroutines)
                # sleep the requests for 5 secs so the server is not going to throw 'Too Many Requests Exceptions'

                with open(walking_target_file_path, "a") as target_file:
                    temp = [target_file.write("{}\n".format(json.dumps(reachability))) for reachability in
                            walking_reachability]

                time.sleep(5)

            if (travel_mode is None) or (TravelModes.CYCLING in travel_mode):
                coroutines = chunk.apply(lambda row: fetch_cycling_reachability(
                    base_url=mapple_url, latitude=row.geometry.y, longitude=row.geometry.x, radius=radius,
                    walking_speed_kmph=WalkingSpeeds.AVERAGE,
                    cycling_speed_kmph=CyclingSpeeds.AVERAGE_CYCLING, maxTimeThreshold=maxTimeThreshold),
                                         axis=1).to_list()

                cycling_reachability = await asyncio.gather(*coroutines)
                with open(cycling_target_file_path, "a") as target_file:
                    temp = [target_file.write("{}\n".format(json.dumps(reachability))) for reachability in
                            cycling_reachability]
                time.sleep(5)

            if (travel_mode is None) or (TravelModes.TRANSIT in travel_mode):
                coroutines = chunk.apply(lambda row: fetch_transit_reachability(
                    base_url=mapple_url, latitude=row.geometry.y, longitude=row.geometry.x, radius=radius,
                    walking_speed_kmph=WalkingSpeeds.AVERAGE,
                    timeOfDay=TimeOfDay.RUSH_HOUR,
                    timeProfile=TimeProfile.FASTEST, maxTimeThreshold=maxTimeThreshold), axis=1).to_list()

                transit_reachability = await asyncio.gather(*coroutines)
                with open(transit_target_file_path, "a") as target_file:
                    temp = [target_file.write("{}\n".format(json.dumps(reachability))) for reachability in
                            transit_reachability]
                time.sleep(5)

            if (travel_mode is None) or (TravelModes.DRIVING in travel_mode):
                coroutines = chunk.apply(lambda row: fetch_driving_reachability(
                    base_url=mapple_url, latitude=row.geometry.y, longitude=row.geometry.x, radius=radius,
                    walking_speed_kmph=WalkingSpeeds.AVERAGE,
                    timeOfDay=TimeOfDay.RUSH_HOUR,
                    timeProfile=TimeProfile.FASTEST, maxTimeThreshold=maxTimeThreshold), axis=1).to_list()

                driving_reachability = await asyncio.gather(*coroutines)
                with open(driving_target_file_path, "a") as target_file:
                    temp = [target_file.write("{}\n".format(json.dumps(reachability))) for reachability in
                            driving_reachability]
                time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mapple API client example')
    parser.add_argument('-u', '--mapple_url', metavar='', type=str,
                        default="http://localhost:8080",
                        help='Mapple API URL.')
    parser.add_argument('-e', '--entry_points', metavar='', type=str,
                        required=True,
                        help='Geojson containing the points to consider as starting points (GeoJSON).')
    parser.add_argument('-t', '--travel_modes', metavar='', type=str, nargs='+',
                        help='Define what travel modes to calculate reachability data (walking, cycling, transit, driving) Leave it without define if accessibility for all travel modes must be calculated.'.format(
                            walking=TravelModes.WALKING,
                            cycling=TravelModes.CYCLING,
                            transit=TravelModes.TRANSIT,
                            driving=TravelModes.DRIVING,
                        ), choices=[TravelModes.WALKING.value, TravelModes.CYCLING.value, TravelModes.TRANSIT.value, TravelModes.DRIVING.value]
                        )
    parser.add_argument('-r', '--radius', metavar='', type=int,
                        default=20000,
                        help='Radius in meters of the area for accessibility calculation.')
    parser.add_argument('-m', '--max_time_threshold', metavar='', type=int,
                        default=30,
                        help='Maximum Travel Time in minutes of the temporal threshold (limits) to define the temporal area for accessibility calculation. Maximum value accepted 500.')
    parser.add_argument('-p', '--output_file_prefix', metavar='', type=str,
                        default="reachability",
                        help='Prefix to add to the output files.')

    outpt_directory = os.path.join(tempfile.gettempdir(), "mapple_api")
    parser.add_argument('-d', '--output_directory', metavar='', type=str,
                        default=outpt_directory,
                        help='Path where to locate the output files (default: {default}).'.format(
                            default=outpt_directory))

    args = parser.parse_args()

    asyncio.run(main(points_geojson=args.entry_points, mapple_url=args.mapple_url, prefix=args.output_file_prefix,
                     travel_mode=args.travel_modes,
                     maxTimeThreshold=args.max_time_threshold, radius=args.radius, output_folder=args.output_directory))
