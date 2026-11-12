class AppError(Exception):
    """A safe, user-facing application error."""


class NetworkUnavailable(AppError):
    pass


class JobNotFound(AppError):
    pass


class DCLNotFound(AppError):
    pass


class CustomerNotFound(AppError):
    pass


class ArchiveError(AppError):
    pass

