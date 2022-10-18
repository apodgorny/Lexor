from os.path import exists
from lexor import Lexor
import importlib

language = 'calculator'
executor = None

try:
    Executor = importlib.import_module(f'languages.{language}.Executor').Executor
    executor = Executor(f'languages/{language}/')
except Exception as e:
    print('Warning:', e)

with open(f'languages/{language}/code.txt') as file:
    code = file.read()

lexor = Lexor(f'languages/{language}/syntax.json')
lexor.run(code, executor)


