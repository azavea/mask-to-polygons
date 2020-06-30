from setuptools import setup

setup(
    name='mask-to-polygons',
    version='0.0.2',
    description='Routines for extracting and working with polygons from semantic segmentation masks',
    url='https://github.com/azavea/mask-to-polygons',
    author='James McClain',
    author_email='jmcclain@azava.com',
    license='Apache License 2.0',
    install_requires=[
        'Shapely==1.6.*',
        'opencv-python==4.1.*',
        'numpy>=1.0.0',
        'rasterio>=1.0.0',
        'geojson>=2.4.0',
    ],
    packages=[
        'mask_to_polygons.simplification',
        'mask_to_polygons.processing',
        'mask_to_polygons',
    ],
)
