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

from pathlib import Path
from typing import Optional
from typing import Union

from operations.models import append_suffix_to_filepath
from operations.models import get_timestamp


class DuplicatedFileNames:
    """Store information about source files that already exist at destination.

    File path should be used without the bucket name.
    Use: 'admin/folder/file.txt'
    Do not use: 'gr-project-code/admin/folder/file.txt'
    """

    def __init__(self) -> None:
        self.filename_timestamp = get_timestamp()
        self.files = {}

    def __str__(self) -> str:
        return f'Count: {len(self.files)}'

    def add(self, filepath: Union[Path, str]) -> str:
        """Store information about duplicated file and return new filename that should be used."""

        path = Path(filepath)

        self.files[path] = append_suffix_to_filepath(path.name, self.filename_timestamp)

        return self.files[path]

    def get(self, filepath: Union[Path, str], default: Optional[str] = '') -> str:
        """Return filename by filepath if it exists or return default value."""

        path = Path(filepath)

        try:
            return self.files[path]
        except KeyError:
            pass

        return default
