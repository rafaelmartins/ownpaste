# -*- coding: utf-8 -*-
"""
    ownpaste.auth
    ~~~~~~~~~~~~~

    Module for HTTP Digest Authentication handling.

    :copyright: (c) 2012 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime, timedelta
from flask import abort, current_app, make_response, request
from hashlib import md5
from ownpaste.models import Ip, db
from ownpaste.utils import jsonify, request_wants_json

import os


class HTTPDigestAuth(object):

    def hash(self, *args):
        return md5(u':'.join(map(unicode, args))).hexdigest()

    def a1(self, password, username=None, realm=None):
        return self.hash(username or current_app.config['USERNAME'],
                         realm or current_app.config['REALM'],
                         password)

    def a2(self, method=None, uri=None):
        return self.hash(method or request.method,
                         uri or request.authorization.uri)

    def response(self, a1=None, a2=None, nonce=None, nc=None, cnonce=None,
                 qop=None):
        return self.hash(a1 or self.a1(), nonce or request.authorization.nonce,
                         nc or request.authorization.nc,
                         cnonce or request.authorization.cnonce,
                         qop or request.authorization.qop, a2 or self.a2())

    def challenge(self, error):
        ip = Ip.get(request.remote_addr)
        if request_wants_json():
            response = jsonify(dict(status='fail',
                                    error='Authentication required'))
        else:
            response = make_response(error.get_body(request.environ))

        # create nonce. the client should return the request with the
        # authentication data and the same nonce
        ip.nonce = os.urandom(8).encode('hex')
        db.session.commit()

        # set digest response
        response.www_authenticate.set_digest(realm=current_app.config['REALM'],
                                             nonce=ip.nonce, qop=['auth'],
                                             algorithm='MD5')
        response.status_code = 401
        return response

    def verify_auth(self):
        auth = request.authorization
        if auth.username != current_app.config['USERNAME']:
            return False
        response = self.response(a1=current_app.config['PASSWORD'])
        if response.lower() != auth.response.lower():
            return False
        return True

    def required(self):
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
        if auth is None or auth.response is None:
            abort(401)

        # verify if the client returned the sended nonce
        if ip.nonce is not None and ip.nonce.lower() != auth.nonce.lower():
            abort(400)

        # if user or password are wrong
        if not self.verify_auth():

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

        # validation passed! user autenticated!
        # at this point we can drop the ip from the table :)
        db.session.delete(ip)
        db.session.commit()
