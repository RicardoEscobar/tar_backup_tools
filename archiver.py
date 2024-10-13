"""
This module contains the Archiver class, which is responsible for archiving files and directories using tarfile module.
"""

from pathlib import Path
import tarfile
import time
from typing import Callable, Optional, Union


class Archiver:
    """
    This class is responsible for archiving files and directories using tarfile module.
    """

    def __init__(
        self,
        source: Union[str, Path],
        destination: Optional[Union[str, Path]] = None,
        progress_callback: Optional[Callable[[int, int, int, int], None]] = None,
        completed_callback: Optional[Callable[[int, int, float], None]] = None,
    ):
        """
        Initialize the Archiver object with source and destination paths.

        :param source: The path to the file or directory to be archived.
        :type source: str or Path
        :param destination: The path to the archive file. If not provided, the archive file will be created in the same directory as the source file with a .tar extension.
        :type destination: str or Path
        :param progress_callback: A function that takes two arguments (current, total) to report progress.
        :type progress_callback: function
        :param files_added: The number of files added to the archive.
        :type files_added: int
        :param bytes_written: The total number of bytes written to the archive.
        :type bytes_written: int
        :param total_files: The total number of files in the source directory.
        :type total_files: int
        :param total_bytes: The total number of bytes in the source directory.
        :type total_bytes: int
        :param completed_callback: A function that takes two arguments (total, elapsed) to report completion.
        :type completed_callback: function
        :param total_files: The total number of files in the source directory.
        :type total_files: int
        :param total_bytes: The total number of bytes in the source directory.
        :type total_bytes: int
        :param elapsed: The total time taken to complete the archiving process in seconds.
        :type elapsed: float
        """

        # Validate the source and destination paths
        if isinstance(source, str):
            self.source = Path(source).resolve()
        elif isinstance(source, Path):
            self.source = source.resolve()
        else:
            raise TypeError("Source must be a string or Path object.")

        # Check if the source file or directory exists
        if not self.source.exists():
            raise FileNotFoundError(f"File or directory not found: {self.source}")
        elif destination is None:
            self.destination = self.source.with_suffix(".tar")
        else:
            self.destination = Path(destination).resolve()

        # Validate the progress and completed callbacks
        if progress_callback and not callable(progress_callback):
            raise TypeError("Progress callback must be a function.")
        else:
            self.progress_callback = progress_callback

        if completed_callback and not callable(completed_callback):
            raise TypeError("Completed callback must be a function.")
        else:
            self.completed_callback = completed_callback

    def archive(self, progress_callback=None, completed_callback=None):
        """
        Archive the source file or directory to the destination path.


        :param progress_callback: A function that takes two arguments (current, total) to report progress.
        :type progress_callback: function
        :param files_added: The number of files added to the archive.
        :type files_added: int
        :param bytes_written: The total number of bytes written to the archive.
        :type bytes_written: int
        :param total_files: The total number of files in the source directory.
        :type total_files: int
        :param total_bytes: The total number of bytes in the source directory.
        :type total_bytes: int
        :param completed_callback: A function that takes two arguments (total, elapsed) to report completion.
        :type completed_callback: function
        :param total_files: The total number of files in the source directory.
        :type total_files: int
        :param total_bytes: The total number of bytes in the source directory.
        :type total_bytes: int
        :param elapsed: The total time taken to complete the archiving process in seconds.
        :type elapsed: float
        """
        # If progress_callback and completed_callback are provided, use them; otherwise, use the ones provided during initialization
        progress_callback = progress_callback or self.progress_callback
        completed_callback = completed_callback or self.completed_callback

        start = time.time()

        # Determine the total number of files to be archived
        total_files = self.total_files
        total_bytes = self.total_bytes
        files_added = 0
        bytes_written = 0

        with tarfile.open(self.destination, "w") as tar:
            # If source is a directory, add files individually and track progress
            if self.source.is_dir():
                for file in self.source.rglob("*"):
                    tar.add(file, arcname=file.relative_to(self.source.parent))
                    files_added += 1
                    bytes_written += file.stat().st_size
                    # Call the progress callback if provided
                    if progress_callback:
                        progress_callback(files_added, bytes_written, total_files, total_bytes)
            else:
                # If source is a single file, add it directly
                tar.add(self.source, arcname=self.source.name)
                files_added = 1
                # Call the progress callback if provided
                if progress_callback:
                    progress_callback(
                        files_added, bytes_written, total_files, total_bytes
                    )

        end = time.time()

        # Call the completed callback if provided
        if completed_callback:
            completed_callback(total_files, total_bytes, end - start)

    @property
    def total_files(self):
        """
        Return the total number of files in the source directory.
        """
        if self.source.is_dir():
            return sum(1 for _ in self.source.rglob("*"))
        return 1

    @property
    def total_bytes(self):
        """
        Return the total number of bytes in the source directory.
        """
        if self.source.is_dir():
            return sum(file.stat().st_size for file in self.source.rglob("*"))
        return self.source.stat().st_size
