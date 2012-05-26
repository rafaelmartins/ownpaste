from flask import Flask, _request_ctx_stack
from flask.ext.script import Manager
from ownpaste.models import db, Paste
from ownpaste.views import views


def create_app(database=None):
    app = Flask(__name__)
    app.config.setdefault('PYGMENTS_STYLE', 'friendly')
    app.config.setdefault('PYGMENTS_LINENOS', True)
    app.config.setdefault('PER_PAGE', 20)
    app.config['SQLALCHEMY_DATABASE_URI'] = database or \
        'sqlite:////tmp/ownpaste.db'
    db.init_app(app)
    app.register_blueprint(views)
    return app


def create_script():
    manager = Manager(create_app, with_default_commands=True)
    manager.add_option('-d', '--database', dest='database', required=False)

    @manager.shell
    def _make_context():
        return dict(app=_request_ctx_stack.top.app, db=db, Paste=Paste)

    return manager
