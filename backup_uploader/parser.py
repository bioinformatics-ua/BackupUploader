from datetime import datetime

from backup_uploader.chain import BackupChain

DIRECTORY_STRFTIME_FORMAT = 1
DIRECTORY_NAME = 0
DIRECTORY_CAPACITY = 2
DIRECTORY_COUNTER_MAX = 3


def parse_chain_config_file(config_text, chain: BackupChain):
    used_names = set()
    duplicated_names = set()
    exceptions = []

    config = config_text.split(";")

    if len(config) == 0:
        raise InvalidChainConfig((EmptyConfig(),))

    for position, directory in enumerate(config):
        directory = directory.split(":")

        if len(directory) != 2 and len(directory) != 4:
            raise InvalidFieldCombination(position)

        name = directory[DIRECTORY_NAME]
        if name in used_names:
            duplicated_names.add(name)
            continue

        used_names.add(name)

        strftime_format = directory[DIRECTORY_STRFTIME_FORMAT]
        try:
            datetime.now().strftime(strftime_format)
        except ValueError:
            exceptions.append(InvalidStrftimeFormat(strftime_format, position))

        if len(directory) == 4:
            try:
                capacity = int(directory[DIRECTORY_CAPACITY])
                counter_max = int(directory[DIRECTORY_COUNTER_MAX])
            except ValueError:
                exceptions.append(InvalidIntegerFormat(position))
            else:
                chain.add_directory(
                    strftime_format,
                    name,
                    capacity,
                    counter_max,
                )
        else:
            chain.set_last(strftime_format, name)
            break

    if duplicated_names:
        exceptions.append(DuplicatedDirectoryName(duplicated_names))

    if exceptions:
        raise InvalidChainConfig(exceptions)
    elif position != len(config) - 1:
        raise InvalidChainConfig((DirectoriesAfterLast(position),))


class InvalidChainConfig(Exception):
    def __init__(self, exceptions):
        self.message = '; '.join(ex.message for ex in exceptions)


class EmptyConfig(InvalidChainConfig):
    def __init__(self):
        self.message = "Empty chain config was provided"
        super(InvalidChainConfig, self).__init__()


class MissingMandatoryField(InvalidChainConfig):
    def __init__(self, missing_keys, directory_position):
        self.message = f'Missing mandatory key(s) {", ".join(missing_keys)} on directory in position {directory_position}'
        super(InvalidChainConfig, self).__init__()


class DuplicatedDirectoryName(InvalidChainConfig):
    def __init__(self, duplicated_names):
        self.message = f"The directory name(s) {', '.join(duplicated_names)} are duplicated"
        super(InvalidChainConfig, self).__init__()


class InvalidStrftimeFormat(InvalidChainConfig):
    def __init__(self, format, directory_position):
        self.message = f'Invalid strftime format "{format}" on directory in position {directory_position}'
        super(InvalidChainConfig, self).__init__()


class InvalidIntegerFormat(InvalidChainConfig):
    def __init__(self, directory_position):
        self.message = f'Invalid integers on key(s) {DIRECTORY_CAPACITY} and/or ' \
                       f'{DIRECTORY_COUNTER_MAX} on directory in position {directory_position}'
        super(InvalidChainConfig, self).__init__()


class InvalidFieldCombination(InvalidChainConfig):
    def __init__(self, directory_position):
        self.message = f"Directory on position {directory_position} must have either 2 (last directory) " \
                       f"or 4 (intermediate directory) fields"
        super(InvalidChainConfig, self).__init__()


class DirectoriesAfterLast(InvalidChainConfig):
    def __init__(self, directory_position):
        self.message = f"There are directories defined after a LastDirectory, defined on position {directory_position}"
        super(InvalidChainConfig, self).__init__()
