import cv2
import json
import math
import numpy as np


def geometries_from_geojson(filename):
    geojson = None
    gs = []

    with open(filename, 'r') as file:
        geojson = json.loads(file.read())
    for g in geojson['features']:
        gs.append(g['geometry'])

    return gs


def get_rectangle(buildings):
    _, contours, _ = cv2.findContours(buildings.copy(), cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)
    rotrect = cv2.minAreaRect(contours[0])
    return rotrect


def get_kernel(buildings,
               min_aspect_ratio=1.618,
               width_factor=0.75,
               rotrect=None):
    if rotrect is None:
        rotrect = get_rectangle(buildings)
    (_, (xwidth, ywidth), angle) = rotrect
    sqrt2 = math.sqrt(2)

    width = int(width_factor * min(xwidth, ywidth))
    kernel = np.zeros((width, width), dtype=np.uint8)
    try:
        kernel = cv2.cvtColor(kernel, cv2.COLOR_GRAY2BGR)
    except Exception:
        return None

    ratio = max(ywidth, xwidth) / min(ywidth, xwidth)
    if ratio < min_aspect_ratio:
        return None
    if ywidth > xwidth:
        element = (((width // 2, width // 2), (width * sqrt2, 0.001), angle))
    else:
        element = (((width // 2, width // 2), (width * sqrt2, 0.001),
                    angle + 90))
    element = cv2.boxPoints(element)
    element = np.int0(element)

    cv2.drawContours(kernel, [element], 0, (1, 0, 0), -1)
    kernel = kernel[:, :, 0]

    return kernel


def split_building_clusters(buildings,
                            min_aspect_ratio=1.618,
                            width_factor=0.33):
    kernel = get_kernel(
        buildings,
        min_aspect_ratio=min_aspect_ratio,
        width_factor=width_factor)
    if kernel is None:
        return buildings
    retval = cv2.morphologyEx(buildings, cv2.MORPH_OPEN, kernel, iterations=1)
    retval = np.array(retval == 1, dtype=np.uint8)

    return retval
