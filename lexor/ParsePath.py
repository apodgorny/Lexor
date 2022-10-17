from functools import wraps
import types
import math

from lexor.RecursionDetector import RecursionDetector
from lexor.CodePoint import CodePoint
from lexor.Exceptions import (
    CyclicRecursionException,
    UnexpectedTokenException
)


class ParsePath:
    instance = None
    def __init__(self):
        self.path = []
        self.full_path = []
        self.lexor = None
        self.is_augmented = False
        self.recursion_detector = RecursionDetector(3)

    def push(self, token):
        detected = self.recursion_detector.detect(self.full_path, token)
        self.path.append(CodePoint(self.lexor.code, token))
        self.full_path.append(token)
        if detected:
            # with open ('fragment.txt', 'a') as f: f.write (f'{self.recursion_detector.fragment}\n')
            raise UnexpectedTokenException(self.lexor.code.max)
            # raise CyclicRecursionException(self.path)

    def pop(self, result):
        code_point = self.path.pop()
        if not result:
            self.lexor.code.unwind(code_point)

    def augment(self, lexor):
        if not self.is_augmented:
            self.lexor = lexor
            parse_path = self
            def lexor_log(self, *args):
                if self.verbose:
                    level = len(parse_path.path)
                    indent = ' │\t' * (level-1)
                    value = self.code.at()
                    print(value.ljust(15, ' '), indent, *args)

            lexor.log = types.MethodType(lexor_log, lexor)
            setattr(lexor, 'path', parse_path)
            self.is_augmented = True

    @staticmethod
    def get_instance():
        if not ParsePath.instance:
            ParsePath.instance = ParsePath()
        return ParsePath.instance

    @staticmethod
    def control(f):
        path = ParsePath.get_instance()
        @wraps(f)
        def wrapper(self, name):
            path.augment(self)
            path.push(f'{name} {self.code.n}')
            return_value = f(self, name)
            path.pop(return_value)
            return return_value
        return wrapper
