#!/usr/bin/env python
from migrate.versioning.shell import main

import os
import sys
cwd = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    main(debug='False', repository=cwd)
