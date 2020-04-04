class Error(Exception):
    pass


class IllegalCharacterError(Error):
    """
    Raised when lexer finds a illegal character
    """
    pass


class UnterminatedStringError(Error):
    """
    Raised when lexer finds a string with " or ' not closed
    """
    pass


class UnterminatedCommentError(Error):
    """
    Raised when lexer finds a comment block not closed
    """
    pass


class LexerError(Error):
    """
    Raised when something went wrong with the lexer, mainly for testing purposes
    """
    pass