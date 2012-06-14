Server setup
============

This section will guide you through the alternatives for setting up and
configuring ownpaste in your operating system. ownpaste is currently tested
on Linux_, but should works in other operating systems.

ownpaste works on Python 2.7.

ownpaste is available at the *Python Package Index* (PyPI_):

http://pypi.python.org/pypi/ownpaste

.. _Linux: http://kernel.org/
.. _PyPI: http://pypi.python.org/


Installing ownpaste
-------------------

Manually
~~~~~~~~

Download the latest tarball from PyPI_, extract it and run::

   # python setup.py install


Using ``pip``/``easy_install``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install blohg using ``pip``, type::

    # pip install ownpaste

Or using ``easy_install``, type::

    # easy_install ownpaste


Gentoo Linux
~~~~~~~~~~~~

There's a Gentoo_ ebuild available in the main tree. Install it using::

    # emerge -av www-apps/ownpaste

.. _Gentoo: http://www.gentoo.org/


Running ownpaste from the Mercurial repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also run ownpaste from the Mercurial repository. Just clone it and make
sure that it is added to your Python path::

    $ hg clone https://hg.rafaelmartins.eng.br/ownpaste/
    $ cd ownpaste/

The ``ownpaste`` script does not exists in the repository, but you can run it
using the following command from the repository root::

    $ python ownpaste/

``ownpaste/`` is the directory of the main Python package, with the ownpaste
implementation.


Configuring ownpaste
--------------------

These are the steps needed to configure ownpaste properly.


Generate password hash
~~~~~~~~~~~~~~~~~~~~~~

ownpaste is a private pastebin application, then you need an username and a
password to be able to add pastes. Password is saved in the configuration file,
but for security reasons you will want it hashed.

ownpaste provides an ``ownpaste`` script, that have some cool commands to help
you when deploying ownpaste.

The following command will ask you for the desired password, and output the hash
to be used in the configuration file::

    $ ownpaste generatepw --config-file=/path/to/config-file.cfg


Configuration parameters
~~~~~~~~~~~~~~~~~~~~~~~~

These are the configuration parameters available for ownpaste.

Please read the descriptions carefully and create your configuration file. The
configuration file is an usual python file, with the following variables:

+-------------------------+------------------------------+----------------------------------+
| Key                     | Default                      | Description                      |
+=========================+==============================+==================================+
| PYGMENTS_STYLE          | 'friendly'                   | Pygments style. See Pygments     |
|                         |                              | documentation for reference      |
+-------------------------+------------------------------+----------------------------------+
| PYGMENTS_LINENOS        | True                         | Enable Pygments line numbering   |
+-------------------------+------------------------------+----------------------------------+
| PER_PAGE                | 20                           | Number of pastes per page, for   |
|                         |                              | pagination                       |
+-------------------------+------------------------------+----------------------------------+
| SQLALCHEMY_DATABASE_URI | 'sqlite:////tmp/ownpaste.db' | SQL-Alchemy database string      |
+-------------------------+------------------------------+----------------------------------+
| REALM                   | 'ownpaste'                   | Realm for HTTP Digest auth.      |
+-------------------------+------------------------------+----------------------------------+
| USERNAME                | 'ownpaste'                   | Username                         |
+-------------------------+------------------------------+----------------------------------+
| PASSWORD                | hash of 'test'               | Password hash                    |
+-------------------------+------------------------------+----------------------------------+
| IP_BLOCK_HITS           | 10                           | Number of login attempts before  |
|                         |                              | block the user IP                |
+-------------------------+------------------------------+----------------------------------+
| IP_BLOCK_TIMEOUT        | 60                           | Timeout to remove IPs from block |
|                         |                              | blacklist                        |
+-------------------------+------------------------------+----------------------------------+
| TIMEZONE                | 'UTC'                        | Timezone                         |
+-------------------------+------------------------------+----------------------------------+

Please don't use the default 'test' password, it is *VERY* unsecure.

Save your configuration file somewhere.


Initializing the ownpaste database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll need to initialize the database with the needed tables. You can use any
database system supported by SQL-Alchemy.

The ``ownpaste`` script provides a command to initialize the database::

    $ ownpaste db_version_control --config-file=/path/to/config-file.cfg
    $ ownpaste db_upgrade --config-file=/path/to/config-file.cfg


Running ownpaste
~~~~~~~~~~~~~~~~

You can run ownpaste using the ``ownpaste`` script, for tests. The built-in
server can't handle a big request load, then please don't use it in production.

::

    $ ownpaste runserver --config-file=/path/to/config-file.cfg

You can also setup the configuration file path using the environment
variable ``OWNPASTE_SETTINGS``. This variable should contains a string
with the path of the configuration file.


Deploying ownpaste
~~~~~~~~~~~~~~~~~~

A simple wsgi file for ownpaste looks like this:

.. sourcecode:: python

   from ownpaste import create_app

   application = create_app('/path/to/config-file.cfg')


ownpaste is an usual Flask application, take a look at flask deployment
documentation for instructions:

http://flask.pocoo.org/docs/deploying/

Make sure that the ``REMOTE_ADDR`` and ``HTTP_AUTHORIZATION`` headers are being
passed to the ownpaste application by your web server of choice.

The IP-based blocker, to avoid brute-force attacks, will fail if ``REMOTE_ADDR``
isn't correct.

