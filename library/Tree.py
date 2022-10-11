
class Node:
    CROSS    = ' ├─'
    CORNER   = ' └─'
    VERTICAL = ' │ '
    SPACE    = '   '

    def __init__(self, value=None):
        self.value = value
        self.children = []

    def append(self, node):
        self.children.append(node)

    def _to_string(self, indent='', is_last=True):
        s = indent
        if is_last:
            s += self.CORNER
            indent += self.SPACE
        else:
            s += self.CROSS
            indent += self.VERTICAL

        s += f'({self.value})\n'

        for i in range(len(self.children)):
            is_last_child = i == len(self.children) - 1
            s += self.children[i]._to_string(indent, is_last_child)

        return s

    def __str__(self):
        return self._to_string()


class Tree:
    def __init__(self, value=None):
        self.root = None
        if value is not None:
            self.root = Node(value)

    def __str__(self):
        return str(self.root)