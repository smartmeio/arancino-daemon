'''
SPDX-license-identifier: Apache-2.0

Copyright (c) 2019 SmartMe.IO

Authors:  Sergio Tomasello <sergio@smartme.io>

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License
'''

from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import call
from distutils.command.sdist import sdist
import os
import re
from configparser import ConfigParser

class ArancinoPostInstallCommand(install):
    """
    Customized setuptools install command used as 
    post-install script to install Arancino services
    """

    def run(self):
        call(["chmod", "+x", "extras/pre-install.sh"])
        call(["chmod", "+x", "extras/post-install.sh"])

        #### ARANCINO PRE INSTALL
        print("--------------------------------------")
        print("START ARANCINO PRE INSTALL")
        call(["extras/pre-install.sh"])       
        print("END ARANCINO PRE INSTALL")
        print("--------------------------------------")
        
        #### ARANCINO INSTALL
        print("--------------------------------------")
        print("START ARANCINO INSTALL")
        install.run(self)
        print("END ARANCINO INSTALL")
        print("--------------------------------------")
        
        #### ARANCINO POST INSTALL
        print("--------------------------------------")
        print("START ARANCINO POST INSTALL")
        call(["extras/post-install.sh"])
        print("END ARANCINO POST INSTALL")
        print("--------------------------------------")

def get_version():
    """Get version number of the package from version.py without importing core module."""
    package_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(package_dir, 'arancino/version.py')

    namespace = {}
    with open(version_file, 'rt') as f:
        exec(f.read(), namespace)

    return namespace['__version__']

with open("arancino/version.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read())

setup(

    version=version,

    provides=['arancino'],

    cmdclass={
        'install': ArancinoPostInstallCommand
    },

)
