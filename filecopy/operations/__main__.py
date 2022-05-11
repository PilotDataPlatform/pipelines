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

from operations.app import app
from operations.commands.copy import copy
from operations.commands.delete import delete

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s\t%(levelname)s\t[%(name)s]\t%(message)s')

    app.add_command(copy)
    app.add_command(delete)
    app()
