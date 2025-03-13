#!/usr/bin/env python3
# pathwiz/src/file_management/manager.py

from pathlib import Path
from typing import Dict, Optional, Tuple, List, Union
from .filesystem import FilesystemManager
from .structure import generate_directory_tree
from .permissions import PermissionsManager
# Built-in:
# from .exceptions import FileSystemError, DirectoryNotFoundError  # if needed


class FileManagementFacade:
    """
    Provides a unified interface to the functionalities offered by:
    - FilesystemManager (for file/folder operations)
    - PermissionsManager (for permission handling)
    - structure.py (to generate a directory tree)

    This facade simplifies usage by exposing common operations as high-level methods.
    """

    def __init__(self, root_path: Union[str, Path]):
        """
        Initialize the FileManagementFacade.

        Args:
            root_path (Union[str, Path]): The root path where operations will be performed.
        """
        self._root_path = Path(root_path)
        self._fs_manager = FilesystemManager(root_path)
        self._perm_manager = PermissionsManager(root_path)

    async def create_folder(
        self,
        directory_name: Union[str, Path],
        overwrite: bool = False,
        permissions: int = 0o755,
        subfolders: Optional[Union[dict, list]] = None,
    ) -> None:
        """
        Delegates folder creation to FilesystemManager.

        Args:
            directory_name (Union[str, Path]): The folder name to create.
            overwrite (bool): If True, existing folder will be overwritten.
            permissions (int): The folder permissions in octal form (e.g. 0o755).
            subfolders (dict or list, optional): Subfolders to be created.

        Returns:
            None
        """
        await self._fs_manager.create_folder(
            directory_name, overwrite, permissions, subfolders
        )

    async def create_file(self, file_path: Union[str, Path], sub_folder: Optional[Union[str, Path]] = None) -> None:
        """
        Delegates file creation to FilesystemManager.

        Args:
            file_path (Union[str, Path]): The file path to create.
            sub_folder (Union[str, Path], optional): A subfolder under the root path.

        Returns:
            None
        """
        await self._fs_manager.create_file(file_path, sub_folder)

    def get_file_list(
        self,
        directory: Union[str, Path],
        extension: Optional[str] = None,
        recursive: bool = False
    ) -> List[Path]:
        """
        Delegates the retrieval of files to FilesystemManager.

        Args:
            directory (Union[str, Path]): The directory to scan.
            extension (str, optional): Filter by file extension (e.g. 'txt').
            recursive (bool): If True, search subdirectories recursively.

        Returns:
            List[Path]: A list of file paths.
        """
        return self._fs_manager.get_file_list(
            directory, extension, recursive
        )

    def get_file_permissions(self, file_path: Union[str, Path]) -> int:
        """
        Delegates permission retrieval to PermissionsManager.

        Args:
            file_path (Union[str, Path]): The target file path.

        Returns:
            int: The numeric permission bits (e.g. 493 for 0o755).
        """
        return self._perm_manager.get_file_permissions(file_path)

    async def check_permissions(self, directory_path: Union[str, Path], request_permissions: int, resolve: bool = False) -> None:
        """
        Delegates permission checking/correction to PermissionsManager.

        Args:
            directory_path (Union[str, Path]): Path to the directory.
            request_permissions (int): Required permissions in octal notation.
            resolve (bool): Follow symbolic links if True.

        Returns:
            None
        """
        await self._perm_manager.check_permissions(directory_path, request_permissions, resolve)

    def generate_directory_tree(
        self,
        directory: str,
        excluded_directories: Optional[List[str]] = None,
        exclude_hidden: bool = True,
        output_format: str = "both",
        formatter=None
    ) -> Tuple[Optional[str], Optional[Dict[str, Dict[str, str]]]]:
        """
        Delegates directory tree generation to `generate_directory_tree`.

        Args:
            directory (str): The root directory path.
            excluded_directories (List[str], optional): Directories to exclude.
            exclude_hidden (bool): If True, hidden directories are excluded.
            output_format (str): 'both', 'markdown', or 'dict'.
            formatter (callable, optional): A function to format the markdown output.

        Returns:
            Tuple[Optional[str], Optional[Dict[str, Dict[str, str]]]]:
                (markdown_string, dict_representation)
        """
        return generate_directory_tree(
            directory,
            excluded_directories,
            exclude_hidden,
            output_format,
            formatter
        )
