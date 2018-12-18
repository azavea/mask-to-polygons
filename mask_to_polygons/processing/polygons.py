import rasterio
import rasterio.features


def get_polygons(mask, transform):
    polygons = []
    shapes = list(rasterio.features.shapes(mask, transform=transform))
    if len(shapes) > 0:
        polygons = [polygon for (polygon, _) in shapes[0:-1]]
    else:
        polygons = []

    return polygons
