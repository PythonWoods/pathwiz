#!/usr/bin/env python3

# pathwiz/src/file_management/filesystem.py

import asyncio
import os
import shutil
from pathlib import Path
from typing import List, Optional, Union
import logging

import aiofiles
from .exceptions import DirectoryNotFoundError, FileSystemError
from .utils import normalize_path


class FilesystemManager:
    """
    Manages basic filesystem operations (creation, removal, listing of files and folders).
    """

    def __init__(self, root_path: Union[str, Path]):
        """
        Initialize the FilesystemManager.

        Args:
            root_path (Union[str, Path]): The root path for all operations.
        """
        self._root_path = Path(normalize_path(root_path))
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    @property
    def root_path(self) -> Path:
        """
        Returns the root path.
        """
        return self._root_path

    async def create_folder(
        self,
        directory_name: Union[str, Path],
        overwrite: bool = False,
        permissions: int = 0o755,
        subfolders: Optional[Union[dict, list]] = None,
    ) -> None:
        """
        Asynchronously create a folder with optional overwrite and permissions.
        """
        full_path = self._root_path / directory_name
        try:
            if overwrite and full_path.exists():
                if full_path.is_dir():
                    # There's no direct aiofiles.os.rmtree(), so we might do:
                    await asyncio.to_thread(shutil.rmtree, full_path)
                    logging.info(f"Removed existing directory: {full_path}")
                else:
                    raise FileSystemError(
                        f"Cannot overwrite file: {full_path}")

            # There's no direct mkdir in aiofiles.os (as of writing),
            # so we do an asyncio.to_thread if needed:
            await asyncio.to_thread(full_path.mkdir, mode=permissions, parents=True, exist_ok=True)
            logging.info(f"Created directory: {full_path}")

            if subfolders:
                if isinstance(subfolders, dict):
                    for subfolder_name, subfolder_structure in subfolders.items():
                        await self.create_folder(
                            full_path / subfolder_name,
                            overwrite=overwrite,
                            permissions=permissions,
                            subfolders=subfolder_structure
                        )
                elif isinstance(subfolders, list):
                    for subfolder_name in subfolders:
                        await self.create_folder(
                            full_path / subfolder_name,
                            overwrite=overwrite,
                            permissions=permissions,
                        )

        except FileSystemError as e:
            logging.error(f"Error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    async def create_file(self, file_path: Union[str, Path], sub_folder: Optional[Union[str, Path]] = None) -> None:
        """
        Asynchronously create an empty file.
        """
        if sub_folder:
            full_path = self._root_path / sub_folder / file_path
        else:
            full_path = self._root_path / file_path

        try:
            # Make sure the parent directory exists (using asyncio.to_thread for non-blocking I/O)
            await asyncio.to_thread(os.makedirs, full_path.parent, exist_ok=True)

            # Actually create the file with aiofiles
            async with aiofiles.open(full_path, 'w') as f:
                await f.write("")  # create an empty file

            logging.info(f"Created file: {full_path}")
        except Exception as e:
            logging.error(f"Error creating file: {e}")
            raise

    def get_file_list(
        self,
        directory: Union[str, Path],
        extension: Optional[str] = None,
        recursive: bool = False
    ) -> List[Path]:
        """
        Returns a list of file paths in the given directory.

        Args:
            directory (Union[str, Path]): The directory to scan.
            extension (str, optional): Filter by file extension (e.g. "txt").
            recursive (bool): If True, searches subdirectories recursively.

        Raises:
            DirectoryNotFoundError: If the directory does not exist.

        Returns:
            List[Path]: A list of Path objects representing each file.
        """
        full_path = self._root_path / directory
        if not full_path.exists() or not full_path.is_dir():
            raise DirectoryNotFoundError(f"Directory not found: {full_path}")

        file_list: List[Path] = []
        if recursive:
            for file_path in full_path.rglob("*"):
                if file_path.is_file():
                    if extension is None or file_path.suffix == f".{extension}":
                        file_list.append(file_path)
        else:
            for file_path in full_path.iterdir():
                if file_path.is_file():
                    if extension is None or file_path.suffix == f".{extension}":
                        file_list.append(file_path)

        return file_list
