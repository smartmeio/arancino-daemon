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

setup(

    name='arancino',

    version='0.1.0',

    description='Arancino Module for Arancino Library',

    author='Sergio Tomasello',

    author_email='sergio@smartme.io',

    #url='http://www.smartme.io,

    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python :: 3',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=['arancino'],

    packages=find_packages(),

    include_package_data=True,

    entry_points={
        's4t.modules': [
            'arancino_module = arancino_module.arancino_module:ArancinoTestModule',
        ],
    },

    zip_safe=False,
)