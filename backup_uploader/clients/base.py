from abc import ABC, abstractmethod

from backup_uploader.directories import Directory


class BaseClient(ABC):

    def __init__(self, app_name):
        self._app_name = app_name
        self._root_dir = None

    @abstractmethod
    def login(self, credentials_file):
        pass

    @abstractmethod
    def get_or_create_directory(self, name: str):
        pass

    @abstractmethod
    def get_files_in_directory(self, directory: Directory):
        pass

    @abstractmethod
    def get_oldest_file(self, files):
        pass

    @abstractmethod
    def move_file(self, file, directory: Directory):
        pass

    @abstractmethod
    def upload_file(self, filename: str, directory: Directory):
        pass

    @abstractmethod
    def delete_file(self, file):
        pass

    def __enter__(self):
        self._root_dir = self.get_or_create_directory(self._app_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
