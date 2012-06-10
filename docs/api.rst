RESTful API documentation
=========================

ownpaste provides a neat RESTful API, that can returns HTML and JSON on demand,
as required by the client, and that can receive JSON data from the client as
well.

The returned content (``application/json`` or ``text/html``) is controlled by
the ``Accept:`` HTTP header.

Our current API version is ``1``.

This section of the documentation will explain the API endpoints and methods.

The tables with returned/received objects are related to the JSON API and
usually (but not always) to the variables that can be used by Jinja templates.

The tables with query string parameters are related to any API format.

All the methods and endpoints will be able to return a JSON object, some of
them can return HTML, and some of them can receive a JSON object in the body
of the request.

Some methods will require digest authentication. Use the credetials created
during the server setup phase.


Base JSON response object
-------------------------

All the methods, when returning JSON data, will have a common base format:

+--------+--------+-------------------------------------------+
| Key    | Type   | Description                               |
+========+========+===========================================+
| status | String | Status of the request. ``ok`` or ``fail`` |
+--------+--------+-------------------------------------------+

If ``status`` is equals to ``fail`` another key will be added:

+-------+--------+----------------------------------------+
| Key   | Type   | Description                            |
+=======+========+========================================+
| error | String | Description of the error that happened |
+-------+--------+----------------------------------------+


``/`` endpoint
--------------

This endpoint returns some basic information about the ownpaste instance.

GET ``/``
~~~~~~~~~

This method returns HTML or JSON.

Returned object:

+-------------+--------+--------------------------------------------------------+
| Key         | Type   | Description                                            |
+=============+========+========================================================+
| version     | String | ownpaste version                                       |
+-------------+--------+--------------------------------------------------------+
| api_version | String | API version                                            |
+-------------+--------+--------------------------------------------------------+
| language    | Object | Languages available on the ownpaste instance. Keys are |
|             |        | the language aliases and values are the language names |
+-------------+--------+--------------------------------------------------------+

``/paste/`` endpoint
--------------------

This endpoint deals with the pastes itself, being able to list, add, delete,
change, etc.

GET ``/paste/``
~~~~~~~~~~~~~~~

This method returns HTML or JSON. It lists the pastes available (public or
public+private) with pagination.

Query string parameters:

+---------+---------+-----------------------------------------------------+
| Key     | Type    | Description                                         |
+=========+=========+=====================================================+
| page    | Integer | Page index for pagination. Defaults to 1            |
+---------+---------+-----------------------------------------------------+
| private | Integer | If ``1`` will list private pastes as well. Requires |
|         |         | authentication                                      |
+---------+---------+-----------------------------------------------------+

Returned object:

+----------+---------+--------------------------------------------------+
| Key      | Type    | Description                                      |
+==========+=========+==================================================+
| page     | Integer | Current page, for pagination                     |
+----------+---------+--------------------------------------------------+
| pages    | Integer | Total number of pages, for pagination            |
+----------+---------+--------------------------------------------------+
| per_page | Integer | Number of pastes per page, for pagination        |
+----------+---------+--------------------------------------------------+
| total    | Integer | Total number of pastes in the database           |
+----------+---------+--------------------------------------------------+
| pastes   | List    | List of objects with specific data of each paste |
+----------+---------+--------------------------------------------------+

The ``pastes`` list will have objects with the following format:

+----------------------+---------+-------------------------------------------+
| Key                  | Type    | Description                               |
+======================+=========+===========================================+
| paste_id             | Integer | Numeric unique ID of the paste            |
+----------------------+---------+-------------------------------------------+
| language             | String  | Language alias of the paste language      |
+----------------------+---------+-------------------------------------------+
| file_name            | String  | File name of the paste, or None           |
+----------------------+---------+-------------------------------------------+
| pub_timestamp        | Integer | UTC Unix timestamp of the creation date   |
+----------------------+---------+-------------------------------------------+
| private              | Boolean | Paste is private?                         |
+----------------------+---------+-------------------------------------------+
| private_id           | String  | If paste is private, the paste unique ID, |
|                      |         | otherwise None                            |
+----------------------+---------+-------------------------------------------+
| file_content_preview | String  | First 5 lines of the paste file content   |
+----------------------+---------+-------------------------------------------+


GET ``/paste/<paste_id>/``
~~~~~~~~~~~~~~~~~~~~~~~~~~

This method returns HTML or JSON. It returns details of a paste, by the paste
public or private ID. It will requires authentication if you want to retrieve
data of a private post using the public (numeric) ID.

Returned object:

+---------------+---------+-----------------------------------------------------+
| Key           | Type    | Description                                         |
+===============+=========+=====================================================+
| paste_id      | Integer | Numeric unique ID of the paste                      |
+---------------+---------+-----------------------------------------------------+
| language      | String  | Language alias of the paste language                |
+---------------+---------+-----------------------------------------------------+
| file_name     | String  | File name of the paste, or None                     |
+---------------+---------+-----------------------------------------------------+
| pub_timestamp | Integer | UTC Unix timestamp of the creation date             |
+---------------+---------+-----------------------------------------------------+
| private       | Boolean | Paste is private?                                   |
+---------------+---------+-----------------------------------------------------+
| private_id    | String  | If paste is private, the paste unique ID, otherwise |
|               |         | None                                                |
+---------------+---------+-----------------------------------------------------+
| file_content  | String  | The full paste file content                         |
+---------------+---------+-----------------------------------------------------+


POST ``/paste/``
~~~~~~~~~~~~~~~~

This method just returns JSON. It will add a new paste to the database. It
requires authentication.

Received object:

+---------------+---------+----------------------------------------------------+
| Key           | Type    | Description                                        |
+===============+=========+====================================================+
| language      | String  | Language alias of the paste language. Optional,    |
|               |         | language will be guessed if not provided or None   |
+---------------+---------+----------------------------------------------------+
| file_name     | String  | File name of the paste. Optional, defaults to None |
+---------------+---------+----------------------------------------------------+
| private       | Boolean | Paste is private? Optional, defaults to False      |
+---------------+---------+----------------------------------------------------+
| file_content  | String  | The full paste file content                        |
+---------------+---------+----------------------------------------------------+

Returned object:

+----------------------+---------+-------------------------------------------+
| Key                  | Type    | Description                               |
+======================+=========+===========================================+
| paste_id             | Integer | Numeric unique ID of the paste            |
+----------------------+---------+-------------------------------------------+
| language             | String  | Language alias of the paste language      |
+----------------------+---------+-------------------------------------------+
| file_name            | String  | File name of the paste, or None           |
+----------------------+---------+-------------------------------------------+
| pub_timestamp        | Integer | UTC Unix timestamp of the creation date   |
+----------------------+---------+-------------------------------------------+
| private              | Boolean | Paste is private?                         |
+----------------------+---------+-------------------------------------------+
| private_id           | String  | If paste is private, the paste unique ID, |
|                      |         | otherwise None                            |
+----------------------+---------+-------------------------------------------+
| file_content_preview | String  | First 5 lines of the paste file content   |
+----------------------+---------+-------------------------------------------+


PATCH ``/paste/<paste_id>/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method just returns JSON. It will change an existing paste. It requires
authentication.

Received object (all parameters are optional, and will be changed if provided):

+---------------+---------+--------------------------------------+
| Key           | Type    | Description                          |
+===============+=========+======================================+
| language      | String  | Language alias of the paste language |
+---------------+---------+--------------------------------------+
| file_name     | String  | File name of the paste               |
+---------------+---------+--------------------------------------+
| private       | Boolean | Paste is private?                    |
+---------------+---------+--------------------------------------+
| file_content  | String  | The full paste file content          |
+---------------+---------+--------------------------------------+

Returned object:

+----------------------+---------+-------------------------------------------+
| Key                  | Type    | Description                               |
+======================+=========+===========================================+
| paste_id             | Integer | Numeric unique ID of the paste            |
+----------------------+---------+-------------------------------------------+
| language             | String  | Language alias of the paste language      |
+----------------------+---------+-------------------------------------------+
| file_name            | String  | File name of the paste, or None           |
+----------------------+---------+-------------------------------------------+
| pub_timestamp        | Integer | UTC Unix timestamp of the creation date   |
+----------------------+---------+-------------------------------------------+
| private              | Boolean | Paste is private?                         |
+----------------------+---------+-------------------------------------------+
| private_id           | String  | If paste is private, the paste unique ID, |
|                      |         | otherwise None                            |
+----------------------+---------+-------------------------------------------+
| file_content_preview | String  | First 5 lines of the paste file content   |
+----------------------+---------+-------------------------------------------+


DELETE ``/paste/<paste_id>/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method just returns JSON. It will remove a paste from the database.

Use the ``status`` key from the base JSON object to know if the delete request
was successful.

