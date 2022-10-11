from lexor import Lexor

with open('data/code.txt') as file:
    code = file.read()

lexor = Lexor('data/synthax.json')
lexor.run(code)


