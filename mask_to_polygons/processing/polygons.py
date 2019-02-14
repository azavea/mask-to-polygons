import rasterio
import rasterio.features


def get_polygons(mask, transform):
    polygons = []
    shapes = rasterio.features.shapes(mask, mask=mask == 1, transform=transform)
    shapes = filter(lambda ab: ab[1] == 1, shapes)
    shapes = list(shapes)

    if len(shapes) > 0:
        polygons = [polygon for (polygon, _) in shapes]
    else:
        polygons = []

    return polygons
