#!/usr/bin/env python3
# pathwiz/src/file_management/structure.py

from pathlib import Path
from typing import Dict, Optional, Tuple, List, Callable


def generate_directory_tree(
    directory: str,
    excluded_directories: Optional[List[str]] = None,
    exclude_hidden: bool = True,
    output_format: str = "both",
    formatter: Optional[Callable[[str], str]] = None,
) -> Tuple[Optional[str], Optional[Dict[str, Dict[str, str]]]]:
    """
    Generate a tree structure for a given directory.

    Args:
        directory (str): The root directory path.
        excluded_directories (List[str], optional): A list of directory names to exclude.
        exclude_hidden (bool): Whether to exclude hidden directories (defaults to True).
        output_format (str): "both", "markdown", or "dict" (defaults to "both").
        formatter (callable, optional): A function that takes a markdown string and
            returns a modified string (useful for fancy rendering in Jupyter or elsewhere).

    Returns:
        Tuple[Optional[str], Optional[Dict[str, Dict[str, str]]]]:
            - A Markdown string (or None if not requested)
            - A dictionary representation of the directory structure (or None if not requested)
    """
    if excluded_directories is None:
        excluded_directories = [".venv", "__pycache__", "tests"]

    project_root = Path(directory)
    markdown_output = None
    dict_output: Dict[str, Dict[str, str]] = {}

    # Generate Markdown
    if output_format in ("markdown", "both"):
        markdown_lines = [
            f"# Project Structure: {project_root.name}",
            "```",
            f"{project_root.name}/"
        ]

        def _generate_markdown_tree(path: Path, prefix: str = "", is_last: bool = True):
            connector = "└── " if is_last else "├── "
            current_prefix = prefix + connector
            next_prefix = prefix + ("    " if is_last else "│   ")
            markdown_lines.append(f"{current_prefix}{path.name}/")

            items = [
                item
                for item in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                if not (item.is_dir() and (item.name in excluded_directories or (exclude_hidden and item.name.startswith("."))))
            ]

            for i, item in enumerate(items):
                is_last_item = (i == len(items) - 1)
                if item.is_dir():
                    _generate_markdown_tree(item, next_prefix, is_last_item)
                elif item.suffix == ".py":
                    item_connector = "└── " if is_last_item else "├── "
                    markdown_lines.append(
                        f"{next_prefix}{item_connector}{item.name}")

        items = [
            item
            for item in sorted(project_root.iterdir(), key=lambda x: (x.is_file(), x.name))
            if not (item.is_dir() and (item.name in excluded_directories or (exclude_hidden and item.name.startswith("."))))
        ]

        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            if item.is_dir():
                _generate_markdown_tree(item, "", is_last)
            elif item.suffix == ".py":
                connector = "└── " if is_last else "├── "
                markdown_lines.append(f"{connector}{item.name}")

        markdown_lines.append("```")
        result_str = "\n".join(markdown_lines)

        # Apply external formatter if provided (e.g. for Jupyter-friendly rendering)
        markdown_output = formatter(result_str) if formatter else result_str

    # Generate dict structure
    if output_format in ("dict", "both"):
        def _build_dict_structure(path: Path, current_dict: Dict[str, Dict[str, str]], module_prefix: str = ""):
            for item in sorted(path.iterdir()):
                if item.name in excluded_directories or (exclude_hidden and item.name.startswith(".")):
                    continue

                if item.is_dir():
                    if (item / "__init__.py").exists():
                        package_name = item.name
                        package_path = f"{module_prefix}{package_name}." if module_prefix else f"{package_name}."
                        current_dict[package_name] = {}
                        _build_dict_structure(
                            item, current_dict[package_name], package_path)
                    else:
                        _build_dict_structure(
                            item, current_dict, module_prefix + item.name + ".")
                elif item.suffix == ".py":
                    module_name = item.stem
                    module_path = f"{module_prefix}{module_name}"
                    current_dict[module_name] = module_path

        if (project_root / "__init__.py").exists():
            package_name = project_root.name
            dict_output[package_name] = {}
            _build_dict_structure(
                project_root, dict_output[package_name], f"{package_name}.")
        else:
            _build_dict_structure(project_root, dict_output)

    return markdown_output, dict_output
