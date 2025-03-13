#!/usr/bin/env python3

# pathwiz/src/file_management/exceptions.py

"""Modulo di eccezioni per la gestione del filesystem."""


class FileSystemError(Exception):
    """Eccezione base per errori del filesystem."""

    pass


class DirectoryNotFoundError(FileSystemError):
    """Eccezione per directory non trovata."""

    pass


class PathNormalizeError(FileSystemError):
    """Eccezione per errori di normalizzazione dei path."""

    pass
