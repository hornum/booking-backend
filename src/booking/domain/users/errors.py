class UserError(Exception):
    pass


class InvalidUserEmail(UserError):
    pass


class UserAlreadyExists(UserError):
    pass


class UserNotFound(UserError):
    pass


class UserBanned(UserError):
    pass


class IncorrectPassword(UserError):
    pass
