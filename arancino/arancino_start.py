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
def run():
    import os

    ENV = os.environ.get('ARANCINOENV')

    #if ENV == "PROD":
    # PROD
    from arancino.arancino_main import Arancino 
    import arancino.arancino_constants as Const
    # else:
    #     # DEV
    #     from arancino.arancino_main import Arancino 
    #     import arancino.arancino_constants as Const

    a = Arancino()
    a.start()


if __name__ == "__main__":
    run()