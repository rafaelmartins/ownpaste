# -*- coding: utf-8 -*-
"""
    ownpaste.utils
    ~~~~~~~~~~~~~~

    Module with helpers and utilities.

    :copyright: (c) 2012 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from collections import OrderedDict
from flask import jsonify as flask_jsonify, request
from jinja2 import Markup
from pygments.lexers import get_all_lexers
from werkzeug.exceptions import HTTPException


def _languages():
    rv = OrderedDict()
    lexers = list(get_all_lexers())
    lexers.sort(key=lambda x: x[0])
    for lexer in lexers:
        for alias in lexer[1]:
            rv[alias] = lexer[0]
    return rv

LANGUAGES = _languages()
del _languages


def jsonify(*args, **kwargs):
    rv = dict(*args, **kwargs)
    if 'status' not in rv:
        rv['status'] = 'ok'
    return flask_jsonify(rv)


def request_wants_json():
    # based on: http://flask.pocoo.org/snippets/45/
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


def error_handler(error):
    if not isinstance(error, HTTPException):
        raise error
    if request_wants_json():
        desc = error.get_description(request.environ)
        desc = Markup(desc[:desc.find('.')]).striptags()
        error_str = '%s: %s' % (error.name, desc)
        response = jsonify(status='fail', error=error_str)
        response.status_code = error.code
        return response
    return error
