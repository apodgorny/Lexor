class CodePoint:
    MAX_EXCERPT_LENGTH = 20

    def __init__(self, code, token=None):
        self.code  = code
        self.n     = code.n
        self.c     = code.c
        self.col   = code.col
        self.row   = code.row
        self.token = token
        self._line = None

    def unwind(self):
        self.code.n   = self.n
        self.code.col = self.col
        self.code.row = self.row

    @property
    def line(self):
        if self._line is None:
            self._line = self.code.line_at(self.n)
        return self._line

    @property
    def at(self):
        return f'{self.row}:{self.col}'

    @property
    def excerpt(self):
        length = min(self.col, self.MAX_EXCERPT_LENGTH)
        start = self.col - length
        end = self.MAX_EXCERPT_LENGTH - start
        half = self.line[start : self.col + 1]
        excerpt = self.line[start : end]
        pointer = '^'.rjust(len(half) + 1, '_')
        return f'{self.at}:\n"{excerpt}"\n{pointer}'

    def __str__(self):
        return f'CodePoint({self.at})'


