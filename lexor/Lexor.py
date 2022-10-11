from lexor.LexorSynthax import LexorSynthax
from lexor.ParsePath import ParsePath
from lexor.Exceptions import (
    CyclicRecursionException,
    UnexpectedTokenException
)
from library.TokenTree import TokenNode, TokenTree

class Lexor:
    SPACES = [' ', '\n', '\t', '\r']

    def __init__(self, synthax_file_name):
        data = LexorSynthax.get_synthax(synthax_file_name)

        self.config  = data['CONFIG']
        self.synthax = data['SYNTHAX']

        self.s           = None
        self.n           = None
        self.words       = None
        self.last_phrase = None
        self.eof         = False
        self.path        = None
        self.log         = None

    def error_unexpected(self, expected_list):
        # raise Unexpected(self.path.path, expected_list, self.s[self.n])
        pass

    def path_push(self, s):
        self.path.append(s)

    def path_pop(self):
        self.path.pop()

    def _get_spaces(self, allow=False):
        if allow:
            while self.s[self.n] in self.SPACES:
                if self.n >= len(self.s) - 2:
                    self.eof = True
                    return
                self.n += 1

    def _is_phrase(self, name) : return name in self.synthax['PHRASES']
    def _is_word(self, name)   : return name in self.synthax['WORDS']

    def _get_letters(self, name, max_length):
        letters = self.synthax['LETTERS'][name]
        s = ''
        for n in range(max_length):
            if self.s[self.n] in letters:
                s += self.s[self.n]
                self.log( f'{name} {self.s[self.n]} => ({s})')
                self.last_phrase = None
                if self.n >= len(self.s) - 2:
                    self.eof = True
                    return s or None
                self.n += 1
            else:
                self.log(f'{name} {self.s[self.n]}')
                break

        return s or None

    @ParsePath.collect
    @ParsePath.mark_unwind
    def _get_syllable(self, name):
        self.log(f'[ {name}')

        syllable = self.synthax['SYLLABLES'][name]
        letters = self._get_letters(syllable['letters'], syllable['max'])

        if letters:
            self.log(f'] {name} => ({letters})')
        else:
            self.log(f'] {name} => None')

        return letters

    @ParsePath.collect
    @ParsePath.mark_unwind
    def _get_word(self, name):
        word = self.synthax['WORDS'][name]
        node = None
        s = ''
        got_all = True
        self.log(f'[ {name}')
        for syllable_name in word['syllables']:
            syllable = self._get_syllable(syllable_name)
            if syllable:
                s += syllable
            else:
                got_all = False
                break

        if not got_all:
            self.log(f'] {name}')
            s = None
        else:
            self.log(f'] {name} => {s}')
            node = TokenNode(s, word['call'])

        return node

    def _get_and_phrase(self, name):
        phrase = self.synthax['PHRASES'][name]
        node = TokenNode(name, phrase['call'])
        got_all = True
        for name in phrase['and']:
            new_node = None
            self._get_spaces(phrase['space'])

            if self._is_phrase(name):                           # phrase
                new_node = self._get_phrase(name)
            else:                                               # word
                new_node = self._get_word(name)

            if new_node:
                if new_node.call:
                    node.append(new_node)
                else:
                    node.children += new_node.children
            else:
                got_all = False
                break

        if not got_all:
            node = None

        return node

    def _get_or_phrase(self, name):
        phrase = self.synthax['PHRASES'][name]
        node = TokenNode(name, phrase['call'])
        got_any = False
        for name in phrase['or']:
            new_node = None
            self._get_spaces(phrase['space'])

            if self._is_phrase(name):                           # phrase
                new_node = self._get_phrase(name)
            else:                                               # word
                new_node = self._get_word(name)

            if new_node:
                if new_node.call:
                    node.append(new_node)
                else:
                    node.children += new_node.children
                got_any = True
                break

        if not got_any:
            node = None

        return node

    def _get_orplus_phrase(self, name):
        phrase = self.synthax['PHRASES'][name]
        node = TokenNode(name, phrase['call'])
        got_any = False
        for name in phrase['or+']:
            new_node = None
            self._get_spaces(phrase['space'])

            if self._is_phrase(name):                           # phrase
                new_node = self._get_phrase(name)
            else:                                               # word
                new_node = self._get_word(name)

            if new_node:
                if new_node.call:
                    node.append(new_node)
                else:
                    node.children += new_node.children

                got_any = True

        if not got_any:
            node = None

        return node


    @ParsePath.collect
    @ParsePath.mark_unwind
    def _get_phrase(self, name):
        if self.eof:
            print('EOF')
            return

        if not self.last_phrase:
            self.last_phrase = name

        phrase = self.synthax['PHRASES'][name]
        node = None

        self.log(f'[ {name}')

        if   'and' in phrase : node = self._get_and_phrase(name)
        elif 'or'  in phrase : node = self._get_or_phrase(name)
        elif 'or+' in phrase : node = self._get_orplus_phrase(name)

        if node : self.log(f'] {name} => (some value)')
        else     : self.log(f'] {name} => NONE')

        return node

    def run(self, code: str):
        pre  = self.config["prepend_with"]
        post = self.config["append_with"]

        self.s           = pre + code + post + ' '
        self.n           = 0
        self.words       = []
        self.last_phrase = None
        self.eof         = False

        program = f'{self.config["name"]} (Version {self.config["version"]})'
        line    = '=' * len(program)
        print(line)
        print(program)
        print(line)
        print(self.s)
        print(line)

        exception = ''
        try:
            node = self._get_phrase(self.config['main'])
        except UnexpectedTokenException as e:
            exception = e
        except CyclicRecursionException as e:
            exception = e

        print('=' * 30 + '\n')
        if exception:
            print(exception)
        else:
            print(node)
        print('=' * 30)





