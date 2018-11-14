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
    if len(contours) > 0:
        rectangle = cv2.minAreaRect(contours[0])
        return rectangle
    else:
        return None


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
                     dilate_thickness=2,
                     rectangle=None):
    if rectangle is None:
        rectangle = get_rectangle(buildings)
        if rectangle is None:
            return np.zeros(buildings.shape, dtype=np.uint8)

    (_, (xwidth, ywidth), _) = rectangle
    aspect_ratio = max(xwidth, ywidth) / min(xwidth, ywidth)
    if min_aspect_ratio is not None and aspect_ratio < min_aspect_ratio:
        return buildings

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


def split_all_buildings(mask,
                        min_aspect_ratio=1.618,
                        min_area_ratio=0.80,
                        hole_width_factor=0.33,
                        hole_erode_thickness=0.001,
                        hole_dilate_thickness=2,
                        wave_width_factor=0.618,
                        wave_erode_thickness=0.001,
                        wave_dilate_thickness=10):
    n, components = cv2.connectedComponents(mask)
    retval = np.zeros(mask.shape, dtype=np.uint8)
    for i in range(1, n + 1):
        buildings = np.array(components == i, dtype=np.uint8)
        split = split_buildings(
            buildings,
            min_aspect_ratio=min_aspect_ratio,
            min_area_ratio=min_area_ratio,
            hole_width_factor=hole_width_factor,
            hole_erode_thickness=hole_erode_thickness,
            hole_dilate_thickness=hole_dilate_thickness,
            wave_width_factor=wave_width_factor,
            wave_erode_thickness=wave_erode_thickness,
            wave_dilate_thickness=wave_dilate_thickness)
        retval = cv2.bitwise_or(retval, split)
    return retval


def split_buildings(buildings,
                    min_aspect_ratio=1.618,
                    min_area_ratio=0.80,
                    hole_width_factor=0.33,
                    hole_erode_thickness=0.001,
                    hole_dilate_thickness=2,
                    wave_width_factor=0.618,
                    wave_erode_thickness=0.001,
                    wave_dilate_thickness=10):
    rectangle = get_rectangle(buildings)
    without_holes = _split_buildings(
        buildings,
        min_aspect_ratio=min_aspect_ratio,
        width_factor=hole_width_factor,
        erode_thickness=hole_erode_thickness,
        dilate_thickness=hole_dilate_thickness,
        rectangle=rectangle)

    area_before = buildings.sum()
    if area_before <= 0:
        return buildings
    area_after = without_holes.sum()
    area_ratio = area_after / area_before
    if min_area_ratio >= area_ratio:
        return buildings

    n, components = cv2.connectedComponents(without_holes)
    retval = np.zeros(buildings.shape, dtype=np.uint8)
    for i in range(1, n + 1):
        component = np.array(components == i, dtype=np.uint8)
        without_waves = _split_buildings(
            component,
            min_aspect_ratio=min_aspect_ratio,
            width_factor=wave_width_factor,
            erode_thickness=wave_erode_thickness,
            dilate_thickness=wave_dilate_thickness,
            rectangle=rectangle)
        area_before = component.sum()
        area_after = without_waves.sum()
        if area_before <= 0:
            area_ratio = 0
        else:
            area_ratio = area_after / area_before
        if min_area_ratio < area_ratio:
            retval = cv2.bitwise_or(retval,
                                    cv2.bitwise_and(component, without_waves))
        else:
            retval = cv2.bitwise_or(retval, component)

    return retval
