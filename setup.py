from setuptools import setup

setup(
    name='polygon_simplification',
    version='0.1.0',
    description='Routines for simplifying shapely polygons',
    url='https://github.com/jamesmcclain/polygon-simplification',
    author='James McClain',
    author_email='jmcclain@azava.com',
    license='Apache License 2.0',
    install_requires=[
        'Shapely==1.6.*',
    ],
    packages=[
        'polygon_simplification',
    ],
)
