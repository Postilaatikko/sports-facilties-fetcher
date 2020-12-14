import asyncio
import json
import os

import asynctest
import geopandas
import pandas
from asynctest.mock import patch

from src.config import WalkingSpeeds, TimeOfDay, TimeProfile
from src.mapple_api import fetch_transit_reachability


class MappleAPITest(asynctest.TestCase):
    def setUp(self):
        self.mapple_url = "https://staging.api.mapple.io/fi"

    @patch('src.mapple_api.fetch')
    async def test_fetch_walking_reachability(self, fetch):
        expected_result = geopandas.read_file(os.path.join(os.getcwd(), "resources", "transit_reachability.geojson"),
                                              driver="GeoJSON")
        pois_df = geopandas.read_file(os.path.join(os.getcwd(), "resources", "pois.geojson"),
                                      driver="GeoJSON")

        with open(os.path.join(os.getcwd(), "resources", "transit_reachability.geojson")) as expected_file:
            fetch.return_value = json.loads(expected_file.read())

        maxTimeThreshold = 60
        radius = 20000

        chunk = pois_df[0:1]

        if not chunk.empty:
            coroutines = chunk.apply(lambda row: fetch_transit_reachability(
                base_url=self.mapple_url, latitude=row.geometry.y, longitude=row.geometry.x, radius=radius,
                walking_speed_kmph=WalkingSpeeds.AVERAGE,
                timeOfDay=TimeOfDay.RUSH_HOUR,
                timeProfile=TimeProfile.FASTEST, maxTimeThreshold=maxTimeThreshold), axis=1).to_list()

            transit_reachability = await asyncio.gather(*coroutines)

            # transit_reachability_memory = io.StringIO()
            # transit_reachability_memory.write(json.dumps(transit_reachability))

            # transit_reachability_memory.seek(0)
            result = geopandas.GeoDataFrame.from_features(transit_reachability[0])
            result["id"] = [feature["id"] for feature in transit_reachability[0]["features"]]
            result = result.set_index("id")

            expected_result = expected_result.set_index("id")
            expected_result = expected_result.drop(["geometry"], axis=1)
            result = result.drop(["geometry"], axis=1)
            result = result.sort_index()
            expected_result = expected_result.sort_index()
            pandas.testing.assert_frame_equal(expected_result, result)

            # target_file_fd, target_file_path = tempfile.mkstemp(prefix="transit_reachability.geojson",
            #                                                     dir=os.path.join(os.getcwd(), "resources"),
            #                                                     suffix=".geojson")
            #
            # with open(target_file_path, "a") as target_file:
            #     temp = [target_file.write("{}\n".format(json.dumps(reachability))) for reachability in
            #             transit_reachability]
