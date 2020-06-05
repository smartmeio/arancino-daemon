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

from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from subprocess import check_call, call
from os import system
import os
import configparser
from distutils.command.sdist import sdist



#cfg_version = config_rel.get("metadata", "version")


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
    #https: // the - hitchhikers - guide - to - packaging.readthedocs.io / en / latest / specification.html  # development-releases
    user_options = sdist.user_options + [
            ('version=', None, "Add a version number")
        ]

    def initialize_options(self):
        sdist.initialize_options(self)
        self.version = "0.0.1"

    def run(self):
        if self.version:
            #suffix = '.dev%d' % self.get_tip_revision()
            #self.distribution.metadata.version += suffix
            self.distribution.metadata.version = self.version
            self.save_cfg_files()
        sdist.run(self)

    def get_tip_revision(self, path=os.getcwd()):
        # from mercurial.hg import repository
        # from mercurial.ui import ui
        # from mercurial import node
        # repo = repository(ui(), path)
        # tip = repo.changelog.tip()
        # return repo.changelog.rev(tip)
        return 0

    def save_cfg_files(self):

        filename_rel = os.path.join("config", "arancino.cfg")
        filename_tst = os.path.join("config", "arancino.test.cfg")

        config = configparser.ConfigParser()
        config.read(filename_rel)

        config.set("metadata", "version", self.version)
        #config_tst.set("metadata", "version", self.version)

        with open(filename_rel, 'w') as configfile:
            config.write(configfile)

        config.read(filename_tst)
        config.set("metadata", "version", self.version)
        with open(filename_tst, 'w') as configfile:
            config.write(configfile)


setup(

    name='arancino',

    #version='2.0.0',
    version=0,

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
        # 'extras/redis-persistent.conf',
        # 'extras/redis-persistent.service',
        # 'extras/redis-volatile.conf',
        # 'extras/redis-volatile.service',
        'config/arancino.cfg',
        'config/arancino.test.cfg'])],

    #package_data={'arancino':['LICENSE','README.md','extras/*.*','config/*.*']},

    install_requires=['pyserial>=3.4', 'redis>=2.10.6', 'setuptools==41.4.0', 'semantic-version==2.8.4', 'uptime==3.0.1', 'Flask==1.1.1', 'Flask_HTTPAuth==3.3.0', 'requests==2.23.0', 'netifaces==0.10.9'],

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
