"""

chaudio setup tools, for installation

"""

import glob
from os import path

# always prefer setuptools over distutils
from setuptools import setup


# the location of the setup file
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


setup(
    name='chaudio',
    version='0.0.4',

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

    install_requires=['numpy', 'scipy', 'simpleaudio'],

    extras_require={
        'test': ['coverage'],
    },

    data_files=[('chaudio/samples', glob.glob('chaudio/samples/*')), ('examples', glob.glob("examples/*"))],
    
    include_package_data=True,

)

