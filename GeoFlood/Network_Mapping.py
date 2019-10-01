import os
import pandas as pd
from osgeo import ogr
import gdal, osr
import ConfigParser
import inspect


def network_mapping(cat_shp, seg_shp, map_csv):
    shapefile = seg_shp
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(seg_shp, 0)
    layer = dataSource.GetLayer()
    hydroid_list = []
    comid_list = []
    for feature in layer:
        geom = feature.GetGeometryRef()
        pnt = geom.Centroid()
        cat_Source = driver.Open(cat_shp, 0)
        cat_layer = cat_Source.GetLayer()
        for cat_feat in cat_layer:
            if pnt.Intersects(cat_feat.GetGeometryRef()):
                hydroid = feature.GetField("HYDROID")
                comid = cat_feat.GetField("FEATUREID")
                hydroid_list.append(hydroid)
                comid_list.append(comid)
    df = pd.DataFrame({"HYDROID" : hydroid_list, "COMID" : comid_list})
    df.to_csv(map_csv, index=False, columns=['HYDROID', 'COMID'])


def main():

    ##CONFIGURATION
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(
        os.path.dirname(
            inspect.stack()[0][1])),
                             'GeoFlood.cfg'))
    geofloodHomeDir = config.get('Section', 'geofloodhomedir')
    projectName = config.get('Section', 'projectname')
    DEM_name = config.get('Section', 'dem_name')
    #geofloodHomeDir = "H:\GeoFlood"
    #projectName = "Test_Stream"
    #DEM_name = "DEM"

    geofloodDir = os.path.join(geofloodHomeDir, "Inputs",
                                    "GIS", projectName) 
    Name_path = os.path.join(geofloodDir, DEM_name)

    ##INPUT
    cat_shp = os.path.join(geofloodDir, "Catchment.shp")
    seg_shp = Name_path + "_channelSegment.shp"

    ##OUTPUT
    map_csv = Name_path + "_networkMapping.csv"

    ##EXECUTION
    network_mapping(cat_shp, seg_shp, map_csv)


if __name__ == "__main__":
    main()
