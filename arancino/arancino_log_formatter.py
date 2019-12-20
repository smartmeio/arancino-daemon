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

import logging

class CustomConsoleFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    """Based on https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    blue = '\x1b[94:21m'
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_pre = "%(asctime)s - %(name)s - "
    format_post ="%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: format_pre + grey + format_post + reset,
        logging.INFO: format_pre + blue + format_post + reset,
        logging.WARNING: format_pre + yellow + format_post + reset,
        logging.ERROR: format_pre + red + format_post + reset,
        logging.CRITICAL: format_pre + bold_red + format_post + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
