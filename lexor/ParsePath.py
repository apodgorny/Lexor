from functools import wraps
import types

from lexor.CycleDetector import CycleDetector
from lexor.Exceptions import (
    CyclicRecursionException,
    UnexpectedTokenException
)

class ParsePath:
    instance = None
    def __init__(self):
        self.path = []
        self.lexor = None
        self.is_augmented = False
        self.cycle_detector = CycleDetector()
        self.max_n = 0

    def push(self, name):
        detected = self.cycle_detector.detect(self.path, name)
        self.path.append(name)
        if detected:
            raise UnexpectedTokenException(self.path, [], self.lexor.s[self.max_n])
            # raise CyclicRecursionException(self.path)

    def pop(self):
        self.path.pop()

    def augment(self, lexor):
        if not self.is_augmented:
            self.lexor = lexor
            parse_path = self
            def lexor_log(self, *args):
                level = len(parse_path.path)
                indent = '\t' * (level-1)
                indent += ' ' * (level-1)
                print(indent, *args)

            lexor.log = types.MethodType(lexor_log, lexor)
            setattr(lexor, 'path', parse_path)
            self.is_augmented = True

    @staticmethod
    def get_instance():
        if not ParsePath.instance:
            ParsePath.instance = ParsePath()
        return ParsePath.instance

    @staticmethod
    def collect(f):
        path = ParsePath.get_instance()
        @wraps(f)
        def wrapper(self, name, *args):
            path.augment(self)
            path.push(f'{name} {self.n}')
            return_value = f(self, name, *args)
            path.pop()
            return return_value
        return wrapper

    @staticmethod
    def mark_unwind(f):
        path = ParsePath.get_instance()
        @wraps(f)
        def wrapper(self, name, *args):
            mark = self.n
            return_value = f(self, name, *args)
            if not return_value:
                if self.n != mark:
                    if path.max_n < self.n:
                        path.max_n = self.n
                    s_before = self.s[self.n] + f' ({self.n})'
                    self.n = mark
                    s_after = self.s[self.n] + f' ({self.n})'
                    print(s_before, f'--- unwind {name}---', s_after)
                    print('\n'.join(path.path))
            return return_value
        return wrapper