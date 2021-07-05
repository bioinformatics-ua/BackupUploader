
class BaseClientException(Exception):
    pass


class InvalidCredentialsFileFormat(BaseClientException):
    pass


class UnableToLogin(BaseClientException):
    pass
