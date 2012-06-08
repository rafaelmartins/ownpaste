#!/usr/bin/env python

from setuptools import find_packages, setup
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, 'README')) as fp:
    long_description = fp.read()

setup(
    name='ownpaste',
    version='0.1pre',
    license='BSD',
    description='Private pastebin (server-side implementation)',
    long_description=long_description,
    author='Rafael G. Martins',
    author_email='rafael@rafaelmartins.eng.br',
    url='https://hg.rafaelmartins.eng.br/ownpaste/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask >= 0.8',
        'Flask-Script >= 0.3.3',
        'Flask-SQLAlchemy >= 0.16',
        'Jinja2 >= 2.6',
        'Werkzeug >= 0.8',
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
