Upgrade notes
=============

Upgrading from 0.1
------------------

Versions newer than 0.1 are using sqlalchemy-migrate to manage the database.

Run the following commands to initialize the sqlalchemy-migrate repository::

    $ ownpaste db_version_control 1 --config-file=/path/to/config-file.cfg
    $ ownpaste db_upgrade --config-file=/path/to/config-file.cfg

You'll also need to re-generate the password hash, using the following command::
    
    $ ownpaste generatepw --config-file=/path/to/config-file.cfg

Please follow the instructions, and update the password in your configuration
file.
