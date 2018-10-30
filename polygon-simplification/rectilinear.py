import math

from shapely.affinity import rotate
from shapely.geometry import Polygon
from shapely.ops import cascaded_union


def cover(polygon, width):
    queries = 0
    boxes = []
    xmin, ymin, xmax, ymax = polygon.bounds

    x = float(math.floor(xmin))
    while x < xmax:
        y = float(math.floor(ymin))
        while y < ymax:
            queries = queries + 1
            box = Polygon([(x+width, y+width), (x+width, y), (x, y), (x, y+width)])
            if box.intersects(polygon):
                boxes.append(box)
            y = y + width
        x = x + width

    area = len(boxes)*width*width
    return cascaded_union(boxes), area, queries

