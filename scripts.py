import contextily as ctx
import geojson
import geopandas as gpd
import mapclassify
import matplotlib.pyplot as plt
import os
import pandas as pd
import requests

from matplotlib_scalebar.scalebar import ScaleBar
from pyproj import CRS

def getBordersFile(borders_path):
    # Read borders file. This file contains all municipality borders in Finland
    borders = gpd.read_file(borders_path)
    return borders

def getGrid():
    grid_path = "../250m/hki_250.shp"
    assert os.path.isfile(grid_path) 
    grid = gpd.read_file(grid_path)
    
    return grid

# Examples of typecodes and typenameslayers
# 1180 = frisbeegolf_rata
# 1340 = pallokenttä
# 2120 = kuntosali
def getLipasData(typecode='1180', typename='frisbeegolf_rata', municipality='Helsinki'):
    """
    This function fetches LIPAS data from WFS and sets its crs. LIPAS data is returned to the user with simplified attributes; id, name of the sport place in Finnish and Swedish, type code and type name in Finnish. 
    Arguments: First argument is 4 digit typecode of the sport facility and second is the typename of the sport facility in Finnish. The third argument is the chosen municipality.
    """
    # Fetching data from WFS using requests, in json format, using bounding box over the helsinki area
    r = requests.get(r"http://lipas.cc.jyu.fi/geoserver/lipas/ows?service=wfs&version=2.0.0&request=GetFeature&typeNames=lipas:lipas_"""+typecode+"""_"""+typename+"""&bbox=-548576.0,1548576.0,6291456.0,8388608.0,EPSG:3067&outputFormat=json""")

    # Creating GeoDataFrame from geojson
    lipas_data = gpd.GeoDataFrame.from_features(geojson.loads(r.content))
    
    # Define crs for lipas_data
    lipas_data.crs = CRS.from_epsg(3067)
    
    # Get the borders for municipalities
    borders_path = "../sport-facility-data/data/mml/hallintorajat_10k/2020/SuomenKuntajako_2020_10k.shp"
    borders = getBordersFile(borders_path)
    
    # choose municipality borders
    muni_borders = borders[borders['NAMEFIN']==municipality]
    
    # create geodaframe from the buffered zone
    #muni_borders = gpd.GeoDataFrame(gpd.GeoSeries(muni_borders))
    #muni_borders = muni_borders.rename(columns={0:'geometry'})
    #muni_borders.crs = CRS.from_epsg(3067)

    # limit the output to be only sports facilities in a municipality
    sports_facilities_in_municipality = gpd.overlay(lipas_data, muni_borders, how='intersection') 
    sports_facilities_in_municipality = sports_facilities_in_municipality.to_crs(epsg=4326)

    return sports_facilities_in_municipality
       

def getReachabilityDF(folder, reachability_type): 
    '''
        Get reachability of sports facilities.
        Arguments: First: folder where the reachability files are. Second:
        reachability_type is transportation mode, possible modes are walking, cycling, transit and driving. output_file_name is the output file name. Third: output_file_name is the name of the output folder.
    '
    '''
    
    # Get filenames into a list
    files = [filename for filename in os.listdir(folder) if filename.startswith(r'reachability_{}'.format(reachability_type))]

    # Init a new empty geodataframe
    gdf = gpd.GeoDataFrame()
    
    # Loop through the file names and add the files to the geodataframe
    for name in files:
        r_path = r"./{}/{}".format(folder,name)
        temp_gdf = gpd.read_file(r_path, driver="GeoJSON")
        gdf = pd.concat([gdf, temp_gdf])
    
    # Sort values by travel time
    gdf = gdf.sort_values(by='travel_time', ascending=True)
    
    # Keep the shortest time for duplicate travel time locations. This needs to be done because there
    # can be multiple travel times for individual grid cells.
    gdf = gdf.drop_duplicates(subset='id', keep="first")
    
    assert gdf['id'].is_unique
    
    return gdf

def visualize(geodataframe, column_name, destination_name, travel_method):
    #define class breaks to array seen below (upper limits), apply this classification to pt and car travel times
    bins = [0,5,10,15,20,25,30,40,50,60]
    classifier = mapclassify.UserDefined.make(bins)
       
    #make new columns with class values
    geodataframe["classified"] = geodataframe[[column_name]].apply(classifier)
    
    #change crs to add basemap later
    geodataframe = geodataframe.to_crs(epsg=3067)
                
    #plot
    fig, ax = plt.subplots(figsize=(10,10))

    #plot the travel times according to the classified field
    geodataframe.plot(ax= ax, column=geodataframe["classified"], cmap="RdYlBu", legend=True, alpha=0.2)
    cbar = fig.axes[1]
    cbar.set_yticklabels(bins)
    
    #add basemap with contextify
    cartodb_url = "https://a.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png" 

    ctx.add_basemap(ax, attribution="Source: Lipas, Mapple Analytics Oy. Basemap: Carto light", 
                    source=cartodb_url)

    #add scalebar
    scalebar = ScaleBar(1.0, location=4)
    plt.gca().add_artist(scalebar)

    #add north arrow
    x, y, arrow_length = 0.9, 0.2, 0.115
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length), arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=20, xycoords=ax.transAxes)
    
    #add title and show map
    ax.set_title("Travel times to " + destination_name + " by " + travel_method , fontsize=24)

    #save and return fig
    output_fig = "results/traveltimes" + column_name + ".png"
    plt.savefig(output_fig)
    return output_fig