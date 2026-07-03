class TokenError(Exception):
    pass


class TokenNotFound(TokenError):
    pass


class TokenExpired(TokenError):
    pass
