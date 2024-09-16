import re

from .token import Token, TokenType


def is_char(input):
    return re.search("[_a-zA-Z0-9]", input)

def is_digit(input):
    return re.search("[0-9]", input)

def is_whitespace(input):
    """
    Checks if the given input is whitespace.

    @param input the input to check
    @return True if the input is whitespace, False otherwise
    """
    return re.search("[\\s+]", input)


class Lexer:
    def __init__(self, program):
        self.program = program
        self.tokens = []

        self.begin = 0
        self.cur = 0
        self.line = 1

    def scan_all(self):
        while not self.is_end():
            self.begin = self.cur
            self.scan_next()
        self.tokens.append(Token(TokenType.END, "", self.line))
        return self.tokens

    def next(self):
        res = self.program[self.cur]
        self.cur += 1
        return res

    def seek(self):
        return "" if self.is_end() else self.program[self.cur]

    def is_end(self):
        return self.cur >= len(self.program)

    def add_token(self, type):
        token = self.program[self.begin:self.cur]
        self.tokens.append(Token(type, token, self.line))

    def scan_next(self):
        char = self.next()
        if char == TokenType.ASSIGN:
            self.add_token(TokenType.ASSIGN)
        elif char == TokenType.COLON:
            self.add_token(TokenType.COLON)
        elif char == TokenType.COMMA:
            self.add_token(TokenType.COMMA)
        elif char == TokenType.SEMICOLON:
            self.add_token(TokenType.SEMICOLON)
        elif char == TokenType.PARENTHESIS_LEFT:
            self.add_token(TokenType.PARENTHESIS_LEFT)
        elif char == TokenType.PARENTHESIS_RIGHT:
            self.add_token(TokenType.PARENTHESIS_RIGHT)
        elif char == TokenType.BRACKET_LEFT:
            self.add_token(TokenType.BRACKET_LEFT)
        elif char == TokenType.BRACKET_RIGHT:
            self.add_token(TokenType.BRACKET_RIGHT)
        elif char == TokenType.LAMBDA:
            self.add_token(TokenType.LAMBDA)
        elif char == TokenType.COMMENT:
            while self.seek() not in [TokenType.END, TokenType.NL]:
                self.next()
        elif char == TokenType.NL:
                self.line += 1
                return
        elif is_whitespace(char):
            # Ignore
            return
        elif is_digit(char):
            while is_digit(self.seek()) and not self.is_end():
                self.next()
            self.add_token(TokenType.INTEGER)
        elif is_char(char):
            while is_char(self.seek()) and not self.is_end():
                self.next()
            self.add_token(TokenType.NAME)
        else:
            raise Exception(f"Unknown token '{char}' at line {self.line}, character {self.cur}: {self.line}")