import sys
from importlib.resources import files
from typing import IO

if sys.version_info < (3, 12):
    # This was deprecated in Python 3.12.
    from importlib.abc import Traversable
else:
    from importlib.resources.abc import Traversable


def resource_root() -> Traversable:
    """
    Return the root directory as a traversable that can
    be used to load the `extensions`, `*.csv` and `encoding.h`
    files. For historical reasons these are not stored inside
    the `src/riscv_opcodes` directory in the source distribution
    but they are moved there when generating the binary wheel.
    This means we need to check in both places.
    """
    assert __package__ is not None
    package_root = files(__package__)
    if (package_root / "extensions").is_dir():
        return package_root
    return package_root / ".." / ".."


def read_text_resource(path_relative_to_root: str) -> str:
    """
    Read a text file relative to the root of this repo.
    """
    return resource_root().joinpath(path_relative_to_root).read_text(encoding="utf-8")


def open_text_resource(path_relative_to_root: str) -> IO[str]:
    """
    Open a text file relative to the root of this repo.
    """
    return resource_root().joinpath(path_relative_to_root).open("r", encoding="utf-8")
