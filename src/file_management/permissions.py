#!/usr/bin/env python3

# pathwiz/src/file_management/permissions.py

import os
from pathlib import Path
import logging
from typing import Union

import asyncio


from .utils import normalize_path


class PermissionsManager:
    """
    Manages file and directory permissions.
    """

    def __init__(self, root_path: Union[str, Path]):
        """
        Initialize the PermissionsManager.

        Args:
            root_path (Union[str, Path]): The root path.
        """
        self._root_path = Path(normalize_path(root_path))
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    async def check_permissions(self, directory_path: Union[str, Path], request_permissions: int, resolve: bool = False):
        """
        Check and correct permissions in the given directory path asynchronously.

        Args:
            directory_path (Union[str, Path]): The directory path.
            request_permissions (int): The required permissions in octal notation (e.g. 0o755).
            resolve (bool): If True, follow symbolic links.

        Raises:
            PermissionError: If permission changes fail.
        """
        full_path = self._root_path / directory_path
        if not full_path.exists():
            return

        async def check_and_correct(path):
            try:
                stat_info = await asyncio.to_thread(os.stat, path, follow_symlinks=resolve)
                current_permissions = stat_info.st_mode & 0o777
                if current_permissions != request_permissions:
                    await asyncio.to_thread(os.chmod, path, request_permissions)
                    logging.info(
                        f"Permissions corrected: '{path}': {oct(current_permissions)} -> {oct(request_permissions)}")
            except OSError as e:
                raise PermissionError(f"Permission error: '{path}': {e}")

        async def traverse(path):
            try:
                await check_and_correct(path)
                child_dirs = [os.path.join(path, child) for child in os.listdir(
                    path) if os.path.isdir(os.path.join(path, child))]
                for child_dir in child_dirs:
                    await traverse(child_dir)
            except OSError as e:
                raise PermissionError(f"Traversal error: '{path}': {e}")

        await traverse(str(full_path))

    def get_file_permissions(self, file_path: Union[str, Path]) -> int:
        """
        Return the numeric permission bits for a given file (e.g. 0o755 -> 493 decimal).

        Args:
            file_path (Union[str, Path]): The file path.

        Returns:
            int: The numeric permission bits (base-10 integer).
        """
        full_path = self._root_path / file_path
        if not full_path.exists():
            # Use built-in FileNotFoundError
            raise FileNotFoundError(f"File not found: {full_path}")
        stat_info = full_path.stat()
        return stat_info.st_mode & 0o777

    @classmethod
    def permissions_to_rwx(cls, octal_permissions: int) -> str:
        """
        Convert octal-based permissions (e.g. 0o755) to 'rwxr-xr-x'.

        Note:
            The input integer is in base 10 but typically denotes an octal literal (e.g. 0o755 == 493 decimal).

        Args:
            octal_permissions (int): The permission bits in base 10 (e.g. 493).

        Returns:
            str: A string representing the rwx pattern (e.g. 'rwxr-xr-x').
        """
        result = ""
        for shift in (6, 3, 0):
            digit = (octal_permissions >> shift) & 0o7
            result += cls.octal_digit_to_rwx(digit)
        return result

    @classmethod
    def octal_digit_to_rwx(cls, octal_digit: int) -> str:
        """
        Convert a single octal digit (0-7) into an rwx string.

        For instance, 7 -> 'rwx', 6 -> 'rw-', 4 -> 'r--', etc.

        Args:
            octal_digit (int): A single digit from 0 to 7.

        Returns:
            str: The corresponding rwx string.
        """
        r = "r" if octal_digit & 0b100 else "-"
        w = "w" if octal_digit & 0b010 else "-"
        x = "x" if octal_digit & 0b001 else "-"
        return r + w + x
