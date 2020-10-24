Upgrade notes
=============

Upgrading from 0.1
------------------

Versions newer than 0.1 are using sqlalchemy-migrate to manage the database.

Run the following commands to initialize the sqlalchemy-migrate repository::

    $ ownpaste --config-file=/path/to/config-file.cfg db_version_control 1
    $ ownpaste --config-file=/path/to/config-file.cfg db_upgrade

You'll also need to re-generate the password hash, using the following command::

    $ ownpaste --config-file=/path/to/config-file.cfg generatepw

Please follow the instructions, and update the password in your configuration
file.
