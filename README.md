# Mapple API

Mapple API provide services to fetch Accessibility data and demographic catchment all over Finland.  

This scripts provides an example on how to use the API to fetch Accessibility Data.

## Requirements
    - conda-forge::python=3.8.0
    - conda-forge::aiohttp=3.7.3
    - conda-forge::starlette=0.12.9
    - conda-forge::python-rapidjson=0.9.4
    - conda-forge::geopandas=0.8.1
## Installation

```shell script
conda env create -f environment.yaml
conda activate mapple-api
```

## Usage


```shell script
export MAPPLE_API_KEY=<YOUR_MAPPLE_API_KEY>
python main.py -u http://localhost:8080 -e resources/pois.geojson
```

## Options
Mapple API client example

arguments:

|      Variable      |      Default      |      Description      |
|--------------------|:-----------------:|----------------------:|
| -h, --help   |            | show this help message and exit |
| -u , --mapple_url   |      http://localhost:8080      | Mapple API URL. |
| -e , --entry_points   |      None      | Geojson containing the points to consider as starting points (GeoJSON). |
| -t  [ ...], --travel_modes  [ ...]   |      None      | Define what travel modes to calculate reachability data (walking, cycling, transit, driving) Leave it without define if accessibility for all travel modes must be calculated. |
| -r , --radius   |  20000 | Radius in meters of the area for accessibility calculation. |
| -m , --max_time_threshold   |  30|  Maximum Travel Time in minutes of the temporal threshold (limits) to define the temporal area for accessibility calculation. Maximum value accepted 500. |
| -p , --output_file_prefix   |      reachability      |  Prefix to add to the output files. |
| -d , --output_directory   |      /tmp/mapple_api/      |  Path where to locate the output files (default: /tmp/mapple_api). |

