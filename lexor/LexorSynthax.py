import json

class SynthaxError(Exception):  ...
class IntegrityError(Exception):  ...


class LexorSynthax:
    @staticmethod
    def _assert_keys(dict_name, dict, keys):
        for key in keys:
            if not key in dict:
                raise SynthaxError(f'No "{key}" section present in {dict_name}')

    @staticmethod
    def _assert_sections(data):
        LexorSynthax._assert_keys('syntax file', data, [
            'CONFIG', 'SYNTAX'
        ])
        LexorSynthax._assert_keys('CONFIG section', data['CONFIG'], [
            'main', 'name', 'version', 'prepend_with', 'append_with'
        ])
        LexorSynthax._assert_keys('SYNTAX section', data['SYNTAX'], [
            'PHRASES', 'WORDS', 'SYLLABLES', 'LETTERS'
        ])

    @staticmethod
    def _assert_phrases_syntax(phrases):
        for name, phrase in phrases.items():
            if name == 'comment': continue
            if not name.startswith('P_'):
                raise SynthaxError(f'Phrase names must start with "P_" in phrase "{name}"')
            if not 'space' in phrase:
                phrase['space'] = True
            if not isinstance(phrase['space'], bool):
                raise SynthaxError(f'Attribute "space" must be boolean in phrase "{name}"')
            if not 'call' in phrase:
                phrase['call'] = False

            selector_phrase_count = 0
            if 'or' in phrase: selector_phrase_count += 1
            if 'and' in phrase: selector_phrase_count += 1
            if 'or+' in phrase: selector_phrase_count += 1
            if selector_phrase_count == 0:
                raise SynthaxError(f'Phrase must specify one of [and, or, or+] attributes in phrase "{name}"')
            if selector_phrase_count > 1:
                raise SynthaxError(f'Phrase can not contain more than one of [and, or, or+] attributes in phrase "{name}"')
            if ('or' in phrase and not isinstance(phrase['or'], list)) or \
                    ('and' in phrase and not isinstance(phrase['and'], list)):
                raise SynthaxError(f'Attributes "and", "or" must be arrays in phrase "{name}')

    @staticmethod
    def _assert_words_syntax(words):
        for name, word in words.items():
            if name == 'comment': continue
            if not name.startswith('W_'):
                raise SynthaxError(f'Word names must start with "W_" in word "{name}"')
            if not 'syllables' in word:
                raise SynthaxError(f'Word must specify "syllables": [] in word "{name}"')
            if not isinstance(word['syllables'], list):
                raise SynthaxError(f'Attribute "syllables" must be an array in word "{name}')
            if not 'call' in word:
                word['call'] = False

    @staticmethod
    def _assert_syllables_syntax(syllables):
        for name, syllable in syllables.items():
            if name == 'comment': continue
            if not name.startswith('S_'):
                raise SynthaxError(f'Syllable names must start with "S_" in syllable "{name}"')
            if not 'letters' in syllable:
                raise SynthaxError(f'Word must specify "letters": [] in syllable "{name}"')
            if not isinstance(syllable['letters'], str):
                raise SynthaxError(f'Attribute "letters" must be array in syllable "{name}')
            if not 'max' in syllable:
                raise SynthaxError(f'Word must specify "max": <int> in syllable "{name}"')
            if not isinstance(syllable['max'], int):
                raise SynthaxError(f'Attribute "max" must be an integer in syllable "{name}')
            if not 'inverse' in syllable:
                syllable['inverse'] = False
            if not isinstance(syllable['inverse'], bool):
                raise SynthaxError(f'Attribute "inverse" must be a bool in syllable "{name}')

    @staticmethod
    def _assert_letters_syntax(letters):
        for name, letter in letters.items():
            if name == 'comment': continue
            if not name.startswith('L_'):
                raise SynthaxError(f'Letters names must start with "L_" in letters "{name}"')
            if not isinstance(letter, str):
                raise SynthaxError(f'Letters" must be string in "{name}')

    @staticmethod
    def _assert_integrity(syn):
        phrases = syn['PHRASES']
        words = syn['WORDS']
        syllables = syn['SYLLABLES']
        letters = syn['LETTERS']

        for name, phrase in phrases.items():
            if name == 'comment': continue
            keyname = (
                'and' if 'and' in phrase else
                'or'  if 'or'  in phrase else
                'or+'
            )
            for ref in phrase[keyname]:
                if ref not in phrases.keys() and ref not in words.keys():
                    raise IntegrityError(f'{ref} is not resolvable in PHRASES or WORDS')

        for name, word in words.items():
            if name == 'comment': continue
            for ref in word['syllables']:
                if ref not in syllables.keys():
                    raise IntegrityError(f'{ref} is not resolvable in SYLLABLES')

        for name, syllable in syllables.items():
            if name == 'comment': continue
            if syllable['letters'] not in letters.keys():
                raise IntegrityError(f'{ref} is not resolvable in LETTERS')

    @staticmethod
    def get_syntax(syntax_file_name):
        with open(syntax_file_name) as syntax_file:
            data = json.load(syntax_file)

        try:
            syn = data['SYNTAX']
            LexorSynthax._assert_sections(data)
            LexorSynthax._assert_phrases_syntax(syn['PHRASES'])
            LexorSynthax._assert_words_syntax(syn['WORDS'])
            LexorSynthax._assert_syllables_syntax(syn['SYLLABLES'])
            LexorSynthax._assert_letters_syntax(syn['LETTERS'])
            LexorSynthax._assert_integrity(syn)
        except SynthaxError as e:
            print(f'Synthax error in "{syntax_file_name}": {str(e)}')
            exit(1)
        except IntegrityError as e:
            print(f'Integrity error in "{syntax_file_name}": {str(e)}')
            exit(2)

        return data

