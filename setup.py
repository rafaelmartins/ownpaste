#!/usr/bin/env python

from setuptools import find_packages, setup
import os
import sys

cwd = os.path.dirname(os.path.abspath(__file__))

# doing things the wrong way...
# we need the module ownpaste.version but we can't import the full package
# first time because the dependencies probably aren't solved yet.
sys.path.append(os.path.join(cwd, 'ownpaste'))
from version import version as __version__

long_description = ''
with open(os.path.join(cwd, 'README')) as fp:
    long_description = fp.read()

setup(
    name='ownpaste',
    version=__version__,
    license='BSD',
    description='Private pastebin (server-side implementation)',
    long_description=long_description,
    author='Rafael G. Martins',
    author_email='rafael@rafaelmartins.eng.br',
    url='http://ownpaste.rtfd.org/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask >= 0.8',
        'Flask-Script >= 0.3.3',
        'Flask-SQLAlchemy >= 0.15',
        'Jinja2 >= 2.6',
        'Werkzeug >= 0.8',
        'sqlalchemy-migrate >= 0.7.2',
        'Pygments',
        'pytz',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={'console_scripts': ['ownpaste = ownpaste:main']},
)
