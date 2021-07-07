from typing import Optional

from backup_uploader.clients.base import BaseClient
from backup_uploader.directories import Counters, Directory, LastDirectory


class BackupChain:

    def __init__(self, client: BaseClient, counters: Counters):
        self._directories = []
        self._last = None

        self._client = client
        self._counters = counters

    def add_directory(self, strftime_format: str, name: str, capacity: int, counter_max: int):
        self._directories.append(Directory(strftime_format, name, capacity, counter_max))
        return self

    def set_last(self, strftime_format: str, name: Optional[str] = None):
        self._last = LastDirectory(strftime_format, name)

    def _first(self):
        if self._directories:
            return self._directories[0]
        return self._last

    def empty(self):
        return len(self._directories) == 0

    def store(self, filename):
        self._client.upload_file(filename, self._first())

        for i, directory in enumerate(self._directories):
            if i != 0:
                self._client.move_file(file, directory)

            stored_files = self._client.get_files_in_directory(directory)
            if len(stored_files) <= directory.capacity:
                return

            oldest_file = self._client.get_oldest_file(stored_files)

            if self._counters.inc(directory.name) >= directory.counter_max:
                file = oldest_file
                self._counters.reset(directory.name)
            else:
                self._client.delete_file(oldest_file)
                return

        if self._last is not None:
            if self._directories:
                self._client.move_file(file, self._last)
            # if there is no intermediary directories the file was already written to the last directory
        else:
            self._client.delete_file(file)
