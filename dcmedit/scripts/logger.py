# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import logging
import logging.handlers
import sys


class Logger:
    def __init__(self, f, console=False, maxBytes=100000000, backupCount=1000):
        self.f = f
        self.logger = None
        self.setup(console, maxBytes, backupCount)

    def setup(self, console, maxBytes, backupCount):
        try:
            # setup the logger
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
            handler = logging.handlers.RotatingFileHandler(self.f, maxBytes=maxBytes, backupCount=backupCount)
            formatter = logging.Formatter('%(asctime)s-%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            if console:
                self.logger.addHandler(logging.StreamHandler(sys.stdout))
        except Exception as err:
            raise LoggerException(err)


class LoggerException(Exception):
    pass
