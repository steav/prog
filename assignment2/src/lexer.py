import re

from .token import Token, TokenType


def is_char(input):
    """
    Checks if the given input is a character.

    @param input the input to check
    @return True if the input is a character, False otherwise
    """
    return re.search("[_a-zA-Z0-9]", input)

def is_digit(input):
    """
    Checks if the given input is a digit.

    @param input the input to check
    @return True if the input is a digit, False otherwise
    """
    return re.search("[0-9]", input)

def is_whitespace(input):
    """
    Checks if the given input is whitespace.

    @param input the input to check
    @return True if the input is whitespace, False otherwise
    """
    return re.search("[\\s+]", input)


class Lexer:
    """
    A class that lexes a given program and returns an array of tokens.
    """

    def __init__(self, program):
        """
        Initializes the lexer.

        @param program the program to lex
        """
        self.program = program
        self.tokens = []

        self.begin = 0
        self.cur = 0
        self.line = 1


    def scan_all(self):
        """
        Scans the given program and returns an array of tokens.

        @return an array of tokens
        """
        while not self.is_end():
            self.begin = self.cur
            self.scan_next()
        self.tokens.append(Token(TokenType.END, "", self.line))
        return self.tokens

    def next(self):
        """
        Returns the next char in the program.

        @return the next char in the program
        """
        res = self.program[self.cur]
        self.cur += 1
        return res

    def seek(self):
        """
        Returns the current char in the program.

        @return the current char in the program
        """
        return "" if self.is_end() else self.program[self.cur]

    def is_end(self):
        """
        Checks if the end of the program has been reached.

        @return true if the end of the program has been reached, false otherwise
        """
        return self.cur >= len(self.program)

    def add_token(self, type):
        """
        Adds a token to the array of tokens.

        @param type the type of the token
        """
        token = self.program[self.begin:self.cur]
        self.tokens.append(Token(type, token, self.line))

    def scan_next(self):
        """
        Scans the next token in the program.
        """
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