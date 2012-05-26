from flask import Blueprint, render_template, current_app, make_response
from pygments.formatters import HtmlFormatter
from ownpaste.models import Paste

import os

views = Blueprint('views', __name__)


@views.route('/')
@views.route('/page/<int:page>/')
def page(page=1):
    query = Paste.all_public()
    per_page = current_app.config['PER_PAGE']
    return render_template('base.html',
                           pagination=query.paginate(page, per_page))


@views.route('/show/<paste_id>/')
def show(paste_id):
    paste = Paste.get(paste_id)
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
    print paste.lexer
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
    response =make_response(formatter.get_style_defs(('#paste', '.syntax')))
    response.headers['Content-Type'] = 'text/css'
    return response

