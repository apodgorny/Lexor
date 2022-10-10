class Postfix:
    PRIORITY = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    OPERATORS = set(['+', '-', '*', '/', '(', ')', '^'])

    def __init__(self):
        self.buffer = []
        self.stack = []

    def insert(self, exp):
        if exp == 'EOF':
            while self.stack:
                self.buffer.append(self.stack.pop())
        elif exp not in self.OPERATORS:
            self.buffer.append(exp)
        elif exp == '(':
            self.stack.append('(')
        elif exp == ')':
            while self.stack and self.stack[-1] != '(':
                self.buffer.append(self.stack.pop())
            self.stack.pop()
        else:
            while self.stack and self.stack[-1] != '('\
                    and self.PRIORITY[exp] <= self.PRIORITY[self.stack[-1]]:
                self.buffer.append(self.stack.pop())
            self.stack.append(exp)

    def _format(self, x):
        if isinstance(x, str):
            return x
        elif x % 1 == 0:
            return str(int(x))
        else:
            return str(x)

    def __str__(self):
        s = ','.join([self._format(x) for x in self.buffer])
        return f'[{s}]'

    def get(self):
        return self.buffer