from LexorSynthax import LexorSynthax

class UnexpectedWord(Exception):
    ...

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

    def mark(self):
        # print('mark at', self.n)
        return self.n

    def unwind(self, mark):
        # print(f'unwind from {self.n} to {mark}')
        self.n = mark

    def log(self, level, *args):
        indent = '\t' * (level-1)
        indent += ' ' * (level-1)
        print(indent, *args)

    def _get_spaces(self, allow=False):
        if allow:
            while self.s[self.n] in self.SPACES:
                if self.n >= len(self.s) - 2:
                    self.eof = True
                    return
                self.n += 1

    def _is_phrase(self, name) : return name in self.synthax['PHRASES']
    def _is_word(self, name)   : return name in self.synthax['WORDS']

    def _get_letters(self, letters_name, max_length, level):
        level += 1
        letters =  self.synthax['LETTERS'][letters_name]
        s = ''
        for n in range(max_length):
            if self.s[self.n] in letters:
                s += self.s[self.n]
                self.log(level, f'{letters_name} {self.s[self.n]} => ({s})')
                self.last_phrase = None
                if self.n >= len(self.s) - 2:
                    self.eof = True
                    return s or None
                self.n += 1
            else:
                self.log(level, f'{letters_name} {self.s[self.n]}')
                break

        return s or None

    def _get_syllable(self, syllable_name, level):
        level += 1
        self.log(level, f'[ {syllable_name}')

        syllable = self.synthax['SYLLABLES'][syllable_name]
        letters = self._get_letters(syllable['letters'], syllable['max'], level)

        if letters:
            self.log(level, f'] {syllable_name} => ({letters})')
            # self.log(0, letters)
        else:
            self.log(level, f'] {syllable_name} => None')

        return letters

    def _get_word(self, word_name, level):
        level += 1
        mark = self.mark()
        word = self.synthax['WORDS'][word_name]
        s = ''
        got_all = True
        self.log(level, f'[ {word_name}')
        for name in word['syllables']:
            syllable = self._get_syllable(name, level)
            if syllable:
                s += syllable
            else:
                got_all = False
                break

        if not got_all:
            self.unwind(mark)
            self.log(level, f'] {word_name}')
            s = None
        else:
            self.log(level, f'] {word_name} => {s}')
            self.log(0, s)

        return s

    def _get_and_phrase(self, phrase, required, space, level):
        all_words = []
        got_all = True
        for name in phrase['and']:
            self._get_spaces(space)
            if self._is_phrase(name):                           # phrase
                words = self._get_phrase(name, True, level)
                if words:
                    all_words += words
                else:
                    got_all = False
                    break
            else:                                               # word
                word = self._get_word(name, level)
                if word:
                    all_words.append(word)
                else:
                    got_all = False
                    break

        if not got_all:
            if required:
                raise UnexpectedWord('Unexpected thing in code')
            else:
                all_words = None

        return all_words

    def _get_or_phrase(self, phrase, required, space, level):
        words = []
        got_any = False
        for name in phrase['or']:
            self._get_spaces(space)
            if self._is_phrase(name):                           # phrase
                new_words = self._get_phrase(name, False, level)
                if new_words:
                    got_any = True
                    words += new_words
                    break
            else:                                               # word
                word = self._get_word(name, level)
                if word:
                    words.append(word)
                    got_any = True
                    break

        if not got_any:
            if required:
                raise UnexpectedWord('Unexpected thing in code')
            else:
                words = None

        return words

    def _get_orplus_phrase(self, phrase, required, space, level):
        words = []
        got_any = False
        for name in phrase['or+']:
            self._get_spaces(space)
            if self._is_phrase(name):                           # phrase
                new_words = self._get_phrase(name, False, level)
                if new_words:
                    got_any = True
                    words += new_words
            else:                                               # word
                word = self._get_word(name, level)
                if word:
                    words.append(word)
                    got_any = True

        if not got_any:
            if required:
                raise UnexpectedWord('Unexpected thing in code')
            else:
                words = None

        return words

    def _get_phrase(self, phrase_name, required, level):
        if self.last_phrase == phrase_name:
            raise Exception('Recursion without load! ' + self.last_phrase)
            return None

        if self.eof:
            print('EOF')
            return

        if not self.last_phrase:
            self.last_phrase = phrase_name

        level += 1
        phrase = self.synthax['PHRASES'][phrase_name]
        space  = phrase['space']
        words = []

        self.log(level, f'[ {phrase_name} {"*" if required else ""}')
        if 'and' in phrase:                                     # and
            words = self._get_and_phrase(phrase, required, space, level)
        elif 'or' in phrase:                                                   # or
            words = self._get_or_phrase(phrase, required, space, level)
        else:
            words = self._get_orplus_phrase(phrase, required, space, level)

        if words:
            self.log(level, f'] {phrase_name} => ({" ".join(words)})')
        else:
            self.log(level, f'] {phrase_name} => NONE')

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

        self._get_phrase(self.config['main'], True, 0)





