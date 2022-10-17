
class UnexpectedTokenException(Exception):
    def __init__(self, code_point):
        self.cp = code_point

    def __str__(self):
        return f'ERROR: Unexpected token "{self.cp.c}" at {self.cp.excerpt}\n'


class CyclicRecursionException(Exception):
    def __init__(self, path):
        self.path = ' =>\n'.join(path)

    def __str__(self):
        return f'ERROR: Cyclic recursion\n{self.path}\n'
