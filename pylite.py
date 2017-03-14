import operator
from argparse import ArgumentParser
from ast import parse, NodeVisitor
from random import randrange
from os.path import exists as file_exists

# see https://docs.python.org/dev/library/ast.html#abstract-grammar

class PyliteInterpreter(NodeVisitor):
    BUILTINS = {
        'print':print
    }
    def __init__(self):
        super().__init__()
        self.last_value = None
        self.env = {}
    def visit_Call(self, node):
        function = node.func.id
        if function in PyliteInterpreter.BUILTINS:
            args = [self.visit(arg) for arg in node.args]
            return PyliteInterpreter.BUILTINS[function](*args)
        elif function in self.env:
            args = [self.visit(arg) for arg in node.args]
            return self.env[function](*args)
        else:
            raise NameError('Undefined function `{}`'.format(function))
    def visit_Name(self, node):
        name = node.id
        if name in self.env:
            return self.env[name]
        raise NameError('Undefined variable `{}`'.format(name))
    def visit_Assign(self, node):
        self.env[node.targets[0].id] = self.visit(node.value)
    def visit_BinOp(self, node):
        args = [self.visit(node.left), self.visit(node.right)]
        op = self.visit(node.op)
        return op(*args)
    def visit_Add(self, node):
        return operator.add
    def visit_Sub(self, node):
        return operator.sub
    def visit_Mult(self, node):
        return operator.mul
    def visit_Div(self, node):
        return operator.truediv
    def visit_FloorDiv(self, node):
        return operator.floordiv
    def visit_Mod(self, node):
        return operator.mod
    def visit_Pow(self, node):
        return operator.pow
    def visit_Str(self, node):
        return node.s
    def visit_Num(self, node):
        return node.n
    @staticmethod
    def run(code):
        PyliteInterpreter().visit(parse(code))

class StochasticPyliteInterpreter(PyliteInterpreter):
    def __init__(self):
        super().__init__()
    def visit_Name(self, node):
        # randomly use the value of a variable or the name as a string
        name = node.id
        if name in self.env:
            random = randrange(2)
            if random == 0:
                return self.env[name]
            elif random == 1:
                return name
        raise NameError('Undefined variable `{}`'.format(name))
    def visit_Mod(self, node):
        random = randrange(2)
        if random == 0:
            return operator.mod
        if random == 1:
            return operator.truediv
    @staticmethod
    def run(code):
        StochasticPyliteInterpreter().visit(parse(code))

class BindingInterpreter(PyliteInterpreter):
    def __init__(self):
        super().__init__()
    def visit_BinOp(self, node):
        # check that this is an Add
        # check that the right child is a Num
        # check that the left child is another BinOp
        # left child of the left child is a Num
        # right child of the left child is a Num
        #       +
        #     /  \
        #    *    4
        #  /  \
        # 2    3
        if (type(node.op).__name__ == 'Add' and
                type(node.right).__name__ == 'Num' and
                type(node.left).__name__ == 'BinOp' and
                type(node.left.op).__name__ == 'Mult' and
                type(node.left.left).__name__ == 'Num' and
                type(node.left.right).__name__ == 'Num'):
            print('first')
            left_left = self.visit(node.left.left)
            left_right = self.visit(node.left.right)
            right = self.visit(node.right)
            return left_left * (left_right + right)

        if (type(node.op).__name__ == 'Add' and
                type(node.left).__name__ == 'Num' and
                type(node.right).__name__ == 'BinOp' and
                type(node.right.op).__name__ == 'Mult' and
                type(node.right.left).__name__ == 'Num' and
                type(node.right.right).__name__ == 'Num'):
            print('second')
            left = self.visit(node.left)
            right_left = self.visit(node.right.left)
            right_right = self.visit(node.right.right)
            return (left + right_left) * right_right


        # (4 / 2 + 1)
        if(type(node.op).__name__ == 'Add' and
           type(node.right).__name__ == 'Num' and
           type(node.left).__name__ == 'BinOp' and
           type(node.left.left).__name__ == 'Num' and
           type(node.left.right).__name__ == 'Num'):
           print('first case division')
           left_left = self.visit(node.left.left)
           right = self.visit(node.right)
           left_right = self.visit(node.left.right)
           return (left_left / (right + left_right))

        else:
            args = [self.visit(node.left), self.visit(node.right)]
            op = self.visit(node.op)
            return op(*args)
    @staticmethod
    def run(code):
        BindingInterpreter().visit(parse(code))

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('line_or_file')
    arg_parser.add_argument('--interp', choices=('correct', 'stochastic', 'binding'))
    args = arg_parser.parse_args()
    if file_exists(args.line_or_file):
        with open(args.line_or_file) as fd:
            code = fd.read()
    else:
        code = args.line_or_file
    if args.interp == 'correct':
        interpreter = PyliteInterpreter
    elif args.interp == 'stochastic':
        interpreter = StochasticPyliteInterpreter
    elif args.interp == 'binding':
        interpreter = BindingInterpreter
    interpreter.run(parse(code))

if __name__ == '__main__':
    main()
