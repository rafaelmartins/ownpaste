import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..')))

from ownpaste import main

sys.exit(main())
