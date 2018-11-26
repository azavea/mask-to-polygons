import json
import rasterio
import rasterio.features


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


def buildings_from_mask(mask, transform):
    if isinstance(transform, rasterio.transform.Affine):
        pass
    elif isinstance(transform, str):
        with rasterio.open(transform, 'r') as dataset:
            transform = dataset.transform

    retval = []
    for shape, value in rasterio.features.shapes(mask, transform=transform):
        retval.append(shape)

    return retval
