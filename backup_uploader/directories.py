import json
import os
import sys
from datetime import datetime
from typing import Optional


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

        self._file_name = f"/var/lib/{app_name}/counters.json"

        try:
            with open(self._file_name) as counters_file:
                try:
                    self._json = json.load(counters_file)
                except json.decoder.JSONDecodeError:
                    print("Counters file with invalid json format", file=sys.stderr)
                    sys.exit(2)
        except FileNotFoundError:
            print("Counters file not found", file=sys.stderr)
            sys.exit(2)
        except PermissionError:
            print("Not read permission on counters file", file=sys.stderr)
            sys.exit(2)

        if not os.access(self._file_name, os.W_OK):
            print("Not write permission on counters file", file=sys.stderr)
            sys.exit(2)

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
            with open(self._file_name, "w") as counters_file:
                json.dump(self._json, counters_file)
