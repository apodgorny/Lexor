from library.Tree import Node, Tree

class TokenNode(Node):
    def __init__(self, name, call):
        super().__init__(name)
        self.call = call

class TokenTree(Tree):
    def __init__(self, root_value):
        super().__init__()
        self.root = TokenNode(root_value)