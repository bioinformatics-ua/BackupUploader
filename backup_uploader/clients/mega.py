import sys

import mega
import mega.errors

from backup_uploader.clients.base import BaseClient
from backup_uploader.clients import exceptions
from backup_uploader.directories import Directory


class MegaClient(BaseClient):

    def __init__(self, app_name):
        super(MegaClient, self).__init__(app_name)
        self._client = mega.Mega()

    def login(self, credentials_file):
        try:
            email = credentials_file.readline().strip()
            password = credentials_file.readline().strip()
        except IOError:
            raise exceptions.InvalidCredentialsFileFormat()

        try:
            self._client.login(email, password)
        except mega.errors.RequestError as err:
            raise exceptions.UnableToLogin(err)

    def get_or_create_directory(self, name: str):
        if self._root_dir is not None:
            name = f"{self._app_name}/{name}"

        directory = self._client.find(name, exclude_deleted=True)
        if not directory:
            return self._client.create_folder(name, dest=self._root_dir)

        if directory[1]["t"] != 1:  # if its not a directory
            print(
                f"Node on the {name} directory provided is not a directory.",
                file=sys.stderr,
            )
            sys.exit(3)

        return directory[0]

    def get_files_in_directory(self, directory: Directory):
        if not hasattr(directory, "id"):
            return self.get_or_create_directory(directory.name)

        return self._client.get_files_in_node(directory.id)

    def get_oldest_file(self, files):
        return sorted(files.items(), key=lambda f: f[1]["ts"])[0]

    def move_file(self, file, directory: Directory):
        if not hasattr(directory, "id"):
            directory.id = self.get_or_create_directory(directory.name)

            if isinstance(directory.id, dict):
                directory.id = directory.id[directory.name]

        self._client.move(file, directory.id)
        self._client.rename(file, directory.generate_name())

    def upload_file(self, filename, directory: Directory):
        dest = self.get_or_create_directory(directory.name)
        directory.id = dest

        file = self._client.upload(filename, dest, directory.generate_name())["f"][0]["h"]
        file = self._client.find(handle=file)
        self._client.rename((None, file), directory.generate_name())

    def delete_file(self, file):
        self._client.destroy(file[1])
