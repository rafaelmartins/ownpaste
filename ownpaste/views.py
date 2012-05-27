from flask import Blueprint, current_app, jsonify, make_response, \
     render_template, request
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers
from ownpaste.models import Paste

import os

views = Blueprint('views', __name__)


def _languages():
    rv = {}
    for lexer in get_all_lexers():
        rv[lexer[1][0]] = lexer[0]
    return rv

LANGUAGES = _languages()
del _languages


def request_wants_json():
    """code snippet from flask website."""
    best = \
        request.accept_mimetypes.best_match(['application/json', 'text/html'])
    print request.accept_mimetypes['text/html']
    return best == 'application/json' and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']


@views.route('/')
@views.route('/page/<int:page>/')
def page(page=None):
    query = Paste.all_public()
    if page is None and request_wants_json():
        return jsonify(dict(languages=LANGUAGES))
    per_page = current_app.config['PER_PAGE']
    return render_template('base.html',
                           pagination=query.paginate(page or 1, per_page))


@views.route('/show/<paste_id>/')
def show(paste_id):
    paste = Paste.get(paste_id)
    if request_wants_json():
        return jsonify(paste.to_json())
    return render_template('paste.html', file_name=paste.file_name,
                           paste=paste.file_content_highlighted)


@views.route('/raw/<paste_id>/')
def raw(paste_id):
    paste = Paste.get(paste_id)
    response = make_response(paste.file_content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@views.route('/download/<paste_id>/')
def download(paste_id):
    paste = Paste.get(paste_id)
    content_type = 'application/octet-stream'
    if len(paste.lexer.mimetypes):
        content_type = paste.lexer.mimetypes[0]
    file_name = 'untitled.txt'
    if paste.file_name is not None:
        file_name = os.path.basename(paste.file_name)
    response = make_response(paste.file_content)
    response.headers['Content-Type'] = content_type
    response.headers['Content-Disposition'] = \
        'attachment; filename=%s' % file_name
    return response


@views.route('/pygments.css')
def pygments_css():
    formatter = HtmlFormatter(style=current_app.config['PYGMENTS_STYLE'])
    response = make_response(formatter.get_style_defs(('#paste', '.syntax')))
    response.headers['Content-Type'] = 'text/css'
    return response
