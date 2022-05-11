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
