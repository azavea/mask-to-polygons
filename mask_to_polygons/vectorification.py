import geojson
import json
import rasterio
import rasterio.features
import shapely
import shapely.geometry
from geojson import GeometryCollection

from mask_to_polygons.processing import buildings


def mask_from_geotiff(mask_filename):
    with rasterio.open(mask_filename, 'r') as dataset:
        mask = dataset.read(1)
    return mask


def geometries_from_geojson(filename):
    geojson = None
    gs = []

    with open(filename, 'r') as file:
        geojson = json.loads(file.read())
    for g in geojson['features']:
        gs.append(g['geometry'])

    return gs


def geometries_from_mask(mask,
                         transform,
                         min_aspect_ratio=1.618,
                         min_area=None,
                         width_factor=0.5,
                         thickness=0.001):
    if isinstance(transform, rasterio.transform.Affine):
        pass
    elif isinstance(transform, str):
        with rasterio.open(transform, 'r') as dataset:
            transform = dataset.transform

    polygons = buildings.get_polygons(mask, transform)

    return polygons


def geojson_from_mask(mask,
                      transform,
                      min_aspect_ratio=1.618,
                      min_area=None,
                      width_factor=0.5,
                      thickness=0.001):
    polygons = geometries_from_mask(mask, transform, min_aspect_ratio,
                                    min_area, width_factor, thickness)
    return geojson.dumps(GeometryCollection(polygons))


def shapley_from_mask(mask,
                      transform,
                      min_aspect_ratio=1.618,
                      min_area=None,
                      width_factor=0.5,
                      thickness=0.001):
    polygons = geometries_from_mask(mask, transform, min_aspect_ratio,
                                    min_area, width_factor, thickness)
    return [shapely.geometry.shape(polygon) for polygon in polygons]
