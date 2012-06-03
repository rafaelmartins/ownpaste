from datetime import datetime, timedelta
from flask import Blueprint, abort, current_app, make_response, \
     render_template, request
from flask.views import MethodView
from pygments.formatters import HtmlFormatter
from ownpaste.models import Ip, Paste, db
from ownpaste.utils import LANGUAGES, encrypt_password, jsonify, \
     request_wants_json

import os
import ownpaste

views = Blueprint('views', __name__)


@views.route('/')
def home():
    languages = LANGUAGES.items()[:]
    languages.sort(key=lambda x: x[0])
    if request_wants_json():
        return jsonify(dict(version=ownpaste.__version__, languages=LANGUAGES))
    return render_template('base.html', version=ownpaste.__version__,
                           languages=languages)


@views.route('/pygments.css')
def pygments_css():
    formatter = HtmlFormatter(style=current_app.config['PYGMENTS_STYLE'])
    response = make_response(formatter.get_style_defs(('#paste', '.syntax')))
    response.headers['Content-Type'] = 'text/css'
    return response


@views.errorhandler(401)
def auth_handler(error):
    args = dict(status='fail', error='Authentication required')
    if request_wants_json():
        response = jsonify(args)
    else:
        response = make_response(args['error'])
    response.headers['WWW-Authenticate'] = 'Basic realm="ownpaste"'
    response.status_code = 401
    return response


def auth_required():

    # get the ip object from the database, or create it if needed
    ip = Ip.get(request.remote_addr)

    # verify the ip status
    if ip.blocked:

        # evaluate the timeout
        timeout = float(current_app.config['IP_BLOCK_TIMEOUT'])
        timeout_delta = timedelta(minutes=timeout)

        # if the ip is still banned
        if ip.blocked_date + timeout_delta > datetime.utcnow():

            # return 'forbidden'
            abort(403)

        # ban timeout expired
        ip.blocked = False
        db.session.commit()

    auth = request.authorization

    # no auth sent. ask for user/password
    if not auth:
        abort(401)

    # if user or password are wrong
    if auth.username != current_app.config['USERNAME'] or \
       encrypt_password(auth.password) != current_app.config['PASSWORD']:

        # we had a bad user/password, then let's increase the hit counter
        ip.hits += 1
        db.session.commit()

        # we need to block the ip?
        if ip.hits >= int(current_app.config['IP_BLOCK_HITS']):

            # block it
            ip.blocked = True
            db.session.commit()
            abort(403)

        # we want authentication!!
        abort(401)

    # valiadtion passed! user autenticated!
    # at this point we can drop the ip from the table :)
    db.session.delete(ip)
    db.session.commit()


class PasteAPI(MethodView):

    def get(self, paste_id=None, action=None):

        # paste listing
        if paste_id is None:

            page = int(request.args.get('page', 1))
            per_page = current_app.config['PER_PAGE']

            # private mode
            if request.args.get('private', '0') == '1':
                auth_required()
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
                auth_required()

            # guess output by browser's accept header
            if action is None:

                # json api
                if request_wants_json():
                    return jsonify(paste.to_json())

                # html output
                return render_template('paste.html', file_name=paste.file_name,
                                       paste=paste.file_content_highlighted)

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
        auth_required()

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
        auth_required()

        paste = paste = Paste.get(paste_id)
        db.session.delete(paste)
        db.session.commit()

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody.
        return jsonify()

    def patch(self, paste_id):
        auth_required()

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
