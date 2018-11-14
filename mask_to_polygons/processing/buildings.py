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
    _, contours, _ = cv2.findContours(buildings, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)
    rotrect = cv2.minAreaRect(contours[0])
    return rotrect


def get_kernel(rectangle, width_factor=0.33, thickness=0.001):
    (_, (xwidth, ywidth), angle) = rectangle

    width = int(width_factor * min(xwidth, ywidth))
    half_width = width // 2
    diagonal = width * math.sqrt(2)
    pos = (half_width, half_width)
    dim = (diagonal, thickness)

    kernel = np.zeros((width, width), dtype=np.uint8)
    try:
        kernel = cv2.cvtColor(kernel, cv2.COLOR_GRAY2BGR)
    except Exception:
        return None

    if ywidth > xwidth:
        element = (pos, dim, angle)
    else:
        element = (pos, dim, angle + 90)
    element = cv2.boxPoints(element)
    element = np.int0(element)

    cv2.drawContours(kernel, [element], 0, (1, 0, 0), -1)
    kernel = kernel[:, :, 0]

    return kernel


def _split_buildings(buildings,
                     min_aspect_ratio=1.618,
                     width_factor=0.33,
                     erode_thickness=0.001,
                     dilate_thickness=2):
    rectangle = get_rectangle(buildings)
    erode_kernel = get_kernel(
        rectangle, width_factor=width_factor, thickness=erode_thickness)
    dilate_kernel = get_kernel(
        rectangle, width_factor=width_factor, thickness=dilate_thickness)
    if erode_kernel is None or dilate_kernel is None:
        return buildings
    retval = cv2.morphologyEx(
        buildings.copy(), cv2.MORPH_ERODE, erode_kernel, iterations=1)
    retval = cv2.morphologyEx(
        retval.copy(), cv2.MORPH_DILATE, dilate_kernel, iterations=1)
    retval = np.array(retval == 1, dtype=np.uint8)

    return retval
