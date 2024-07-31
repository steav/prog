from .nodes import *
from .token import TokenType


class Parser:
    def __init__(self, tokens):
        self.cur = 0
        self.tokens = tokens

    def parse(self):
        statements = []
        while not self.is_end():
            statements.append(self.statement())
        return statements

    def prev(self):
        if self.cur > 0:
            return self.tokens[self.cur - 1]
        return self.tokens[0]

    def next(self):
        if not self.is_end():
            self.cur += 1
        return self.prev()

    def seek(self, offset=0):
        return self.tokens[self.cur + offset]

    def match(self, *types):
        if self.is_end():
            return False
        for token_type in types:
            if token_type == self.seek().type:
                return True
        return False

    def is_end(self):
        return self.seek().type == TokenType.END

    def consume(self, *types):
        for t in types:
            if self.match(t):
                self.next()
                return True
        return False

    def statement(self):
        if self.seek().type == TokenType.NAME and self.seek(1).type == TokenType.ASSIGN:
            name = self.create_named()
            if not self.consume(TokenType.ASSIGN):
                raise Exception(f"Missing = after name: {name}")
            expr = AssignNode(name, self.expression())
        else:
            expr = self.expression()

        if not self.consume(TokenType.SEMICOLON) and not self.is_end():
            token = self.seek()
            raise Exception(f"Missing ; at '{token.expression}', line {token.line}")

        return expr

    def expression(self):
        elements = []
        endings = [TokenType.PARENTHESIS_RIGHT, TokenType.BRACKET_RIGHT, TokenType.COMMA, TokenType.SEMICOLON]

        while not (self.match(*endings) or self.is_end()):
            if self.match(TokenType.INTEGER):
                expr = self.create_integer()
            elif self.match(TokenType.NAME):
                expr = self.create_named()
            elif self.consume(TokenType.PARENTHESIS_LEFT):
                expr = self.expression()
                if not self.consume(TokenType.PARENTHESIS_RIGHT):
                    raise Exception(f"Missing ) at end of expression: {expr}")
            elif self.match(TokenType.LAMBDA):
                expr = self.create_func()
            elif self.match(TokenType.BRACKET_LEFT):
                expr = self.create_record()
            else:
                token = self.next()
                raise Exception(f"Unknown token: {token.expression}")

            elements.append(expr)

        if len(elements) <= 0:
            raise Exception("Unexpected expression")

        result = elements.pop(0)
        for e in elements:
            result = ApplyNode(result, e)

        return result

    def create_named(self):
        name = self.next()
        return NameNode(name.expression)

    def create_integer(self):
        value = self.next()
        return IntegerNode(int(value.expression))

    def create_record(self):
        if not self.consume(TokenType.BRACKET_LEFT):
            raise Exception("Missing [ at start of record list")
        entries = dict()
        while not self.is_end() and (
                self.consume(TokenType.COMMA) or not self.match(TokenType.BRACKET_RIGHT)):
            name = self.create_named()
            if not self.consume(TokenType.ASSIGN):
                raise Exception("Missing = in record assignment")
            entries[name.name] = self.expression()

        if not self.consume(TokenType.BRACKET_RIGHT):
            raise Exception("Missing ] at end of record list")

        node = EnvNode(entries)

        endings = [TokenType.SEMICOLON, TokenType.PARENTHESIS_RIGHT, TokenType.BRACKET_RIGHT, TokenType.COMMA,
                   TokenType.BRACKET_LEFT]
        if self.is_end() or self.match(*endings):
            return node

        return ApplyNode(node, self.expression())

    def create_func(self):
        if not self.consume(TokenType.LAMBDA):
            raise Exception("Expected lamda symbol at function begin")

        if not self.consume(TokenType.PARENTHESIS_LEFT):
            raise Exception("Missing { after lamda symbol")

        params = [self.create_named()]
        while self.consume(TokenType.COMMA) and not self.is_end():
            params.append(self.create_named())

        if not self.consume(TokenType.PARENTHESIS_RIGHT):
            raise Exception("Missing } after lamda param list")

        if not self.consume(TokenType.COLON):
            raise Exception("Missing : after lambda param list")

        node = self.expression()
        while len(params) > 0:
            node = FunctionNode(params.pop(), node)
        return node
