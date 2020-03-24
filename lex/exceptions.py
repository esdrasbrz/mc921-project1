class Error(Exception):
    pass


class IllegalCharacterError(Error):
    """
    Raised when lexer finds a illegal character
    """
    pass
