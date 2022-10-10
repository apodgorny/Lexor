
class UnexpectedTokenException(Exception):
    def __init__(self, path, expected_list, found_char):
        self.path = ' =>\n'.join(path)
        self.expected = expected_list
        self.found = found_char

    def __str__(self):
        return f'ERROR: Unexpected token\n{self.path}\nUnexpected token "{self.found}"'


class CyclicRecursionException(Exception):
    def __init__(self, path):
        self.path = ' =>\n'.join(path)

    def __str__(self):
        return f'ERROR: Cyclic recursion\n{self.path}\n'
