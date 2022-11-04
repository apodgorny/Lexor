import json
import os

class SyntaxError(Exception):  ...
class IntegrityError(Exception):  ...


class LexorSyntax:

    @staticmethod
    def _load(file_name):
        with open(file_name) as f:
            return json.load(f)

    @staticmethod
    def _assert_keys(dict_name, dict, keys):
        for key in keys:
            if not key in dict:
                raise SyntaxError(f'No "{key}" section present in {dict_name}')

    @staticmethod
    def _assert_sections(data):
        LexorSyntax._assert_keys('syntax file', data, [
            'CONFIG', 'SYNTAX'
        ])
        LexorSyntax._assert_keys('CONFIG section', data['CONFIG'], [
            'main', 'name', 'version', 'prepend_with', 'append_with'
        ])
        LexorSyntax._assert_keys('SYNTAX section', data['SYNTAX'], [
            'PHRASES', 'WORDS', 'SYLLABLES', 'LETTERS'
        ])

    @staticmethod
    def _process_comments(data):
        has_comments = False
        if isinstance(data, dict):
            for name in data:
                if name == '@COMMENT':
                    has_comments = True
                else:
                    LexorSyntax._process_comments(data[name])
        if has_comments:
            del data['@COMMENT']

    @staticmethod
    def _process_imports(syntax, import_path):
        for name in syntax:
            section = syntax[name]
            if '@IMPORT' in section:
                paths = section['@IMPORT']
                for path in paths:
                    path = os.path.join(import_path, path)
                    data = LexorSyntax._load(path)
                    section.update(data)
                del section['@IMPORT']

    @staticmethod
    def _assert_phrases_syntax(phrases):
        for name, phrase in phrases.items():
            if not name.startswith('P_'):
                raise SyntaxError(f'Phrase names must start with "P_" in phrase "{name}"')
            if not 'space' in phrase:
                phrase['space'] = True
            if not isinstance(phrase['space'], bool):
                raise SyntaxError(f'Attribute "space" must be boolean in phrase "{name}"')
            if not 'call' in phrase:
                phrase['call'] = False

            selector_phrase_count = 0
            if 'or'       in phrase: selector_phrase_count += 1
            if 'and'      in phrase: selector_phrase_count += 1
            if 'or+'      in phrase: selector_phrase_count += 1
            if 'sequence' in phrase: selector_phrase_count += 1

            if selector_phrase_count == 0:
                raise SyntaxError(f'Phrase must specify one of [and, or, or+, sequence] attributes in phrase "{name}"')
            if selector_phrase_count > 1:
                raise SyntaxError(f'Phrase can not contain more than one of [and, or, or+] attributes in phrase "{name}"')
            if ('or' in phrase and not isinstance(phrase['or'], list)) or \
                    ('and' in phrase and not isinstance(phrase['and'], list)):
                raise SyntaxError(f'Attributes "and", "or" must be arrays in phrase "{name}')
            if 'or+' in phrase and 'max' not in phrase:
                raise SyntaxError(f'Phrases with attribute "or+" must specify "max" in phrase "{name}"')

    @staticmethod
    def _assert_words_syntax(words):
        for name, word in words.items():
            if not name.startswith('W_'):
                raise SyntaxError(f'Word names must start with "W_" in word "{name}"')
            if not 'syllables' in word:
                raise SyntaxError(f'Word must specify "syllables": [] in word "{name}"')
            if not isinstance(word['syllables'], list):
                raise SyntaxError(f'Attribute "syllables" must be an array in word "{name}')
            if not 'call' in word:
                word['call'] = False

    @staticmethod
    def _assert_syllables_syntax(syllables):
        for name, syllable in syllables.items():
            if not name.startswith('S_'):
                raise SyntaxError(f'Syllable names must start with "S_" in syllable "{name}"')
            if not 'letters' in syllable:
                raise SyntaxError(f'Word must specify "letters": [] in syllable "{name}"')
            if not isinstance(syllable['letters'], str):
                raise SyntaxError(f'Attribute "letters" must be array in syllable "{name}')
            if not 'max' in syllable:
                raise SyntaxError(f'Word must specify "max": <int> in syllable "{name}"')
            if not isinstance(syllable['max'], int):
                raise SyntaxError(f'Attribute "max" must be an integer in syllable "{name}')
            if not 'inverse' in syllable:
                syllable['inverse'] = False
            if not isinstance(syllable['inverse'], bool):
                raise SyntaxError(f'Attribute "inverse" must be a bool in syllable "{name}')

    @staticmethod
    def _assert_letters_syntax(letters):
        for name, letter in letters.items():
            if not name.startswith('L_'):
                raise SyntaxError(f'Letters names must start with "L_" in letters "{name}"')
            if not isinstance(letter, str):
                raise SyntaxError(f'Letters" must be string in "{name}')

    @staticmethod
    def _assert_integrity(syn):
        phrases = syn['PHRASES']
        words = syn['WORDS']
        syllables = syn['SYLLABLES']
        letters = syn['LETTERS']

        for name, phrase in phrases.items():
            keyname = (
                'and' if 'and' in phrase else
                'or'  if 'or'  in phrase else
                'or+' if 'or+' in phrase else
                'sequence' if 'sequence' in phrase else None
            )
            for ref in phrase[keyname]:
                if ref not in phrases and ref not in words:
                    raise IntegrityError(f'{ref} is not resolvable in PHRASES or WORDS')

        for name, word in words.items():
            for ref in word['syllables']:
                if ref not in syllables.keys():
                    raise IntegrityError(f'{ref} is not resolvable in SYLLABLES')

        for name, syllable in syllables.items():
            if syllable['letters'] not in letters.keys():
                raise IntegrityError(f'{ref} is not resolvable in LETTERS')

    @staticmethod
    def get_syntax(syntax_file_name):
        import_path = os.path.dirname(syntax_file_name)
        data = LexorSyntax._load(syntax_file_name)

        try:
            LexorSyntax._assert_sections(data)
            syn = data['SYNTAX']
            LexorSyntax._process_imports(syn, import_path)
            LexorSyntax._process_comments(data)
            LexorSyntax._assert_phrases_syntax(syn['PHRASES'])
            LexorSyntax._assert_words_syntax(syn['WORDS'])
            LexorSyntax._assert_syllables_syntax(syn['SYLLABLES'])
            LexorSyntax._assert_letters_syntax(syn['LETTERS'])
            LexorSyntax._assert_integrity(syn)
        except SyntaxError as e:
            print(f'Synthax error in "{syntax_file_name}": {str(e)}')
            exit(1)
        except IntegrityError as e:
            print(f'Integrity error in "{syntax_file_name}": {str(e)}')
            exit(2)

        return data

