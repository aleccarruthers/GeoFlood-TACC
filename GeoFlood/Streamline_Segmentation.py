import os
import math
from osgeo import ogr
import gdal, osr
import ConfigParser
import inspect


def _distance(a, b):
    dx = abs(b[0] - a[0])
    dy = abs(b[1] - a[1])
    return (dx ** 2 + dy ** 2) ** 0.5


def split_line_single(line, length):
    line_points = line.GetPoints()
    sub_line = ogr.Geometry(ogr.wkbLineString)
    while length > 0:
        d = _distance(line_points[0], line_points[1])
        if d >= length:
            sub_line.AddPoint(*line_points[0])
            sub_line.AddPoint(*line_points[1])
            line_points.remove(line_points[0])
            break
        if d < length:
            sub_line.AddPoint(*line_points[0])
            line_points.remove(line_points[0])
            length -= d
    remainder = ogr.Geometry(ogr.wkbLineString)
    for point in line_points:
        remainder.AddPoint(*point)
    return sub_line, remainder


def network_split(in_shp, out_shp, split_distance):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(in_shp, 0)
    layer = dataSource.GetLayer()
    srs = layer.GetSpatialRef()
    ds = driver.CreateDataSource(out_shp)
    output_layer = ds.CreateLayer(out_shp,
                                  srs, ogr.wkbLineString)
    output_layer.CreateField(ogr.FieldDefn("HYDROID", ogr.OFTInteger))
    output_layer.CreateField(ogr.FieldDefn("Length", ogr.OFTReal))
    HydroID = 1
    for feature in layer:
        line = feature.GetGeometryRef()
        no_segments = int(math.ceil(line.Length() / split_distance))
        if no_segments == 0:
            remainder = line
            feat = ogr.Feature(output_layer.GetLayerDefn())
            feat.SetGeometry(remainder)
            feat.SetField('HYDROID', HydroID)
            feat.SetField('Length',remainder.Length())
            HydroID += 1
            output_layer.CreateFeature(feat)
            feat.Destroy()
        else:
            length = line.Length()/no_segments
            remainder = line
            for i in range(no_segments-1):
                segment, remainder = split_line_single(remainder, length)
                feat = ogr.Feature(output_layer.GetLayerDefn())
                feat.SetGeometry(segment)
                feat.SetField('HYDROID', HydroID)
                feat.SetField('Length',segment.Length())
                HydroID += 1
                output_layer.CreateFeature(feat)
                feat.Destroy()
            feat = ogr.Feature(output_layer.GetLayerDefn())
            feat.SetGeometry(remainder)
            feat.SetField('HYDROID', HydroID)
            feat.SetField('Length',remainder.Length())
            HydroID += 1
            output_layer.CreateFeature(feat)
            feat.Destroy()
    ds.Destroy()


def main():

    ##CONFIGURATION
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(os.path.dirname(
        os.path.dirname(
            inspect.stack()[0][1])),
                             'GeoFlood.cfg'))
    geofloodHomeDir = config.get('Section', 'geofloodhomedir')
    projectName = config.get('Section', 'projectname')
    #geofloodHomeDir = "H:\GeoFlood"
    #projectName = "Test_Stream"
    DEM_name = config.get('Section', 'dem_name')
    #DEM_name = "DEM"

    geofloodResultsDir = os.path.join(geofloodHomeDir, projectName)
    Name_path = os.path.join(geofloodResultsDir, DEM_name)

    #INPUT
    in_shp = Name_path+ "_channelNetwork.shp"

    ##OUTPUT
    out_shp = Name_path+ "_channelSegment.shp"

    ##EXECUTION
    split_distance = 1700
    network_split(in_shp, out_shp, split_distance)


if __name__ == "__main__":
    main()
