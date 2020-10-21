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


class sdist_hg(sdist):

    def initialize_options(self):
        filename_src = os.path.join(".", "setup.cfg")
        config_src = ConfigParser()

        config_src.read(filename_src)
        rel_vers=config_src.get("metadata", "version")

        sdist.initialize_options(self)
        self.version=(rel_vers)

    def run(self):
        if self.version:
            #suffix = '.dev%d' % self.get_tip_revision()
            #self.distribution.metadata.version += suffix
            self.distribution.metadata.version = self.version
            self.save_cfg_files()
        sdist.run(self)

    def save_cfg_files(self):

        filename = os.path.join("config", "meta.cfg")
        config = ConfigParser()

        config.read(filename)
        config.set("metadata", "version", self.version)
        with open(filename, 'w') as configfile:
            config.write(configfile)

def get_version():
    """Get version number of the package from version.py without importing core module."""
    package_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(package_dir, 'arancino/version.py')

    namespace = {}
    with open(version_file, 'rt') as f:
        exec(f.read(), namespace)

    return namespace['__version__']

setup(

    name='arancino',

    version=get_version(),

    description='Arancino Module for Arancino Library',

    long_description='Receives commands from Arancino Library (uC) trough the Arancino Cortex Protocol over serial connection. It is designed to run under Arancino OS and can manage multiple serial connections.',

    long_description_content_type="text/markdown",

    author='Sergio Tomasello',

    author_email='sergio@smartme.io',

    license='Apache License, Version 2.0',

    url='http://www.arancino.cc',

    classifiers=[   'Development Status :: 5 - Production/Stable',
                    'License :: OSI Approved :: Apache Software License',
                    'Programming Language :: Python :: 3',
                    'Environment :: Console',
                    'Operating System :: Unix'
                ],

    platforms=['Unix'],

    scripts=[],

    provides=['arancino'],

    packages=find_packages(exclude=["test"]),

    python_requires='>3',

    data_files=[('arancino',
        ['extras/pre-install.sh',
        'extras/post-install.sh',
        'extras/arancino.service',
        'config/meta.cfg',
        'config/arancino.cfg',
        'config/arancino.test.cfg',
        'LICENSE'])],

    #package_data={'arancino':['LICENSE','README.md','extras/*.*','config/*.*']},

    install_requires=['pyserial>=3.4', 'redis>=2.10.6', 'setuptools>=41.4.0', 'semantic-version==2.8.4', 'uptime==3.0.1', 'Flask==1.1.1', 'Flask_HTTPAuth==3.3.0', 'requests==2.23.0', 'netifaces==0.10.9'],

    include_package_data=True,

    zip_safe=False,

    cmdclass={
        'install': ArancinoPostInstallCommand,
        'sdist': sdist_hg
    },

    entry_points={
        'console_scripts': [
            'arancino=arancino.ArancinoStart:run'
        ]
    }
)
