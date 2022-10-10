
class ExpressionNode:
    CROSS    = ' ├─'
    CORNER   = ' └─'
    VERTICAL = ' │ '
    SPACE    = '   '

    def __init__(self, value=None, lchild=None, rchild=None):
        self.value = value
        self.lchild = lchild
        self.rchild = rchild

    def is_operator(self):
        return self.value in ExpressionTree.OPERATORS

    def _to_string(self, indent='', is_last=True):
        s = indent
        if is_last:
            s += self.CORNER
            indent += self.SPACE
        else:
            s += self.CROSS
            indent += self.VERTICAL

        s += f'({self.value})\n'

        if self.lchild:
            s += self.lchild._to_string(indent, False)

        if self.rchild:
            s += self.rchild._to_string(indent, True)

        return s

    def __str__(self):
        return (
            '\nExpression Tree\n' +
            '===============\n' +
            self._to_string()
        )


class ExpressionTree:
    OPERATORS = set(['+', '-', '*', '/', '(', ')', '^'])
    OPERATION = {
        '+': lambda a, b : a + b,
        '-': lambda a, b : a - b,
        '*': lambda a, b : a * b,
        '/': lambda a, b : a / b
    }

    def __init__(self, a):
        # print('a', a)
        self.nodes = []
        self.root = None

        while a:
            m = a.pop()
            if m in self.OPERATORS:
                right = self.nodes.pop()
                left = self.nodes.pop()
                node = ExpressionNode(m, left, right)
                self.nodes.append(node)
            else:
                node = ExpressionNode(m)
                self.nodes.append(node)

        self.root = self.nodes.pop()
        print(self.root)

    def calculate(self, node=None):
        if not node:
            node = self.root

        if node.lchild and node.rchild:
            left = self.calculate(node.lchild)
            right = self.calculate(node.rchild)
            result = self.OPERATION[node.value](left, right)
        else:
            result = node.value

        return result



