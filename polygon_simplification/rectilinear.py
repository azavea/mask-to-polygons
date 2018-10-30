import math
import random

from shapely.affinity import rotate
from shapely.geometry import Polygon
from shapely.ops import cascaded_union


def cover(polygon, width, max_queries=float('inf')):
    queries = 0
    boxes = []
    xmin, ymin, xmax, ymax = polygon.bounds

    if (xmax - xmin) * (ymax - ymin) > max_queries * width * width:
        return None, None, None

    x = xmin
    while x < xmax:
        y = ymin
        while y < ymax:
            queries = queries + 1
            box = Polygon([(x + width, y + width), (x + width, y), (x, y),
                           (x, y + width)])
            if box.intersects(polygon):
                boxes.append(box)
            y = y + width
        x = x + width

    area = len(boxes) * width * width
    return cascaded_union(boxes), area, queries


def simplify(polygon, width, query_budget=3000):
    best_area = math.inf
    best_shape = None

    centroid = polygon.centroid.xy
    cx = centroid[0][0]
    cy = centroid[1][0]
    cx, cy

    queries = 0
    while queries < query_budget:
        theta = random.uniform(0, 2 * math.pi)
        s = rotate(
            geom=polygon, angle=theta, origin=(cx, cy), use_radians=True)
        shape, area, query_cost = cover(s, width)
        queries = queries + query_cost
        if area < best_area:
            best_area = area
            best_shape = rotate(
                geom=shape, angle=-theta, origin=(cx, cy), use_radians=True)

        # return best_area*(width*width)
        return best_shape
