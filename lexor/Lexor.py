from lexor.LexorSynthax import LexorSynthax
from lexor.ParsePath import ParsePath
from lexor.CodeMap import CodeMap
from lexor.Exceptions import (
    CyclicRecursionException,
    UnexpectedTokenException
)
from library.TokenTree import TokenNode

class Lexor:
    def __init__(self, synthax_file_name):
        data = LexorSynthax.get_synthax(synthax_file_name)

        self.config  = data['CONFIG']
        self.synthax = data['SYNTHAX']

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

    def _is_phrase(self, name) : return name in self.synthax['PHRASES']
    def _is_word(self, name)   : return name in self.synthax['WORDS']

    def _get_letters(self, name, max_length):
        s = ''
        for n in range(max_length):
            c = self.code.c
            if c in self.synthax['LETTERS'][name]:
                s += c
                self.code.advance()
            else:
                break

        return s or None

    @ParsePath.control
    def _get_syllable(self, name):
        syllable = self.synthax['SYLLABLES'][name]
        return self._get_letters(syllable['letters'], syllable['max'])

    @ParsePath.control
    def _get_word(self, name):
        word    = self.synthax['WORDS'][name]
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
        phrase  = self.synthax['PHRASES'][name]
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
        phrase  = self.synthax['PHRASES'][name]
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
        phrase  = self.synthax['PHRASES'][name]
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
        if self.code.eof:
            return

        phrase = self.synthax['PHRASES'][name]
        node   = None

        self.log(f'[ {name}')

        if   'and' in phrase : node = self._get_and_phrase(name)
        elif 'or'  in phrase : node = self._get_or_phrase(name)
        elif 'or+' in phrase : node = self._get_orplus_phrase(name)

        if node : self.log(f'] {name} => ({node.expression_view()})')
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

        print(node)

        if executor and node:
            executor.execute(node)





