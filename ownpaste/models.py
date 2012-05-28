from datetime import datetime
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name, guess_lexer, \
     guess_lexer_for_filename

import random
import string
import time

db = SQLAlchemy()


class Private(object):

    def _random_id(self, length=20):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for x in range(length))

    def __get__(self, obj, cls):
        return obj.private_id is not None

    def __set__(self, obj, value):
        if not value:
            obj.private_id = None
            return

        # we should not override existing private_id
        if obj.private_id is not None:
            return

        # loop until find an unique id
        while 1:
            obj.private_id = self._random_id()
            paste = Paste.query.filter(db.and_(
                Paste.private_id == obj.private_id,
                Paste.paste_id != obj.paste_id)).first()
            if paste is None:
                break


class Blocked(object):

    def __get__(self, obj, cls):
        return obj.blocked_date is not None

    def __set__(self, obj, value):
        if not value:
            obj.blocked_date = None
            obj.hits = 0
            return

        # we should not override existing blocked_date
        if obj.blocked_date is not None:
            return

        obj.blocked_date = datetime.now()


class Paste(db.Model):

    paste_id = db.Column(db.Integer, primary_key=True)
    private_id = db.Column(db.String(40), unique=True, nullable=True)
    language = db.Column(db.String(30))
    file_name = db.Column(db.Text, nullable=True)  # not extensively used yet
    file_content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    private = Private()

    def __init__(self, file_content, file_name=None, language=None,
                 private=False):
        self.file_content = u'\n'.join(file_content.splitlines())
        self.file_name = file_name
        self.language = language
        self.private = private
        self.pub_date = datetime.now()

        # guess language, if needed
        if self.language is None:
            if self.file_name is None:
                lexer = guess_lexer(self.file_content)
            else:
                lexer = guess_lexer_for_filename(self.file_name,
                                                 self.file_content)
            self.language = lexer.aliases[0]

    @property
    def pub_timestamp(self):
        return int(time.mktime(self.pub_date.timetuple()))

    @staticmethod
    def get(paste_id):
        if isinstance(paste_id, basestring) and not paste_id.isdigit():
            return Paste.query.filter(
                Paste.private_id == paste_id).first_or_404()
        return Paste.query.filter(
            Paste.paste_id == int(paste_id)).first_or_404()

    @staticmethod
    def all(hide_private=True):
        if hide_private:
            query = Paste.query.filter(Paste.private_id == None)
        else:
            query = Paste.query
        return query.order_by(Paste.paste_id.desc())

    @property
    def lexer(self):
        try:
            return get_lexer_by_name(self.language)
        except:
            return TextLexer

    @property
    def file_content_highlighted(self):
        linenos = current_app.config['PYGMENTS_LINENOS']
        style = current_app.config['PYGMENTS_STYLE']
        formatter = HtmlFormatter(linenos=linenos, style=style,
                                  cssclass='syntax')
        return Markup('<div id="paste">%s</div>' % \
                      highlight(self.file_content, self.lexer, formatter))

    def to_json(self, short=False):
        rv = dict(paste_id=self.paste_id, language=self.language,
                  file_name=self.file_name, pub_timestamp=self.pub_timestamp,
                  private=self.private, private_id=self.private_id)
        if short:
            rv.update(file_content_preview='\n'.join(
                self.file_content.splitlines()[:5]))
        else:
            rv.update(file_content=self.file_content,
                      file_content_highlighted=self.file_content_highlighted)
        return rv

    def to_text(self, short=False):
        rv = self.to_json(short)
        rv['private'] = int(rv['private'])
        for key in rv.keys():
            if key.startswith('file_content'):
                rv.pop(key)
        return rv

    def __repr__(self):
        return '<%s %s: language=%s; private=%r>' % \
               (self.__class__.__name__, self.file_name or 'unnamed',
                self.language, self.private)


class Ip(db.Model):

    ip_id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True)
    hits = db.Column(db.Integer)
    blocked_date = db.Column(db.DateTime, nullable=True)
    blocked = Blocked()

    def __init__(self, ip):
        self.ip = ip
        self.hits = 0
        self.blocked = False

    @classmethod
    def get(cls, ip):
        obj = cls.query.filter(cls.ip == ip).first()
        if obj is None:
            obj = cls(ip)
            db.session.add(obj)
            db.session.commit()
        return obj

    def __repr__(self):
        rv = '<%s %s: ' % (self.__class__.__name__, self.ip)
        if self.blocked:
            rv += 'blocked>'
        else:
            rv += '%i hits>' % self.hits
        return rv
