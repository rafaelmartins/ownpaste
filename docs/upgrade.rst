Upgrade notes
=============

Upgrading from 0.1
------------------

Versions newer than 0.1 are using sqlalchemy-migrate to manage the database.

Run the following commands to initialize the sqlalchemy-migrate repository::

    $ ownpaste db_version_control 1 --config-file=/path/to/config-file.cfg
    $ ownpaste db_upgrade --config-file=/path/to/config-file.cfg

