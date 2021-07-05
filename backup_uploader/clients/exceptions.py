
class BaseClientException(Exception):
    def __init__(self, message):
        self.message = message
        super(BaseClientException, self).__init__()


class InvalidCredentialsFileFormat(BaseClientException):
    def __init__(self, message):
        super(InvalidCredentialsFileFormat, self).__init__(message)


class UnableToLogin(BaseClientException):
    def __init__(self, message):
        super(UnableToLogin, self).__init__(message)
