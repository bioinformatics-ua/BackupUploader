import json
import os
import sys
from datetime import datetime
from typing import Optional

import click


class Directory:
    client = None
    upload_folder = None
    counters = None

    def __init__(  # noqa
            self,
            strftime_format: str,
            name: Optional[str],
            capacity: Optional[int],
            counter_max: Optional[int],
    ):
        self._strftime_format = strftime_format
        self.name = name
        self.capacity = capacity
        self.counter_max = counter_max

    def generate_name(self):
        return datetime.now().strftime(self._strftime_format)


class LastDirectory(Directory):
    def __init__(self, strftime_format: str, name: Optional[str] = None):
        super().__init__(strftime_format, name, None, None)


class Counters:

    def __init__(self, app_name):
        self.updates = False

        self._file_name = f"/var/lib/backup_uploader/{app_name}.json"

        try:
            with open(self._file_name) as counters_file:
                try:
                    self._json = json.load(counters_file)
                except json.decoder.JSONDecodeError:
                    click.echo(f'Counters file "{self._file_name}" with invalid json format', err=True)
                    sys.exit(2)
        except FileNotFoundError:
            self._json = {}
            self.updates = True
        except PermissionError:
            click.echo(f'Unable to read on counters file "{self._file_name}"', err=True)
            sys.exit(2)

        old_mask = os.umask(0o002)
        try:
            with open(self._file_name, "a+"):  # test if I can write/create the file to later save
                pass
        except FileNotFoundError:
            click.echo(
                "The directory /var/lib/backup_uploader does not exist.\n"
                'Run sudo sh -c "useradd backup_uploader && '
                'mkdir /var/lib/backup_uploader && '
                'chown backup_uploader:backup_uploader /var/lib/backup_uploader" '
                'to create it and the respective backup_uploader user and group.'
            )
        except PermissionError:
            click.echo(
                f'Unable to create/write on counters file "{self._file_name}".\n'
                'The user running this script should belong to the "backup_uploader" group.',
                err=True,
            )
            sys.exit(2)
        finally:
            os.umask(old_mask)

    def inc(self, name):
        if name not in self._json:
            self._json[name] = 0
        self._json[name] += 1
        self.updates = True
        return self._json[name]

    def reset(self, name):
        self._json[name] = 0
        self.updates = True

    def get(self, name):
        return self._json[name]

    def save(self):
        if self.updates:
            old_mask = os.umask(0o002)
            try:
                with open(self._file_name, "w+") as counters_file:
                    json.dump(self._json, counters_file)
            finally:
                os.umask(old_mask)
