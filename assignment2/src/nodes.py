from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


"""
Abstract base class for all nodes in an abstract syntax tree (AST).

Contains methods is_leaf() and visit(visitor).
"""
class AbstractNode(ABC):
    """
    Checks if this node is a leaf node.

    @return True if this node is a leaf node, False otherwise
    """
    def is_leaf(self):
        return False

    """
    Applies a visitor to this node.

    @param visitor the visitor to apply
    @return the result of applying the visitor
    """
    @abstractmethod
    def visit(self, visitor: ""):
        pass


@dataclass
class NameNode(AbstractNode):
    """
    Represents a node in an abstract syntax tree (AST) that contains a name.

    @param name the name of the node
    """
    name: str

    def is_leaf(self):
        return True

    def __repr__(self) -> str:
        return f"{self.name}"

    def visit(self, visitor: ""):
        """
        Applies a visitor to this node.

        @param visitor the visitor to apply
        @return the result of applying the visitor
        """
        return visitor.visit_name(self)

@dataclass
class IntegerNode(AbstractNode):
    """
    Represents a node in an abstract syntax tree (AST) that contains an integer value.

    @param value the value of the node
    """
    value: int

    def is_leaf(self):
        return True

    def __repr__(self) -> str:
        return f"{self.value}"

    def visit(self, visitor: ""):
        return visitor.visit_integer(self)


@dataclass
class AssignNode(AbstractNode):
    """
    Represents a node in an abstract syntax tree (AST) that contains an assignment.

    @param left the left side of the assignment
    @param right the right side of the assignment
    """
    left: NameNode
    right: AbstractNode

    def __repr__(self) -> str:
        return f"{self.left} = {self.right}"

    def visit(self, visitor: ""):
        return visitor.visit_assignment(self)


@dataclass
class FunctionNode(AbstractNode):
    """
    Represents a node in an abstract syntax tree (AST) that contains a lambda.

    @param left the parameter of the lambda
    @param right the body of the lambda
    """
    left: NameNode
    right: AbstractNode

    def __repr__(self) -> str:
        return f"λ({self.left}): {self.right}"

    def visit(self, visitor: ""):
        return visitor.visit_function(self)


@dataclass
class EnvNode(AbstractNode):
    """
    Represents a node in an abstract syntax tree (AST) that contains an environment.

    @param elements the elements of the environment
    """
    elements: Dict[str, AbstractNode]

    def __repr__(self) -> str:
        return "[" + ", ".join(map(lambda i: f"{i[0]}={i[1]}", self.elements.items())) + "]"

    def visit(self, visitor: ""):
        return visitor.visit_env(self)


@dataclass
class ApplyNode(AbstractNode):
    """
    Represents a node in an abstract syntax tree (AST) that contains an application.

    @param left the left side of the application
    @param right the right side of the application
    """
    left: AbstractNode
    right: AbstractNode

    def __repr__(self) -> str:
        return f"({self.left} {self.right})"

    def visit(self, visitor: ""):
        return visitor.visit_apply(self)