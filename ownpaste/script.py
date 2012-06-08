from flask.ext.script import Command, prompt_pass
from werkzeug.security import generate_password_hash
from ownpaste.models import db

import sys


class InitDb(Command):
    '''Initializes the database.'''

    def run(self):
        db.create_all()


class GeneratePw(Command):
    '''Generates a safe password for your configuration file.'''

    def run(self):
        p1 = prompt_pass('Password')
        p2 = prompt_pass('Retype password')
        if p1 != p2:
            print >> sys.stderr, 'Passwords didn\'t match.'
            return
        print
        print 'Add this to your configuration file:'
        print 'PASSWORD = \'%s\'' % generate_password_hash(p1)
