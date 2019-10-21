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
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from subprocess import check_call, call
from os import system

class ArancinoPostInstallCommand(install):
    """
    Customized setuptools install command used as 
    post-install script to install Arancino services
    """
    def run(self):

        call(["pwd"])
        call(["ls","-alh"])

        #### ARANCINO PRE INSTALL
        print("START ARANCINO PRE INSTALL")
        call(["chmod","+x","extras/pre-install.sh"])
        call(["extras/pre-install.sh"])       
        print("END ARANCINO PRE INSTALL")
        
        #### ARANCINO INSTALL
        print("START ARANCINO INSTALL")
        install.run(self)
        print("POST ARANCINO INSTALL")
        
        #### ARANCINO POST INSTALL
        print("START ARANCINO POST INSTALL")
        call(["chmod","+x","extras/post-install.sh"])
        call(["extras/post-install.sh"])
        print("END ARANCINO POST INSTALL")



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

    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. If you
    # do not support Python 2, you can simplify this to '>=3.5' or similar, see
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>3',

    data_files=[('arancino',
		['extras/pre-install.sh',
		'extras/post-install.sh',
		'extras/arancino.service',
		'extras/redis-persistent.conf',
		'extras/redis-persistent.service',
		'extras/redis-volatile.conf',
		'extras/redis-volatile.service'])],

    install_requires=['pyserial>=3.4', 'redis>=2.10.6'],

    include_package_data=True,

    zip_safe=False,

    cmdclass={
        'install': ArancinoPostInstallCommand,
    },
)
