from lexor.LexorSynthax import LexorSynthax
from lexor.ParsePath import ParsePath

class Unexpected(Exception):
    def __init__(self, path, expected_list, found_char):
        self.path = ' =>\n'.join(path)
        self.expected = expected_list
        self.found = found_char

    def __str__(self):
        return f'ERROR: Unexpected token\n{self.path}\nexpected {" or ".join(self.expected)}, found "{self.found}"'

class CyclicRecursion(Exception):
    def __init__(self, path):
        self.path = ' =>\n'.join(path)

    def __str__(self):
        return f'ERROR: Cyclic recursion\n{self.path}\n'


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

    @ParsePath.collect
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
            print(s)

        return s

    def _get_and_phrase(self, phrase, required):
        all_words = []
        got_all = True
        for name in phrase['and']:
            self._get_spaces(phrase['space'])
            if self._is_phrase(name):                           # phrase
                words = self._get_phrase(name, True)
                if words:
                    all_words += words
                else:
                    got_all = False
                    break
            else:                                               # word
                word = self._get_word(name)
                if word:
                    all_words.append(word)
                else:
                    got_all = False
                    break

        if not got_all:
            if required:
                self.error_unexpected([name])
            else:
                all_words = None

        return all_words

    def _get_or_phrase(self, phrase, required):
        words = []
        got_any = False
        for name in phrase['or']:
            self._get_spaces(phrase['space'])
            if self._is_phrase(name):                           # phrase
                new_words = self._get_phrase(name, False)
                if new_words:
                    got_any = True
                    words += new_words
                    break
            else:                                               # word
                word = self._get_word(name)
                if word:
                    words.append(word)
                    got_any = True
                    break

        if not got_any:
            if required:
                self.error_unexpected(phrase['or'])
            else:
                words = None

        return words

    def _get_orplus_phrase(self, phrase, required):
        words = []
        got_any = False
        for name in phrase['or+']:
            self._get_spaces(phrase['space'])
            if self._is_phrase(name):                           # phrase
                new_words = self._get_phrase(name, False)
                if new_words:
                    got_any = True
                    words += new_words
            else:                                               # word
                word = self._get_word(name)
                if word:
                    words.append(word)
                    got_any = True

        if not got_any:
            if required:
                self.error_unexpected(phrase['or+'])
            else:
                words = None

        return words


    @ParsePath.collect
    @ParsePath.mark_unwind
    def _get_phrase(self, name, required):
        # if self.last_phrase == name:
        #     raise CyclicRecursion(self.path.path)
        #     return None

        if self.eof:
            print('EOF')
            return

        if not self.last_phrase:
            self.last_phrase = name

        phrase = self.synthax['PHRASES'][name]
        words = []

        self.log(f'[ {name} {"*" if required else ""}')

        if   'and' in phrase : words = self._get_and_phrase(phrase, required)
        elif 'or'  in phrase : words = self._get_or_phrase(phrase, required)
        elif 'or+' in phrase : words = self._get_orplus_phrase(phrase, required)

        if words : self.log(f'] {name} => ({" ".join(words)})')
        else     : self.log(f'] {name} => NONE')

        return words

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
            self._get_phrase(self.config['main'], True)
        except Unexpected as e:
            exception = e
        except CyclicRecursion as e:
            exception = e

        print('=' * 30 + '\n')
        print(exception)
        print('=' * 30)





