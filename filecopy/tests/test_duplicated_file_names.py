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

import pytest
from operations.duplicated_file_names import DuplicatedFileNames


@pytest.fixture
def duplicated_files() -> DuplicatedFileNames:
    yield DuplicatedFileNames()


class TestDuplicatedFileNames:
    def test_add_stores_filename_with_timestamp_for_given_filepath(self, duplicated_files, fake):
        filepath = fake.file_path(depth=3)

        expected_filename = f'{Path(filepath).stem}_{duplicated_files.filename_timestamp}{Path(filepath).suffix}'

        received_filename = duplicated_files.add(filepath)

        assert received_filename == expected_filename

    def test_get_returns_existing_filename_by_filepath(self, duplicated_files, fake):
        filepath = fake.file_path(depth=3)
        expected_filename = duplicated_files.add(filepath)

        received_filename = duplicated_files.get(filepath)

        assert received_filename == expected_filename

    def test_get_returns_default_value_if_filename_does_not_exist(self, duplicated_files, fake):
        filepath = fake.file_path(depth=3)
        expected_filename = fake.pystr()

        received_filename = duplicated_files.get(filepath, expected_filename)

        assert received_filename == expected_filename
