# -*- coding: utf-8 -*-
"""
    ownpaste.script
    ~~~~~~~~~~~~~~~

    Module with Flask-Script commands.

    :copyright: (c) 2012 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from flask import current_app
from flask.ext.script import Command, Option, prompt_pass
from migrate.versioning import api as migrate_api
from ownpaste.auth import HTTPDigestAuth
from ownpaste.migrations import __file__ as migrations_init

import logging
import os
import sys


class GeneratePw(Command):
    '''Generates a safe password for your configuration file.'''

    def run(self):
        auth = HTTPDigestAuth()
        p1 = prompt_pass('Password')
        p2 = prompt_pass('Retype password')
        if p1 != p2:
            print >> sys.stderr, 'Passwords didn\'t match.'
            return
        print
        print 'Add this to your configuration file:'
        print 'PASSWORD = \'%s\'' % auth.a1(p1)


class SingleLevelFilter(logging.Filter):
    def __init__(self, min=None, max=None):
        self.min = min or 0
        self.max = max or 100

    def filter(self, record):
        return self.min <= record.levelno <= self.max


class MigrateBase(Command):

    def init_logging(self):
        # code snippet from sqlalchemy-migrate
        logger = migrate_api.log
        h1 = logging.StreamHandler(sys.stdout)
        f1 = SingleLevelFilter(max=logging.INFO)
        h1.addFilter(f1)
        h2 = logging.StreamHandler(sys.stderr)
        f2 = SingleLevelFilter(min=logging.WARN)
        h2.addFilter(f2)
        logger.addHandler(h1)
        logger.addHandler(h2)
        logger.setLevel(logging.INFO)

    @property
    def dburi(self):
        return current_app.config['SQLALCHEMY_DATABASE_URI']

    @property
    def repository(self):
        return os.path.dirname(os.path.abspath(migrations_init))


class DbVersionControl(MigrateBase):
    '''Marks the database as under sqlalchemy-migrate's version control.'''

    option_list = (Option('version', type=int, nargs='?'),)

    def run(self, version):
        self.init_logging()
        migrate_api.version_control(url=self.dburi, repository=self.repository,
                                    version=version)


class DbUpgrade(MigrateBase):
    '''Upgrades the database to a later version.'''

    option_list = (Option('version', type=int, nargs='?'),)

    def run(self, version):
        self.init_logging()
        migrate_api.upgrade(url=self.dburi, repository=self.repository,
                            version=version)


class DbDowngrade(MigrateBase):
    '''Downgrades the database to an earlier version.'''

    option_list = (Option('version', type=int),)

    def run(self, version):
        self.init_logging()
        migrate_api.downgrade(url=self.dburi, repository=self.repository,
                              version=version)


class DbVersion(MigrateBase):
    '''Shows the current version of the database.'''

    def run(self):
        self.init_logging()
        print migrate_api.db_version(url=self.dburi,
                                     repository=self.repository)
