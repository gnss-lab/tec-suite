"""A setuptools based setup module."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import setup, find_packages
from codecs import open
from os import path

from tecs import version

here = path.abspath(path.dirname(__file__))

print(here)

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tec-suite',
    version=version,

    description='Reconstruct TEC value in the ionosphere using GNSS-data',
    long_description=long_description,

    url='https://github.com/gnss-lab/tec-suite',

    author='Ilya Zhivetiev',
    author_email='i.zhivetiev@gnss-lab.org',

    license='GPLv3+',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',

        ('License :: OSI Approved :: GNU General Public License v3 '
         'or later (GPLv3+)'),

        'Programming Language :: Python :: 3',
    ],

    keywords='ionosphere GNSS TEC',

    py_modules=["tecs"],
    packages=find_packages(),

    install_requires=['future'],

    extras_require={
        'test': ['coverage', 'nose'],
    },

    package_data={},
    data_files=[],

    entry_points={
        'console_scripts': [
            'tecs = tecs.__main__:run',
        ]
    },
)
