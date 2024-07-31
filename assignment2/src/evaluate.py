from enum import Enum, auto
from typing import MutableSet, Union

from .nodes import *
from .nodes import AbstractNode, NameNode, IntegerNode, AssignNode, ApplyNode, EnvNode, \
    FunctionNode


class Type(Enum):
    add = auto()
    minus = auto()
    mult = auto()
    div = auto()
    cond = auto()

    def __str__(self) -> str:
        return self.name


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


class PredefinedNode(AbstractNode):
    def __init__(self, builtin_type: Type):
        self.type = builtin_type
        self.max_children = 3 if builtin_type == Type.cond else 2
        self.children = list()
        self.env = None

    def __repr__(self) -> str:
        children = ", ".join([f"{c}" for c in self.children])
        return f"({str(self.type)} {children})"

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

    def visit(self, visitor: AbstractNodeVisitor):
        return visitor.visit_predefined(self)

    def is_applyable(self) -> bool:
        return len(self.children) < self.max_children

    def apply(self, node: AbstractNode):
        if not isinstance(node, AbstractNode):
            raise TypeError("Unexpected error: expected AbstractNode")

        if len(list(self.children)) == self.max_children:
            raise Exception("Unexpected error: already applied")
        self.children.append(node)


class Environment:
    parent: ["Environment"]
    entries: Dict[str, AbstractNode]

    def __init__(self, parent: "Environment" = None) -> None:
        self.parent = parent
        self.entries = dict()

        self.define(str(Type.add), PredefinedNode(Type.add))
        self.define(str(Type.minus), PredefinedNode(Type.minus))
        self.define(str(Type.mult), PredefinedNode(Type.mult))
        self.define(str(Type.div), PredefinedNode(Type.div))
        self.define(str(Type.cond), PredefinedNode(Type.cond))

    def __repr__(self):
        parent = str
        if self.parent is not None:
            parent = repr(self.parent) + "\n"
        definitions = ",\n".join([f"{k} = {v}" for k, v in self.entries.items()])
        return parent + "{\n" + definitions + "\n}"

    def define(self, name: str, node: AbstractNode):
        if name in self.entries:
            raise Exception(f"Redefinition of already defined name: {name}")
        self.entries[name] = node

    def find(self, name: str) -> Union[AbstractNode, None]:
        item = self.entries.get(name, None)
        if item is not None:
            return item
        if self.parent is not None:
            return self.parent.find(name)
        return None


class AST(AbstractNodeVisitor):
    root: AbstractNode
    env: Environment
    bound_variables: MutableSet
    num_changes: int

    def __init__(self, root: AbstractNode, env=None, bound_variables=None):
        self.env = env or Environment()
        self.root = root
        self.bound_variables = bound_variables or set()
        self.num_changes = 0

    def reduce(self) -> AbstractNode:
        self.num_changes = 0
        changes = -1
        root = self.root
        while self.num_changes > changes:
            changes = self.num_changes
            root = root.visit(self)
        return root

    def push_env(self, env: EnvNode = None):
        self.env = Environment(self.env)
        for k, v in env.elements.items():
            self.env.define(k, v)

    def pop_env(self):
        self.env = self.env.parent

    def visit_name(self, node: NameNode):
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
        return node

    def visit_assignment(self, node: AssignNode):
        node.right = node.right.visit(self)
        self.env.define(node.left.name, node.right)
        return node

    def visit_apply(self, node: ApplyNode):
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
        return node

    def visit_function(self, node: FunctionNode):
        if node.left.name not in self.bound_variables:
            self.bound_variables.add(node.left.name)
            node.right = node.right.visit(self)
            self.bound_variables.remove(node.left.name)
        else:
            node.right = node.right.visit(self)
        return node

    def visit_predefined(self, node: PredefinedNode):
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
    root: AbstractNode
    variable_name: str
    expr: AbstractNode

    def __init__(self, root: AbstractNode, variable_name: str, expr: AbstractNode) -> None:
        self.root = root
        self.variable_name = variable_name
        self.expr = expr

    def run(self) -> AbstractNode:
        return self.root.visit(self)

    def visit_name(self, node: NameNode):
        if node.name == self.variable_name:
            return AstDeepCopy(self.expr).run()
        return node

    def visit_integer(self, node: IntegerNode):
        return node

    def visit_assignment(self, node: AssignNode):
        node.right = node.right.visit(self)
        return node

    def visit_apply(self, node: ApplyNode):
        node.left = node.left.visit(self)
        node.right = node.right.visit(self)
        return node

    def visit_env(self, node: EnvNode):
        node.elements = {k: v.visit(self) for k, v in node.elements.items()}
        return node

    def visit_function(self, node: FunctionNode):
        if node.left.name == self.variable_name:
            return node
        node.right = node.right.visit(self)
        return node

    def visit_predefined(self, node: PredefinedNode):
        node.children = list(map(lambda n: n.visit(self), node.children))
        return node


class AstDeepCopy(AbstractNodeVisitor):
    root: AbstractNode

    def __init__(self, node: AbstractNode):
        self.root = node

    def run(self) -> AbstractNode:
        return self.root.visit(self)

    def visit_name(self, node: NameNode):
        return node

    def visit_integer(self, node: IntegerNode):
        return node

    def visit_assignment(self, node: AssignNode):
        return AssignNode(node.left, node.right.visit(self))

    def visit_apply(self, node: ApplyNode):
        left = node.left.visit(self)
        right = node.right.visit(self)
        return ApplyNode(left, right)

    def visit_env(self, node: EnvNode):
        symbols = {k: v.visit(self) for k, v in node.elements.items()}
        return EnvNode(symbols)

    def visit_function(self, node: FunctionNode):
        return FunctionNode(node.left, node.right.visit(self))

    def visit_predefined(self, node: PredefinedNode):
        new_node = PredefinedNode(node.type)
        new_node.children = list(map(lambda n: n.visit(self), node.children))
        return new_node
