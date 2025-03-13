#!/usr/bin/env python3

# pathwiz/src/file_management/utils.py

import os
from .exceptions import PathNormalizeError


def normalize_path(path: str) -> str:
    """
    Normalize a file path by:
      - Expanding the '~' home directory symbol.
      - Converting to absolute path if not already.
      - Resolving symbolic links via realpath.
      - Ensuring compatibility with Windows UNC paths if possible.

    Args:
        path (str): The path string to normalize.

    Returns:
        str: The fully normalized path.

    Raises:
        PathNormalizeError: If an error occurs during normalization.
    """
    try:
        expanded = os.path.expanduser(path)   # handle '~'
        absolute = os.path.abspath(expanded)  # convert to absolute
        resolved = os.path.realpath(absolute)  # resolve symlinks
        return resolved
    except Exception as e:
        raise PathNormalizeError(f"Error normalizing path '{path}': {e}")
