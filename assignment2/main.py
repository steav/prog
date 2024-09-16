import sys

from src.evaluate import AST, Environment
from src.lexer import Lexer
from src.nodes import AssignNode, IntegerNode
from src.parse import Parser


def execute(code: str) -> int:
    env = Environment()
    statements = Parser(Lexer(code).scan_all()).parse()
    output = 0

    for s in statements:
        if isinstance(s, AssignNode):
            env.define(s.left.name, s.right)
        else:
            result = AST(s, env).reduce()
            if isinstance(result, IntegerNode):
                output = result.value
            else:
                output = result

    return output


def main(argv):
    if len(argv) != 2:
        print("Error: Missing path to program file")
        exit(-1)

    file_path = argv[1]
    with open(file_path, "r") as f:
        code = f.read()

    try:
        print(execute(code))
        exit(0)
    except Exception as e:
        print(e, file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main(sys.argv)