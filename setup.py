"""

chaudio setup tools

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import glob
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='chaudio',
    version='0.0.1',

    description='Programmatic music synthesis',
    long_description=long_description,

    url='https://github.com/chemicaldevelopment/chaudio',

    author='Cade Brown',
    author_email='cade@chemicaldevelopment.us',

    license='GPLv3',

    classifiers=[
        'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis',
    ],

    keywords='audio music synthesis processing',

    packages = ["chaudio"],

    test_suite="chaudio.tests",

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    install_requires=['numpy', 'scipy', 'matplotlib'],

    extras_require={
        'test': ['coverage'],
    },

    data_files=[('chaudio/samples', glob.glob('chaudio/samples/*')), ('examples', glob.glob("examples/*"))],
    
    include_package_data=True,

)

# figure this out
"""
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },

"""
