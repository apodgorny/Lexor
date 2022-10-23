from lexor.LexorSynthax import LexorSynthax
from lexor.ParsePath import ParsePath
from lexor.CodeMap import CodeMap
from lexor.Exceptions import (
    CyclicRecursionException,
    UnexpectedTokenException
)
from library.TokenTree import TokenNode

class Lexor:
    def __init__(self, syntax_file_name):
        data = LexorSynthax.get_syntax(syntax_file_name)

        self.config  = data['CONFIG']
        self.syntax = data['SYNTAX']

        self.path        = None
        self.log         = None
        self.verbose     = True
        self.code        = None

    def log_result(self, exception, node):
        print('=' * 30 + '\n')
        if exception:
            print(exception)
        else:
            print(node)
        print('=' * 30)
    def log_header(self):
        program = f'{self.config["name"]} (Version {self.config["version"]})'
        line    = '=' * len(program)

        print(line)
        print(program)
        print(line)
        print(self.code.s)
        print(line)

    def _get_comments(self):
        self.code.skip()
        sl_begin = self.syntax['COMMENTS']['SL_BEGIN']
        ml_begin = self.syntax['COMMENTS']['ML_BEGIN']
        ml_end   = self.syntax['COMMENTS']['ML_END']
        comment  = ''

        if self.code.peek(sl_begin):
            self.code.advance(len(sl_begin))
            while not self.code.eof:
                if self.code.c != '\n':
                    comment += self.code.c
                    self.code.advance()
                else:
                    self.code.advance()
                    break
        elif self.code.peek(ml_begin):
            self.code.advance(len(ml_begin))
            while not self.code.eof:
                if not self.code.peek(ml_end):
                    comment += self.code.c
                    self.code.advance()
                else:
                    self.code.advance(len(ml_end))
                    break
        comment = comment.strip()
        if comment: print('comment:', comment)
        self.code.skip()
        return comment

    def _is_phrase(self, name) : return name in self.syntax['PHRASES']
    def _is_word(self, name)   : return name in self.syntax['WORDS']

    def _get_letters(self, name, max_length, inverse):
        s = ''
        n = 0
        while not self.code.eof and n < max_length:
            c = self.code.c
            if inverse:
                if c not in self.syntax['LETTERS'][name]:
                    s += c
                    n += 1
                    self.code.advance()
                else:
                    break
            else:
                if c in self.syntax['LETTERS'][name]:
                    s += c
                    n += 1
                    self.code.advance()
                else:
                    break

        return s or None

    @ParsePath.control
    def _get_syllable(self, name):
        syllable = self.syntax['SYLLABLES'][name]
        return self._get_letters(syllable['letters'], syllable['max'], syllable['inverse'])

    @ParsePath.control
    def _get_word(self, name):
        word    = self.syntax['WORDS'][name]
        node    = None
        got_all = True
        s       = ''

        for syllable_name in word['syllables']:
            syllable = self._get_syllable(syllable_name)
            if syllable:
                s += syllable
            else:
                got_all = False
                break

        if got_all:
            node = TokenNode(s, word['call'], True)

        return node

    def _get_and_phrase(self, name):
        phrase  = self.syntax['PHRASES'][name]
        node    = TokenNode(name, phrase['call'])
        got_all = True

        for name in phrase['and']:
            if phrase['space']: self.code.skip()
            if self._is_phrase(name) : new_node = self._get_phrase(name)
            else                     : new_node = self._get_word(name)

            if new_node:
                if new_node.call : node.append(new_node)
                else             : node.children += new_node.children
            else:
                got_all = False
                break

        if not got_all:
            return None
        return node

    def _get_or_phrase(self, name):
        phrase  = self.syntax['PHRASES'][name]
        node    = TokenNode(name, phrase['call'])
        got_any = False

        for name in phrase['or']:
            if phrase['space']: self.code.skip()
            if self._is_phrase(name) : new_node = self._get_phrase(name)
            else                     : new_node = self._get_word(name)

            if new_node:
                if new_node.call : node.append(new_node)
                else             : node.children += new_node.children
                got_any = True
                break

        if not got_any:
            return None
        return node

    def _get_orplus_phrase(self, name):
        phrase  = self.syntax['PHRASES'][name]
        node    = TokenNode(name, phrase['call'])
        got_any = False

        for name in phrase['or+']:
            if phrase['space']: self.code.skip()
            if self._is_phrase(name) : new_node = self._get_phrase(name)
            else                     : new_node = self._get_word(name)

            if new_node:
                if new_node.call : node.append(new_node)
                else             : node.children += new_node.children

                got_any = True

        if not got_any:
            return None
        return node


    @ParsePath.control
    def _get_phrase(self, name):
        self._get_comments()
        phrase = self.syntax['PHRASES'][name]
        node   = None

        if not self.code.eof:
            self.log(f'[ {name}')

            if   'and' in phrase : node = self._get_and_phrase(name)
            elif 'or'  in phrase : node = self._get_or_phrase(name)
            elif 'or+' in phrase : node = self._get_orplus_phrase(name)

            if node : self.log(f'] {name} => ({node.expression_view(True)})')
            else    : self.log(f'] {name} => NONE')

        return node

    def run(self, code: str, executor=None):
        pre  = self.config["prepend_with"]
        post = self.config["append_with"]

        self.code = CodeMap(pre + code + post)
        self.log_header()

        node = None
        exception = None
        try:
            node = self._get_phrase(self.config['main'])
        except UnexpectedTokenException as e:
            exception = e
        except CyclicRecursionException as e:
            exception = e

        self.log_result(exception, node)

        if executor and node:
            executor.execute(node)





