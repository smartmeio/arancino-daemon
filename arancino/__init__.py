# -*- coding: utf-8 -*-
"""
    arancino
    ~~~~~~~~~~~~~~~~~~~~~~~~

    A Python module for Arancino Lirbrary.

    :copyright: Copyright 2007-2018 by the SmartME team, see README.
    :license: BSD, see LICENSE for details.
"""
from os import path

__import__('pkg_resources').declare_namespace(__name__)

package_dir = path.abspath(path.dirname(__file__))

from arancino import *
from arancino.version import __version__
from arancino.version import __cortex__version__
