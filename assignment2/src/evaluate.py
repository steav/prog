from enum import Enum, auto
from typing import MutableSet, Union

from .nodes import *
from .nodes import AbstractNode, NameNode, IntegerNode, AssignNode, ApplyNode, EnvNode, \
    FunctionNode


"""
Type of a predefined node.
"""
class Type(Enum):
    """
    Addition.
    """
    add = auto()
    """
    Subtraction.
    """
    minus = auto()
    """
    Multiplication.
    """
    mult = auto()
    """
    Division.
    """
    div = auto()
    """
    Conditional.
    """
    cond = auto()

    def __str__(self) -> str:
        """
        @return the string representation of the type
        """
        return self.name

"""
Abstract base class for all node visitors.

A node visitor is an object that visits each node in an abstract syntax tree (AST) and
performs some computation on each node. Node visitors are used to implement various
tree traversals, such as evaluating an expression or replacing a variable with a value.
"""
class AbstractNodeVisitor(ABC):

    @abstractmethod
    def visit_assignment(self, node: AssignNode):
        pass

    @abstractmethod
    def visit_apply(self, node: ApplyNode):
        pass

    @abstractmethod
    def visit_predefined(self, node):
        pass

    @abstractmethod
    def visit_env(self, node: EnvNode):
        pass

    @abstractmethod
    def visit_function(self, node: FunctionNode):
        pass

    @abstractmethod
    def visit_integer(self, node: IntegerNode):
        pass

    @abstractmethod
    def visit_name(self, node: NameNode):
        pass



"""
Predefined node in an abstract syntax tree (AST).

Predefined nodes are nodes that are pre-defined by the language and are not created
by the user. Examples of predefined nodes include the "+", "-", "*", "/" and "cond"
nodes.
"""
class PredefinedNode(AbstractNode):
    """
    A predefined node in an abstract syntax tree (AST).

    A predefined node is a node that is pre-defined by the language and is not created
    by the user. Examples of predefined nodes include the "+", "-", "*", "/" and "cond"
    nodes.

    @param builtin_type a Type object representing the type of the node
    """
    def __init__(self, builtin_type: Type):
        self.type = builtin_type
        self.max_children = 3 if builtin_type == Type.cond else 2
        self.children = list()
        self.env = None

    """
    @return the string representation of the node
    """
    def __repr__(self) -> str:
        children = ", ".join([f"{c}" for c in self.children])
        return f"({str(self.type)} {children})"

    """
    Evaluates the node by performing the respective integer operation on the two children of the node.

    @param type a Type object representing the type of the node
    @param a the first child of the node
    @param b the second child of the node
    @return the result of the operation
    """
    def eval_integer_operation(self, type: Type, a: IntegerNode, b: IntegerNode) -> IntegerNode:
        a = a.value
        b = b.value
        if type == Type.add:
            res = a + b
        elif type == Type.minus:
            res = a - b
        elif type == Type.mult:
            res = a * b
        elif type == Type.div:
            res = a / b
        else:
            raise Exception(f"Unsupported integer operand: {type}")
        return IntegerNode(res)

    """
    @param visitor a visitor that will be used to visit the node
    @return the result of visiting the node
    """
    def visit(self, visitor: AbstractNodeVisitor):
        return visitor.visit_predefined(self)

    """
    @return true if the node can be applied and false otherwise
    """
    def is_applyable(self) -> bool:
        return len(list(self.children)) < self.max_children

    """
    Applies the node to the given node.

    @param node the node to apply to
    """
    def apply(self, node: AbstractNode):
        if not isinstance(node, AbstractNode):
            raise TypeError("Unexpected error: expected AbstractNode")

        if len(list(self.children)) == self.max_children:
            raise Exception("Unexpected error: already applied")
        self.children.append(node)


class Environment:
    """
    A mapping from names to nodes.

    This class represents a mapping from names to nodes. It is used to
    represent the environment in which a program is evaluated.

    @param parent the parent environment
    """
    parent: ["Environment"]
    entries: Dict[str, AbstractNode]

    def __init__(self, parent: "Environment" = None) -> None:
        """
        Initializes this environment with the given parent environment.
        """
        self.parent = parent
        self.entries = dict()

        self.define(str(Type.add), PredefinedNode(Type.add))
        self.define(str(Type.minus), PredefinedNode(Type.minus))
        self.define(str(Type.mult), PredefinedNode(Type.mult))
        self.define(str(Type.div), PredefinedNode(Type.div))
        self.define(str(Type.cond), PredefinedNode(Type.cond))

    def __repr__(self) -> str:
        """
        @return a string representation of this environment
        """
        parent = str
        if self.parent is not None:
            parent = repr(self.parent) + "\n"
        definitions = ",\n".join([f"{k} = {v}" for k, v in self.entries.items()])
        return parent + "{\n" + definitions + "\n}"

    def define(self, name: str, node: AbstractNode) -> None:
        """
        Defines a new name in this environment.

        @param name the name of the new variable
        @param node the node associated with the new variable
        """
        if name in self.entries:
            raise Exception(f"Redefinition of already defined name: {name}")
        self.entries[name] = node

    def find(self, name: str) -> Union[AbstractNode, None]:
        """
        Finds a node in this environment by name.

        @param name the name of the node to find
        @return the node associated with the given name, or None if no such node exists
        """
        item = self.entries.get(name, None)
        if item is not None:
            return item
        if self.parent is not None:
            return self.parent.find(name)
        return None


class AST(AbstractNodeVisitor):
    """
    Represents an abstract syntax tree (AST) that can be evaluated.

    @param root the root of the AST
    @param env the environment to use during evaluation
    @param bound_variables the set of bound variables in the tree
    @param num_changes the number of changes made during evaluation
    """

    root: AbstractNode
    env: Environment
    bound_variables: MutableSet
    num_changes: int

    def __init__(self, root: AbstractNode, env=None, bound_variables=None):
        """
        Initializes this AST with the given root, environment, and set of bound variables.
        """
        self.env = env or Environment()
        self.root = root
        self.bound_variables = bound_variables or set()
        self.num_changes = 0

    def reduce(self) -> AbstractNode:
        """
        Evaluates this AST.

        @return the result of evaluating this AST
        """
        self.num_changes = 0
        changes = -1
        root = self.root
        while self.num_changes > changes:
            changes = self.num_changes
            root = root.visit(self)
        return root

    def push_env(self, env: EnvNode = None):
        """
        Pushes a new environment onto the stack.

        @param env: the new environment
        """
        self.env = Environment(self.env)
        for k, v in env.elements.items():
            self.env.define(k, v)

    def pop_env(self):
        """
        Pops the current environment off the stack.
        """
        self.env = self.env.parent

    def visit_name(self, node: NameNode):
        """
        Visits a name node.

        @param node: the name node to visit
        @return the result of visiting the node
        """
        # bound variable: ignore
        if node.name in self.bound_variables:
            return node
        # free variable: replace it
        item = self.env.find(node.name)
        if item is None:
            raise Exception(f"Error: {node.name} is not defined")
        self.num_changes += 1
        return AstDeepCopy(item).run()


    def visit_integer(self, node: IntegerNode):
        """
        Visits an integer node.

        @param node: the integer node to visit
        @return the result of visiting the node
        """
        return node

    def visit_assignment(self, node: AssignNode):
        """
        Visits an assignment node.

        @param node: the assignment node to visit
        @return the result of visiting the node
        """
        node.right = node.right.visit(self)
        self.env.define(node.left.name, node.right)
        return node

    def visit_apply(self, node: ApplyNode):
        """
        Visits an apply node.

        @param node: the apply node to visit
        @return the result of visiting the node
        """
        if isinstance(node.left, FunctionNode):
            self.num_changes += 1
            variable_name = node.left.left.name
            lambda_body = node.left.right
            expr = node.right
            return AstDeepReplace(lambda_body, variable_name, expr).run()
        elif isinstance(node.left, PredefinedNode) and node.left.is_applyable():
            self.num_changes += 1
            left = node.left
            left.apply(node.right)
            return left
        elif isinstance(node.left, EnvNode):
            self.push_env(node.left)

            if isinstance(node.right, IntegerNode):
                self.pop_env()
                return node.right

            change = self.num_changes
            node.right = node.right.visit(self)
            self.pop_env()

            if change == self.num_changes:
                self.num_changes += 1
                return node.right

            return node
        elif isinstance(node.left, NameNode):
            node.left = self.visit_name(node.left)
            return node
        elif isinstance(node.left, ApplyNode):
            node.left = self.visit_apply(node.left)
            return node
        elif isinstance(node.left, PredefinedNode) and node.left.type is Type.cond:
            node.left = node.left.visit(self)
            return node
        else:
            raise Exception(f"Invalid syntax, unexpected: {node.right}")

    def visit_env(self, node: EnvNode):
        """
        Visits an environment node.

        @param node: the environment node to visit
        @return the result of visiting the node
        """
        return node

    def visit_function(self, node: FunctionNode):
        """
        Visits a function node.

        @param node: the function node to visit
        @return the result of visiting the node
        """
        if node.left.name not in self.bound_variables:
            self.bound_variables.add(node.left.name)
            node.right = node.right.visit(self)
            self.bound_variables.remove(node.left.name)
        else:
            node.right = node.right.visit(self)
        return node

    def visit_predefined(self, node: PredefinedNode):
        """
        Visits a predefined node.

        @param node: the predefined node to visit
        @return the result of visiting the node
        """
        if node.type is Type.cond:
            children = list(node.children)
            if len(children) == 3:
                cond = children[0]
                if isinstance(cond, IntegerNode):
                    self.num_changes += 1
                    if cond.value != 0:
                        return children[1]
                    else:
                        return children[2]
                if isinstance(cond, EnvNode):
                    self.num_changes += 1
                    if len(cond.elements) != 0:
                        return children[1]
                    else:
                        return children[2]

                children[0] = cond.visit(self)
                node.children = children
            node.env = self.env

        elif not node.is_applyable() and isinstance(node.children[0], IntegerNode) and isinstance(node.children[1],
                                                                                                  IntegerNode):
            self.num_changes += 1
            return node.eval_integer_operation(node.type, node.children[0], node.children[1])

        node.children = list(map(lambda x: x.visit(self), node.children))
        return node


class AstDeepReplace(AbstractNodeVisitor):
    """
    Replaces a variable in an abstract syntax tree (AST) with an expression.

    @param root the root of the AST
    @param variable_name the name of the variable to replace
    @param expr the expression to replace the variable with
    """
    root: AbstractNode
    variable_name: str
    expr: AbstractNode

    def __init__(self, root: AbstractNode, variable_name: str, expr: AbstractNode) -> None:
        """
        @param root the root of the AST
        @param variable_name the name of the variable to replace
        @param expr the expression to replace the variable with
        """
        self.root = root
        self.variable_name = variable_name
        self.expr = expr

    def run(self) -> AbstractNode:
        """
        @return the modified AST
        """
        return self.root.visit(self)

    def visit_name(self, node: NameNode):
        """
        @param node the name node to visit
        @return the replaced name node
        """
        if node.name == self.variable_name:
            return AstDeepCopy(self.expr).run()
        return node

    def visit_integer(self, node: IntegerNode):
        """
        @param node the integer node to visit
        @return the same integer node
        """
        return node

    def visit_assignment(self, node: AssignNode):
        """
        @param node the assignment node to visit
        @return the modified assignment node with the right side replaced
        """
        node.right = node.right.visit(self)
        return node

    def visit_apply(self, node: ApplyNode):
        """
        @param node the apply node to visit
        @return the modified apply node with the left and right sides replaced
        """
        node.left = node.left.visit(self)
        node.right = node.right.visit(self)
        return node

    def visit_env(self, node: EnvNode):
        """
        @param node the env node to visit
        @return the modified env node with the elements replaced
        """
        node.elements = {k: v.visit(self) for k, v in node.elements.items()}
        return node

    def visit_function(self, node: FunctionNode):
        """
        @param node the function node to visit
        @return the modified function node with the right side replaced
        """
        if node.left.name == self.variable_name:
            return node
        node.right = node.right.visit(self)
        return node

    def visit_predefined(self, node: PredefinedNode):
        """
        @param node the predefined node to visit
        @return the modified predefined node with the children replaced
        """
        node.children = list(map(lambda n: n.visit(self), node.children))
        return node


class AstDeepCopy(AbstractNodeVisitor):
    """
    Copies an abstract syntax tree (AST) recursively.
    """
    root: AbstractNode

    def __init__(self, node: AbstractNode):
        """
        Initializes this node copier with the given node.

        :param node: the node to copy
        """
        self.root = node

    def run(self) -> AbstractNode:
        """
        @return the copied node
        """
        return self.root.visit(self)

    def visit_name(self, node: NameNode):
        """
        Copies a name node.

        @param node the node to copy
        @return the copied node
        """
        return node

    def visit_integer(self, node: IntegerNode):
        """
        Copies an integer node.

        @param node the node to copy
        @return the copied node
        """
        return node

    def visit_assignment(self, node: AssignNode):
        """
        Copies an assignment node.

        @param node the node to copy
        @return the copied node
        """
        return AssignNode(node.left, node.right.visit(self))

    def visit_apply(self, node: ApplyNode):
        """
        Copies an application node.

        @param node the node to copy
        @return the copied node
        """
        left = node.left.visit(self)
        right = node.right.visit(self)
        return ApplyNode(left, right)

    def visit_env(self, node: EnvNode):
        """
        Copies an environment node.

        @param node the node to copy
        @return the copied node
        """
        symbols = {k: v.visit(self) for k, v in node.elements.items()}
        return EnvNode(symbols)

    def visit_function(self, node: FunctionNode):
        """
        Copies a function node.

        @param node the node to copy
        @return the copied node
        """
        return FunctionNode(node.left, node.right.visit(self))

    def visit_predefined(self, node: PredefinedNode):
        """
        Copies a predefined node.

        @param node the node to copy
        @return the copied node
        """
        new_node = PredefinedNode(node.type)
        new_node.children = list(map(lambda n: n.visit(self), node.children))
        return new_node
