from dataclasses import dataclass
from enum import Enum, auto


"""
All the possible types of tokens in the language.
"""
class TokenType(str, Enum):
    """
    The name of a variable.
    """
    NAME = auto()
    """
    An integer literal.
    """
    INTEGER = auto()

    COMMA = ','
    COLON = ':'
    SEMICOLON = ';'
    ASSIGN = '='
    PARENTHESIS_LEFT = '('
    PARENTHESIS_RIGHT = ')'

    # lists / records
    BRACKET_LEFT = '['
    BRACKET_RIGHT = ']'

    COMMENT = '#'
    LAMBDA = 'λ'

    NL = '\n'
    END = auto()



@dataclass
class Token:
    """
    Represents a token in a token stream.

    A token is a small unit of text that is used to form a program. It may be a keyword,
    identifier, literal, operator, or special character.

    @param type the type of the token
    @param expression the expression that the token represents
    @param line the line number of the token in the source code
    """
    type: TokenType
    expression: str
    line: int

    def __repr__(self) -> str:
        return self.type.name
