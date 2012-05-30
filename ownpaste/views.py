from datetime import datetime, timedelta
from flask import Blueprint, abort, current_app, g, make_response, \
     render_template, request
from flask.views import MethodView
from pygments.formatters import HtmlFormatter
from ownpaste.models import Ip, Paste, db
from ownpaste.utils import LANGUAGES, AcceptMimeType, encrypt_password, \
     jsonify, textify

import os
import ownpaste

views = Blueprint('views', __name__)


@views.before_request
def before_request():
    g.accept = AcceptMimeType()


@views.route('/')
def home():
    languages = LANGUAGES.items()[:]
    languages.sort(key=lambda x: x[0])
    if g.accept.wants_text:
        rv = ['"language", "name"', '']
        for language in languages:
            rv.append('"%s","%s"' % language)
        return textify('\n'.join(rv), version=ownpaste.__version__)
    if g.accept.wants_json:
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
    if g.accept.wants_text:
        response = textify(**args)
    elif g.accept.wants_json:
        response = jsonify(args)
    else:
        response = make_response(args['error'])

    response.headers['WWW-Authenticate'] = 'Basic realm="ownpaste"'
    response.status_code = 401
    return response


@views.errorhandler(403)
def forbidden_handler(error):
    args = dict(status='fail', error='IP blocked')
    if g.accept.wants_text:
        response = textify(**args)
    elif g.accept.wants_json:
        response = jsonify(args)
    else:
        response = make_response(args['error'])
    response.status_code = 403
    return response


@views.errorhandler(404)
def notfound_handler(error):
    args = dict(status='fail', error='Resource not found')
    if g.accept.wants_text:
        response = textify(**args)
    elif g.accept.wants_json:
        response = jsonify(args)
    else:
        response = make_response(args['error'])
    response.status_code = 404
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
        if ip.blocked_date + timeout_delta > datetime.now():

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

            # text api
            if g.accept.wants_text:
                rv = ['"paste_id","language","file_name","pub_timestamp",'
                      '"private","private_id"', '']
                for paste in pagination.items:
                    rv.append('"%s","%s","%s",%i,%i,"%s"' %
                              (paste.paste_id, paste.language or '',
                               paste.file_name or '', paste.pub_timestamp,
                               paste.private, paste.private_id or ''))
                return textify('\n'.join(rv), **kwargs)

            # json api
            if g.accept.wants_json:
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

                # text api
                if g.accept.wants_text:
                    return textify(**paste.to_text())

                # json api
                if g.accept.wants_json:
                    return jsonify(paste.to_json())

                # html output
                return render_template('paste.html', file_name=paste.file_name,
                                       paste=paste.file_content_highlighted)

            # browser goodies

            # plain text output
            if action == 'raw':
                return textify(paste.file_content, show_status=False)

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

        file_name = request.args.get('file_name')
        language = request.args.get('language')
        private = request.args.get('private', '0') == '1'
        file_content = request.data

        # create object
        paste = Paste(file_content, file_name, language, private)

        db.session.add(paste)
        db.session.commit()

        args = dict(paste_id=paste.paste_id, private=paste.private,
                    private_id=paste.private_id)

        # text response
        if g.accept.wants_text:
            args.update(private=int(paste.private))
            return textify(**args)

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody who doesn't prefers text.
        return jsonify(args)

    def delete(self, paste_id):
        auth_required()

        paste = paste = Paste.get(paste_id)
        db.session.delete(paste)
        db.session.commit()

        # text response
        if g.accept.wants_text:
            return textify()

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody who doesn't prefers text.
        return jsonify()

    def put(self, paste_id):
        auth_required()

        file_name = request.args.get('file_name')
        language = request.args.get('language')
        private = request.args.get('private', '0') == '1'
        file_content = request.data

        paste = Paste.get(paste_id)
        if file_name is not None:
            paste.file_name = file_name
        if language is not None:
            paste.language = language
        paste.private = private
        if len(file_content):
            paste.file_content = file_content
        db.session.commit()

        args = dict(paste_id=paste.paste_id, private=paste.private,
                    private_id=paste.private_id)

        # text response
        if g.accept.wants_text:
            args.update(private=int(paste.private))
            return textify(**args)

        # this api method isn't intended to be used in browsers, then we will
        # return json for everybody who doesn't prefers text.
        return jsonify(args)


paste_view = PasteAPI.as_view('paste_api')
views.add_url_rule('/paste/', defaults={'paste_id': None, 'action': None},
                   view_func=paste_view, methods=['GET'])
views.add_url_rule('/paste/', view_func=paste_view, methods=['POST'])
views.add_url_rule('/paste/<paste_id>/', view_func=paste_view,
                   methods=['GET', 'DELETE', 'PUT'])
views.add_url_rule('/paste/<paste_id>/<action>/', view_func=paste_view,
                   methods=['GET'])
