# -*- coding: utf-8 -*-
"""
    ownpaste.views
    ~~~~~~~~~~~~~~

    Module with Flask views.

    :copyright: (c) 2012 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint, abort, current_app, make_response, \
     render_template, request
from flask.views import MethodView
from pygments.formatters import HtmlFormatter
from ownpaste.auth import HTTPDigestAuth
from ownpaste.models import Paste, db
from ownpaste.utils import LANGUAGES, jsonify, request_wants_json

import os
import ownpaste

views = Blueprint('views', __name__)


@views.route('/')
def home():
    if request_wants_json():
        return jsonify(dict(version=ownpaste.__version__,
                            api_version=ownpaste.api_version,
                            languages=LANGUAGES))
    return render_template('base.html', version=ownpaste.__version__,
                           api_version=ownpaste.api_version,
                           languages=LANGUAGES.iteritems())


@views.route('/pygments.css')
def pygments_css():
    formatter = HtmlFormatter(style=current_app.config['PYGMENTS_STYLE'])
    response = make_response(formatter.get_style_defs(('#paste', '.syntax')))
    response.headers['Content-Type'] = 'text/css'
    return response


class PasteAPI(MethodView):

    def __init__(self, *args, **kwargs):
        self.auth = HTTPDigestAuth()
        MethodView.__init__(self, *args, **kwargs)

    def get(self, paste_id=None, action=None):

        # paste listing
        if paste_id is None:

            page = int(request.args.get('page', 1))
            per_page = current_app.config['PER_PAGE']

            # private mode
            if request.args.get('private', '0') == '1':
                self.auth.required()
                query = Paste.all(hide_private=False)

            # normal mode
            else:
                query = Paste.all()

            pagination = query.paginate(page or 1, per_page)
            kwargs = dict(page=pagination.page, pages=pagination.pages,
                          per_page=pagination.per_page, total=pagination.total)

            # json api
            if request_wants_json():
                return jsonify(dict(pastes=[i.to_json(True) \
                                            for i in pagination.items],
                                    **kwargs))

            # html output
            return render_template('pastes.html', pagination=pagination)

        # paste rendering
        else:

            paste = Paste.get(paste_id)

            # if private ask for authentication
            if paste.private and paste_id.isdigit():
                self.auth.required()

            # guess output by browser's accept header
            if action is None:

                # json api
                if request_wants_json():
                    return jsonify(paste.to_json())

                # html output
                return render_template('paste.html', paste=paste)

            # browser goodies

            # plain text output
            if action == 'raw':
                response = make_response(paste.file_content)
                response.headers['Content-type'] = 'text/plain; charset=utf-8'
                return response

            # force download
            if action == 'download':
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

            # no render found
            abort(404)

    def post(self):
        self.auth.required()

        try:
            data = request.json
        except:
            abort(400)

        if data is None:
            abort(415)

        file_name = data.get('file_name')
        language = data.get('language')
        private = data.get('private', False)
        if not isinstance(private, bool):
            raise(400)
        try:
            file_content = data['file_content']
        except KeyError:
            abort(400)

        # create object
        paste = Paste(file_content, file_name, language, private)

        db.session.add(paste)
        db.session.commit()

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody.
        return jsonify(paste.to_json(True))

    def delete(self, paste_id):
        self.auth.required()

        paste = paste = Paste.get(paste_id)
        db.session.delete(paste)
        db.session.commit()

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody.
        return jsonify()

    def patch(self, paste_id):
        self.auth.required()

        try:
            data = request.json
        except:
            abort(400)

        if data is None:
            abort(415)

        file_name = data.get('file_name')
        language = data.get('language')
        private = data.get('private')
        file_content = data.get('file_content')

        paste = Paste.get(paste_id)
        if file_name is not None:
            paste.file_name = file_name
        if language is not None:
            paste.language = language
        if private is not None:
            if not isinstance(private, bool):
                abort(400)
            paste.private = private
        if file_content is not None:
            if not isinstance(file_content, basestring):
                abort(400)
            paste.set_file_content(file_content)
        db.session.commit()

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody.
        return jsonify(paste.to_json(True))


paste_view = PasteAPI.as_view('paste_api')
views.add_url_rule('/paste/', defaults={'paste_id': None, 'action': None},
                   view_func=paste_view, methods=['GET'])
views.add_url_rule('/paste/', view_func=paste_view, methods=['POST'])
views.add_url_rule('/paste/<paste_id>/', view_func=paste_view,
                   methods=['GET', 'DELETE', 'PATCH'])
views.add_url_rule('/paste/<paste_id>/<action>/', view_func=paste_view,
                   methods=['GET'])
