from lexor import Lexor
from execs.B3 import B3

with open('data/code.b3') as file:
    code = file.read()

lexor = Lexor('data/b3.json')
lexor.run(code, B3())


