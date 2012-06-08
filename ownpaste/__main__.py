# -*- coding: utf-8 -*-
"""
    ownpaste.__main__
    ~~~~~~~~~~~~~~~~~

    Main script endpoint.

    :copyright: (c) 2012 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..')))

from ownpaste import main

sys.exit(main())
