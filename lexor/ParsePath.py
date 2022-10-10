from functools import wraps
import types

class ParsePath:
    instance = None
    def __init__(self):
        self.path = []
        self.is_augmented = False

    def push(self, name):
        self.path.append(name)

    def pop(self):
        self.path.pop()

    def augment(self, lexor):
        if not self.is_augmented:
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
            path.push(name)
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
            # print(f'\t\tbefore {name}', self.n)
            return_value = f(self, name, *args)
            # print(f'\t\tafter {name}', self.n)
            if not return_value:
                if self.n != mark:
                    s_before = self.s[self.n] + f' ({self.n})'
                    self.n = mark
                    s_after = self.s[self.n] + f' ({self.n})'
                    print(s_before, f'--- unwind {name}---', s_after)
            return return_value
        return wrapper