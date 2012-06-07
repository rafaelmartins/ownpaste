# ignore useless warnings about modules already imported.
import warnings
warnings.filterwarnings('ignore', r'module.*already imported', UserWarning)

from flask import Flask, _request_ctx_stack
from flask.ext.script import Manager
from werkzeug.exceptions import default_exceptions
from ownpaste.models import Ip, Paste, db
from ownpaste.utils import encrypt_password, error_handler
from ownpaste.views import views

version = __version__ = '0.1pre'
api_version = '1'


def create_app(config_file=None):
    app = Flask(__name__)
    app.config.setdefault('PYGMENTS_STYLE', 'friendly')
    app.config.setdefault('PYGMENTS_LINENOS', True)
    app.config.setdefault('PER_PAGE', 20)
    app.config.setdefault('SQLALCHEMY_DATABASE_URI',
                          'sqlite:////tmp/ownpaste.db')
    app.config.setdefault('USERNAME', 'ownpaste')
    app.config.setdefault('PASSWORD', encrypt_password('test'))
    app.config.setdefault('IP_BLOCK_HITS', 10)
    app.config.setdefault('IP_BLOCK_TIMEOUT', 60)  # in minutes
    app.config.setdefault('TIMEZONE', 'UTC')
    app.config.from_envvar('OWNPASTE_SETTINGS', True)
    if config_file is not None:
        app.config.from_pyfile(config_file)
    db.init_app(app)

    # register default error handler
    # based on: http://flask.pocoo.org/snippets/15/
    for _exc in default_exceptions:
        app.error_handlers[_exc] = error_handler
    del _exc

    app.register_blueprint(views)

    @app.before_first_request
    def before_first_request():
        if (not app.debug) and \
           (app.config['PASSWORD'] == encrypt_password('test')):
            raise RuntimeError('You should provide a password!!')

    return app


def create_script():
    manager = Manager(create_app, with_default_commands=True)
    manager.add_option('-c', '--config-file', dest='config_file',
                       required=False)

    @manager.shell
    def _make_context():
        return dict(app=_request_ctx_stack.top.app, db=db, Paste=Paste, Ip=Ip)

    return manager
