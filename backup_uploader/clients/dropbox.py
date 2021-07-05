from backup_uploader.clients.base import BaseClient
from backup_uploader.clients.exceptions import UnableToLogin
from backup_uploader.directories import Directory

import dropbox
import dropbox.exceptions
import dropbox.files


class DropboxClient(BaseClient):

    CHUNKS_SIZES = 1 * 1024 * 1024  # 5 MB

    def __init__(self, app_name):
        super(DropboxClient, self).__init__(app_name)
        # self._client = dropbox.Dropbox()

    def login(self, credentials_file):
        self._client = dropbox.Dropbox(credentials_file.readline().strip())
        self._client.__enter__()

        # Check that the access token is valid
        try:
            self._client.users_get_current_account()
        except dropbox.exceptions.AuthError:
            raise UnableToLogin(
                "ERROR: Invalid access token; try re-generating an "
                "access token from the app console on the web."
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.__exit__()

    def get_or_create_directory(self, name: str):
        if self._root_dir is not None:
            name = f"/{self._app_name}/{name}"
        else:
            name = f"/{name}"

        try:
            self._client.files_create_folder_v2(name)
        except dropbox.exceptions.ApiError:
            pass

        return name

    def get_files_in_directory(self, directory: Directory):
        name = self.get_or_create_directory(directory.name)

        return self._client.files_list_folder(name).entries

    def get_oldest_file(self, files):
        files.sort(key=lambda f: f.client_modified)
        return files[0]

    def move_file(self, file, directory: Directory):
        dir_name = self.get_or_create_directory(directory.name)

        self._client.files_move_v2(
            file.path_display,
            f"{dir_name}/{directory.generate_name()}",
            autorename=True,
        )

    def upload_file(self, filename: str, directory: Directory):
        dir_name = self.get_or_create_directory(directory.name)

        with open(filename, "rb") as file:
            data = file.read(self.CHUNKS_SIZES)
            upload_session_result = self._client.files_upload_session_start(data)
            offset = len(data)

            while True:
                data = file.read(self.CHUNKS_SIZES)

                if not data:
                    break

                self._client.files_upload_session_append_v2(
                    data,
                    dropbox.files.UploadSessionCursor(
                        upload_session_result.session_id,
                        offset,
                    ),
                )

        self._client.files_upload_session_finish(
            b"",
            dropbox.files.UploadSessionCursor(
                upload_session_result.session_id,
                offset,
            ),
            dropbox.files.CommitInfo(
                f"{dir_name}/{directory.generate_name()}",
                autorename=True,
            )
        )

    def delete_file(self, file):
        self._client.files_delete_v2(file.path_display)
