from library.Tree import Node, Tree

class TokenNode(Node):
    def __init__(self, name, call, is_actual_value=False):
        super().__init__(name)
        self.call   = call
        self.is_actual = is_actual_value

    def expression_view(self, parenthesize_children=False):
        value = ''
        if len(self.children) > 0:
            child_values = []
            for child in self.children:
                child_values.append(child.expression_view(parenthesize_children))
                value = f"{' '.join(child_values)}"
                if parenthesize_children and len(child_values) > 1:
                    value = f"({value})"
        else:
            value = self.value
        return value

class TokenTree(Tree):
    def __init__(self, root_value):
        super().__init__()
        self.root = TokenNode(root_value)
