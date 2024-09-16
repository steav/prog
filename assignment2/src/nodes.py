from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


class AbstractNode(ABC):
    def is_leaf(self):
        return False

    @abstractmethod
    def visit(self, visitor: ""):
        pass


@dataclass
class NameNode(AbstractNode):
    name: str

    def is_leaf(self):
        return True

    def __repr__(self) -> str:
        return f"{self.name}"

    def visit(self, visitor: ""):
        return visitor.visit_name(self)


@dataclass
class IntegerNode(AbstractNode):
    value: int

    def is_leaf(self):
        return True

    def __repr__(self) -> str:
        return f"{self.value}"

    def visit(self, visitor: ""):
        return visitor.visit_integer(self)


@dataclass
class AssignNode(AbstractNode):
    left: NameNode
    right: AbstractNode

    def __repr__(self) -> str:
        return f"{self.left} = {self.right}"

    def visit(self, visitor: ""):
        return visitor.visit_assignment(self)


@dataclass
class FunctionNode(AbstractNode):
    left: NameNode
    right: AbstractNode

    def __repr__(self) -> str:
        return f"λ({self.left}): {self.right}"

    def visit(self, visitor: ""):
        return visitor.visit_function(self)


@dataclass
class EnvNode(AbstractNode):
    elements: Dict[str, AbstractNode]

    def __repr__(self) -> str:
        return "[" + ", ".join(map(lambda i: f"{i[0]}={i[1]}", self.elements.items())) + "]"

    def visit(self, visitor: ""):
        return visitor.visit_env(self)


@dataclass
class ApplyNode(AbstractNode):
    left: AbstractNode
    right: AbstractNode

    def __repr__(self) -> str:
        return f"({self.left} {self.right})"

    def visit(self, visitor: ""):
        return visitor.visit_apply(self)