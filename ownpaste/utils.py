from flask import jsonify as flask_jsonify, request, make_response
from hashlib import sha512
from pygments.lexers import get_all_lexers


def _languages():
    rv = {}
    for lexer in get_all_lexers():
        rv[lexer[1][0]] = lexer[0]
    return rv

LANGUAGES = _languages()
del _languages


def jsonify(*args, **kwargs):
    rv = dict(*args, **kwargs)
    if 'status' not in rv:
        rv['status'] = 'ok'
    return flask_jsonify(rv)


def textify(content=None, show_status=True, **kwargs):
    rv = []
    kwargs.setdefault('status', u'ok')
    if not show_status:
        kwargs.pop('status')
    meta_list = kwargs.items()
    meta_list.sort(key=lambda x: x[0])
    for meta in meta_list:
        rv.append('# %s: %s' % meta)
    if content is not None:
        if len(meta_list):
            rv.append('')
        rv.append(content)
    response = make_response('\n'.join(rv))
    response.headers['Content-Type'] = 'text/plain'
    return response


def encrypt_password(password):
    return sha512(password).hexdigest()


class AcceptMimeType(object):

    def __init__(self):
        self.text = request.accept_mimetypes['text/plain']
        self.json = request.accept_mimetypes['application/json']
        self.html = request.accept_mimetypes['text/html']
        self.best = request.accept_mimetypes.best_match(['text/plain',
                                                         'application/json',
                                                         'text/html'])

    @property
    def wants_text(self):
        return self.best == 'text/plain' and \
               self.text > self.json and \
               self.text > self.html

    @property
    def wants_json(self):
        return self.best == 'application/json' and \
               self.json > self.text and \
               self.json > self.html
