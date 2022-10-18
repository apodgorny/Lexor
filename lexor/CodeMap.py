from lexor.CodePoint import CodePoint

class CodeMap:
    SPACES = ' \n\t\r'
    def __init__(self, code, verbose=True):
        self.s       = code
        self.n       = 0
        self.col     = 0
        self.row     = 0
        self.eof     = False
        self.max     = None
        self.verbose = verbose

    @property
    def c(self):
        return self.s[self.n]

    def advance(self):
        if self.n >= len(self.s) - 1:
            self.eof = True
        else:
            if self.c == '\n':
                self.col = 0
                self.row += 1
            else:
                self.col  += 1
            self.n += 1

    def at(self):
        max_len = 10
        line = self.line_at(self.n)
        length = min(self.col, max_len)
        return line[self.col - length : self.col]

    def mark(self):
        return CodePoint(self)

    def unwind(self, code_point):
        if self.n > code_point.n:
            start = self.n - 10 if len(self.s) >= 10 else 0
            s_before = '"' + self.s[start:self.n] + f'" ({self.n})'

        if self.max is None or self.max.n < self.n:
            self.max = CodePoint(self)

        code_point.unwind()

        if self.n > code_point.n:
            start = self.n - 10 if len(self.s) >= 10 else 0
            s_after = '"' + self.s[start:self.n] + f'" ({self.n})'
            if self.verbose: print(s_before, f'--> unwind {code_point.token}-->', s_after)

    def skip(self, chars=SPACES):
        while self.s[self.n] in chars:
            self.advance()

    def line_at(self, n):
        i = n
        line = ''
        while i >= 0 and self.s[i] != '\n':
            line = self.s[i] + line
            i -= 1
        i = n + 1
        while i < len(self.s) and self.s[i] != '\n':
            line += self.s[i]
            i += 1
        return line