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
from subprocess import check_call, call

class ArancinoPostInstallCommand(install):
    """
    Customized setuptools install command used as 
    post-install script to install Arancino services
    """
    def run(self):
        print("INSTALL PRE")

        install.run(self)

        #call(["systemctl","enable","redis-persistent"])
        #call(["systemctl","enable","redis-volatile"])
        #call(["systemctl","enable","arancino"])

        print("INSTALL POST")

        #move redis configuration files:
        print("CALL PWD")
        call(["pwd"])
        print("CALL LS")
        call(["ls","-alh"])
        print("INSTALL END")




with open("README.md", "r") as fh:
    long_description = fh.read()

setup(

    name='arancino',

    version='1.0.0',

    description='Arancino Module for Arancino Library',

    long_description=long_description,

    long_description_content_type="text/markdown",

    author='Sergio Tomasello @ SmartMe.IO',

    author_email='sergio@smartme.io',

    license='Apache License, Version 2.0',

    url='http://www.arancino.cc',

    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python :: 3',
                 'Environment :: Console',
                 'Operating System :: Unix'
                 ],

    platforms=['Unix'],

    scripts=[],

    provides=['arancino'],

    packages=find_packages(exclude=["test"]),

    #data_files=[('/arancino/extras/', ['post-install.sh','extras/arancino.service', 'extras/redis-persistent.conf', 'extras/redis-persistent.service', 'extras/redis-volatile.conf', 'extras/redis-volatile.service'])],
    data_files=[('/arancino/extras/', ['extras/arancino.service', 'extras/redis-persistent.conf', 'extras/redis-persistent.service', 'extras/redis-volatile.conf', 'extras/redis-volatile.service'])],

    install_requires=['pyserial>=3.4', 'redis>=2.10.6'],

    include_package_data=True,

    zip_safe=False,

    cmdclass={
        'install': ArancinoPostInstallCommand,
    },
)
