from dataclasses import dataclass
from enum import Enum, auto


class TokenType(str, Enum):
    NAME = auto()
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
    type: TokenType
    expression: str
    line: int

    def __repr__(self) -> str:
        return self.type.name
