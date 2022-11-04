class BaseExecutor:
    def __init__(self, language_path):
        self.language_path = language_path

    def dump_vars(self):
        ...

    def dump_output(self):
        ...

    def execute(self, node):
        if len(node.children) > 0:
            method = getattr(self, node.value.lower())
            params = []
            for child in node.children:
                params.append(self.execute(child))
            return method(*params)
        return node.value