import geojson
import json
import rasterio
import rasterio.features
import shapely
import shapely.geometry
from geojson import FeatureCollection

from mask_to_polygons.processing import buildings
from mask_to_polygons.processing import polygons


def mask_from_geotiff(mask_filename):
    with rasterio.open(mask_filename, 'r') as dataset:
        mask = dataset.read(1)
    return mask


def geometries_from_geojson(filename):
    geo_json = None
    gs = []

    with open(filename, 'r') as file:
        geo_json = json.loads(file.read())

    if 'features' in geo_json.keys():
        for g in geo_json['features']:
            gs.append(g['geometry'])
    elif 'geometries' in geo_json.keys():
        for g in geo_json['geometries']:
            gs.append(g)
    else:
        raise Exception('Unrecognized GeoJSON Format')

    return gs


def geometries_from_mask(mask,
                         transform,
                         mode,
                         min_aspect_ratio=1.618,
                         min_area=None,
                         width_factor=0.5,
                         thickness=0.001):
    transform_fn = None
    if isinstance(transform, rasterio.transform.Affine):
        pass
    elif isinstance(transform, str):
        with rasterio.open(transform, 'r') as dataset:
            transform = dataset.transform
    elif callable(transform):
        # Transform can be function of form f(x, y) which is assumed to convert from
        # pixel coordinates to (lat, lng)
        transform_fn = transform
        transform = rasterio.transform.IDENTITY

    if mode == 'polygons':
        polys = polygons.get_polygons(mask, transform)
    elif mode == 'buildings':
        polys = buildings.get_polygons(mask, transform, min_aspect_ratio,
                                       min_area, width_factor, thickness)
    else:
        raise Exception()

    if transform_fn:
        new_polys = []
        for p in polys:
            p = shapely.geometry.shape(p)
            p = shapely.ops.transform(lambda x, y, z=None: transform_fn(x, y), p)
            new_polys.append(shapely.geometry.mapping(p))
        polys = new_polys

    return polys


def geojson_from_mask(mask,
                      transform,
                      mode='polygon',
                      min_aspect_ratio=1.618,
                      min_area=None,
                      width_factor=0.5,
                      thickness=0.001):
    polys = geometries_from_mask(mask, transform, mode, min_aspect_ratio,
                                 min_area, width_factor, thickness)
    features = []
    for poly in polys:
        features.append({
            'type': 'Feature',
            'properties': {},
            'geometry': poly
        })
    return geojson.dumps(FeatureCollection(features))


def shapeley_from_mask(mask,
                      transform,
                      mode='polygon',
                      min_aspect_ratio=1.618,
                      min_area=None,
                      width_factor=0.5,
                      thickness=0.001):
    polys = geometries_from_mask(mask, transform, mode, min_aspect_ratio,
                                 min_area, width_factor, thickness)
    return [shapely.geometry.shape(polygon) for polygon in polys]
